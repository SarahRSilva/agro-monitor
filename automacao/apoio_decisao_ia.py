"""
apoio_decisao_ia.py
Apoio à decisão com IA Generativa (Fase 6 reaproveitando a Fase 5).

Publica, na camada refined, o mesmo "contrato de dados" que o Data Lake da
Fase 5 gera em datalake-demo/datalake/refined/resumo_talhoes.json — agora
alimentado pelos sensores da Fase 6 e enriquecido com o resultado da
automação (alertas do motor de regras e risco previsto pelo modelo de ML).
Em seguida chama o módulo de IA Generativa da Fase 5
(datalake-demo/scripts/04_ia_generativa.py) para gerar um relatório por talhão.

  dados/trusted/leituras_processadas.csv ─┐
  dados/refined/status_talhoes.json ──────┴─► dados/refined/resumo_talhoes.json
                                              ─► 04_ia_generativa.py (Fase 5)
                                              ─► dados/refined/relatorios_ia/<TALHAO>_<data>.md

Uso:
    python automacao/apoio_decisao_ia.py                # modo simulado (sem API)
    python automacao/apoio_decisao_ia.py --talhao TAL-02
    python automacao/apoio_decisao_ia.py --real         # API da Anthropic, se ANTHROPIC_API_KEY existir
"""
import argparse
import importlib.util
import json
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
TRUSTED_DIR = ROOT_DIR / "dados" / "trusted"
REFINED_DIR = ROOT_DIR / "dados" / "refined"
RELATORIOS_DIR = REFINED_DIR / "relatorios_ia"
SCRIPTS_FASE5 = ROOT_DIR / "datalake-demo" / "scripts"

JANELA_ANALISE = pd.Timedelta("72h")  # 24h fica dominada pelo ciclo dia/noite da umidade
PRIORIDADE_POR_NIVEL = {"CRITICO": "alta", "ATENCAO": "media", "AVISO": "baixa"}


def carregar_modulo_fase5(arquivo: str):
    """Os scripts da Fase 5 começam com número (01_, 03_...), então não dá para usar import direto."""
    spec = importlib.util.spec_from_file_location(Path(arquivo).stem, SCRIPTS_FASE5 / arquivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


camada_refined_fase5 = carregar_modulo_fase5("03_camada_refined.py")
ia_generativa_fase5 = carregar_modulo_fase5("04_ia_generativa.py")


def deteccoes_relevantes(janela: pd.DataFrame) -> list[dict]:
    """Detecções da câmera no período. A Fase 6 não tem a confiança do classificador,
    então a gravidade vem do % de folhas doentes."""
    com_praga = janela[janela["praga_presente"] == 1]
    deteccoes = []
    for praga, grupo in com_praga.groupby("praga_detectada"):
        deteccoes.append({
            "talhao_id": grupo["talhao_id"].iloc[0],
            "timestamp": grupo["timestamp"].max().isoformat(),
            "classe": praga,
            "confianca": None,
            "perc_folhas_doentes": round(float(grupo["perc_folhas_doentes"].max()), 1),
            "fonte": "visao_computacional",
        })
    return deteccoes


def montar_resumo_por_talhao(leituras: pd.DataFrame, status: dict) -> dict:
    resumo = {}
    for talhao_id, grupo in leituras.groupby("talhao_id"):
        grupo = grupo.sort_values("timestamp")
        janela = grupo[grupo["timestamp"] > grupo["timestamp"].max() - JANELA_ANALISE]
        ultima = janela.iloc[-1]
        s = status[talhao_id]

        resumo[talhao_id] = {
            # ── contrato da camada Refined da Fase 5 ──
            "talhao_id": talhao_id,
            "periodo_analisado": {
                "inicio": janela["timestamp"].iloc[0].isoformat(),
                "fim": ultima["timestamp"].isoformat(),
                "total_leituras": int(len(janela)),
            },
            "umidade_solo_pct": {
                "atual": float(ultima["umidade_solo_pct"]),
                "media_periodo": round(float(janela["umidade_solo_pct"].mean()), 1),
                "tendencia": camada_refined_fase5.calcular_tendencia(janela["umidade_solo_pct"].tolist()),
            },
            "temperatura_c": {
                "atual": float(ultima["temperatura_c"]),
                "media_periodo": round(float(janela["temperatura_c"].mean()), 1),
            },
            "ph_solo": None,                      # sensores da Fase 6 não medem pH
            "previsao_precipitacao_3d_mm": None,  # sem API de clima na Fase 6
            "deteccoes_imagem_relevantes": deteccoes_relevantes(janela),
            "alertas": [{"tipo": a["regra"].lower(), "prioridade": PRIORIDADE_POR_NIVEL[a["nivel"]],
                         "detalhe": f"{a['regra']} ({a['nivel']}) ativo há {a['duracao_h']}h, "
                                    f"pior valor {a['valor_pior']}"}
                        for a in s["alertas_ativos"]],
            "gerado_em": datetime.now().isoformat(timespec="seconds"),
            # ── extensões da Fase 6 ──
            "chuva_24h_mm": float(ultima["chuva_24h_mm"]),
            "alertas_automacao": [{"regra": a["regra"], "nivel": a["nivel"]} for a in s["alertas_ativos"]],
            "risco_previsto_6h": {"classe": s["risco_previsto"], "probabilidade": s["prob_evento_6h"]},
            "nivel_final": s["nivel_final"],
        }
    return resumo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--talhao", help="gerar relatório apenas para este talhão (ex: TAL-02)")
    parser.add_argument("--real", action="store_true", help="usar a API real da Anthropic em vez do modo simulado")
    args = parser.parse_args()

    caminho_status = REFINED_DIR / "status_talhoes.json"
    if not caminho_status.exists():
        raise SystemExit("Rode antes: python automacao/automacao_inteligente.py")
    leituras = pd.read_csv(TRUSTED_DIR / "leituras_processadas.csv", parse_dates=["timestamp"])
    status = json.loads(caminho_status.read_text(encoding="utf-8"))

    resumo = montar_resumo_por_talhao(leituras, status)
    with open(REFINED_DIR / "resumo_talhoes.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    print(f"[ia] contrato da camada refined (Fase 5) com {len(resumo)} talhões -> refined/resumo_talhoes.json")

    if args.talhao:
        talhoes = [args.talhao]
    else:
        talhoes = list(resumo)
        shutil.rmtree(RELATORIOS_DIR, ignore_errors=True)  # evita relatórios de execuções anteriores
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    for talhao_id in talhoes:
        contexto = resumo[talhao_id]
        relatorio = ia_generativa_fase5.gerar_relatorio(contexto, usar_api_real=args.real)
        data_leitura = contexto["periodo_analisado"]["fim"][:10]
        (RELATORIOS_DIR / f"{talhao_id}_{data_leitura}.md").write_text(relatorio, encoding="utf-8")
    print(f"[ia] {len(talhoes)} relatório(s) de apoio à decisão -> refined/relatorios_ia/")


if __name__ == "__main__":
    main()
