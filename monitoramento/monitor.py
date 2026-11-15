"""
monitor.py — Monitoramento da plataforma AgroSmart (Fase 7).

Três instrumentos, todos em arquivos simples para serem lidos por qualquer
ferramenta (dashboard, `tail`, `jq`, Grafana Loki, ELK...):

  1. Log da aplicação   logs/agrosmart.log
     Uma linha JSON por evento (nível, componente, mensagem, run_id). Também é
     impresso no stdout, então aparece em `docker compose logs`.

  2. Registro de execuções  dados/monitoramento/execucoes.jsonl
     Uma linha por etapa de cada ciclo do pipeline: início, fim, duração,
     status (ok/erro) e mensagem de erro. É também o EVENT LOG técnico usado
     na mineração de processos (case = run_id, atividade = etapa).

  3. Status atual  dados/monitoramento/status.json
     Resumo do último ciclo + indicadores de funcionamento (linhas processadas,
     taxa de rejeição, alertas críticos, F1 do modelo, talhões críticos, ...).
     É o que o healthcheck do container e a aba "Monitoramento" do dashboard leem.
"""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = Path(os.environ.get("AGRO_LOGS_DIR", ROOT_DIR / "logs"))
DADOS_DIR = Path(os.environ.get("AGRO_DADOS_DIR", ROOT_DIR / "dados"))
MONITOR_DIR = DADOS_DIR / "monitoramento"
ARQ_LOG = LOGS_DIR / "agrosmart.log"
ARQ_EXECUCOES = MONITOR_DIR / "execucoes.jsonl"
ARQ_STATUS = MONITOR_DIR / "status.json"

FORMATO_DATA = "%Y-%m-%d %H:%M:%S"


def agora() -> str:
    return datetime.now().strftime(FORMATO_DATA)


class FormatoJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        evento = {
            "ts": datetime.fromtimestamp(record.created).strftime(FORMATO_DATA),
            "nivel": record.levelname,
            "componente": record.name,
            "mensagem": record.getMessage(),
        }
        for campo in ("run_id", "etapa", "duracao_s"):
            if hasattr(record, campo):
                evento[campo] = getattr(record, campo)
        return json.dumps(evento, ensure_ascii=False)


def configurar_logger(nome: str = "agrosmart") -> logging.Logger:
    """Logger com saída legível no console e JSON (rotacionado) em logs/agrosmart.log."""
    logger = logging.getLogger(nome)
    if logger.handlers:
        return logger
    logger.setLevel(os.environ.get("AGRO_LOG_LEVEL", "INFO"))
    logger.propagate = False

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
                                           datefmt=FORMATO_DATA))
    logger.addHandler(console)

    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        arquivo = RotatingFileHandler(ARQ_LOG, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    except OSError as erro:
        # ex.: container read-only sem volume de logs — a plataforma segue logando no stdout
        logger.warning(f"Log em arquivo desativado ({erro}); usando apenas o console")
        return logger
    arquivo.setFormatter(FormatoJson())
    logger.addHandler(arquivo)
    return logger


def _ler_json(caminho: Path) -> dict:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def coletar_indicadores(dados_dir: Path = DADOS_DIR) -> dict:
    """Indicadores de funcionamento a partir das saídas do pipeline."""
    qualidade = _ler_json(dados_dir / "trusted" / "qualidade_dados.json")
    metricas = _ler_json(dados_dir / "refined" / "metricas_modelo.json")
    status = _ler_json(dados_dir / "refined" / "status_talhoes.json")
    indicadores: dict = {}
    if qualidade:
        recebidas = qualidade.get("linhas_recebidas", 0) or 0
        rejeitadas = qualidade.get("rejeitadas_fora_da_faixa", 0)
        indicadores.update({
            "linhas_recebidas": recebidas,
            "linhas_processadas": qualidade.get("linhas_processadas"),
            "linhas_rejeitadas": rejeitadas,
            "taxa_rejeicao_pct": round(100 * rejeitadas / recebidas, 2) if recebidas else None,
            "duplicadas_removidas": qualidade.get("duplicadas_removidas"),
            "ultima_leitura_dados": (qualidade.get("periodo") or [None, None])[1],
        })
    if metricas:
        indicadores["f1_modelo"] = metricas.get("metricas_modelo", {}).get("f1")
        indicadores["f1_baseline"] = metricas.get("metricas_baseline_regra_atual", {}).get("f1")
    if status:
        niveis = [s.get("nivel_final") for s in status.values()]
        indicadores.update({
            "talhoes_monitorados": len(status),
            "talhoes_criticos": niveis.count("CRITICO"),
            "talhoes_atencao": niveis.count("ATENCAO"),
            "alertas_ativos": sum(len(s.get("alertas_ativos", [])) for s in status.values()),
        })
    alertas_csv = dados_dir / "refined" / "alertas.csv"
    if alertas_csv.exists():
        with open(alertas_csv, encoding="utf-8") as f:
            linhas = f.read().splitlines()[1:]
        indicadores["episodios_alerta"] = len(linhas)
        indicadores["episodios_criticos"] = sum(",CRITICO," in linha for linha in linhas)
    return indicadores


class Execucao:
    """Um ciclo do pipeline. Uso:

        with Execucao(ciclo=1) as execucao:
            with execucao.etapa("Coleta"):
                ...
    """

    def __init__(self, ciclo: int = 1, parametros: dict | None = None,
                 logger: logging.Logger | None = None):
        self.run_id = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        self.ciclo = ciclo
        self.parametros = parametros or {}
        self.logger = logger or configurar_logger()
        self.etapas: list[dict] = []
        self.inicio = None
        self._t0 = 0.0
        self.status = "em_execucao"

    def _extra(self, **kw):
        return {"extra": {"run_id": self.run_id, **kw}}

    def __enter__(self):
        MONITOR_DIR.mkdir(parents=True, exist_ok=True)
        self.inicio = agora()
        self._t0 = time.perf_counter()
        self.logger.info(f"Ciclo {self.ciclo} iniciado (run_id={self.run_id}, parametros={self.parametros})",
                         **self._extra())
        self._gravar_status()
        return self

    @contextmanager
    def etapa(self, nome: str):
        registro = {"run_id": self.run_id, "ciclo": self.ciclo, "etapa": nome, "inicio": agora()}
        t0 = time.perf_counter()
        self.logger.info(f"Etapa '{nome}' iniciada", **self._extra(etapa=nome))
        try:
            yield registro
            registro["status"] = "ok"
        except BaseException as erro:
            registro["status"] = "erro"
            registro["erro"] = f"{type(erro).__name__}: {erro}"[:500]
            raise
        finally:
            registro["fim"] = agora()
            registro["duracao_s"] = round(time.perf_counter() - t0, 3)
            self.etapas.append(registro)
            with open(ARQ_EXECUCOES, "a", encoding="utf-8") as f:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            nivel = logging.INFO if registro["status"] == "ok" else logging.ERROR
            self.logger.log(nivel, f"Etapa '{nome}' {registro['status']} em {registro['duracao_s']}s"
                            + (f" — {registro['erro']}" if "erro" in registro else ""),
                            **self._extra(etapa=nome, duracao_s=registro["duracao_s"]))

    def __exit__(self, tipo, valor, tb):
        self.status = "ok" if tipo is None else "erro"
        duracao = round(time.perf_counter() - self._t0, 3)
        nivel = logging.INFO if self.status == "ok" else logging.ERROR
        self.logger.log(nivel, f"Ciclo {self.ciclo} finalizado com status={self.status} em {duracao}s",
                        **self._extra(duracao_s=duracao))
        self._gravar_status(duracao)
        return False  # não engole a exceção

    def _gravar_status(self, duracao: float | None = None):
        anterior = _ler_json(ARQ_STATUS)
        historico = anterior.get("historico", {"ciclos_ok": 0, "ciclos_erro": 0})
        if self.status == "ok":
            historico["ciclos_ok"] += 1
        elif self.status == "erro":
            historico["ciclos_erro"] += 1
        total = historico["ciclos_ok"] + historico["ciclos_erro"]
        historico["disponibilidade_pct"] = round(100 * historico["ciclos_ok"] / total, 1) if total else None

        status = {
            "plataforma": "AgroSmart",
            "run_id": self.run_id,
            "ciclo": self.ciclo,
            "status": self.status,
            "inicio": self.inicio,
            "fim": agora() if duracao is not None else None,
            "duracao_s": duracao,
            "parametros": self.parametros,
            "etapas": [{k: e.get(k) for k in ("etapa", "status", "duracao_s", "erro")} for e in self.etapas],
            "ultimo_sucesso": (agora() if self.status == "ok" else anterior.get("ultimo_sucesso")),
            "historico": historico,
            "indicadores": coletar_indicadores() if duracao is not None else anterior.get("indicadores", {}),
        }
        tmp = ARQ_STATUS.with_suffix(".tmp")
        tmp.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(ARQ_STATUS)  # escrita atômica: o healthcheck nunca lê arquivo pela metade


def ler_execucoes(caminho: Path = ARQ_EXECUCOES) -> list[dict]:
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]
