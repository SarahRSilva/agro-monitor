"""
healthcheck.py — verifica se a plataforma AgroSmart está saudável.

Critérios (todos precisam passar):
  1. existe um status de execução (dados/monitoramento/status.json);
  2. o último ciclo concluído terminou sem erro;
  3. o último sucesso é recente (menos de AGRO_MAX_IDADE_MIN minutos — padrão 15);
  4. as saídas principais da camada refined existem.

Saída: JSON com o diagnóstico; código 0 = saudável, 1 = não saudável.
Usado pelo HEALTHCHECK do Docker e pelo pipeline de CI (smoke test).

Uso:
    python monitoramento/healthcheck.py
    AGRO_MAX_IDADE_MIN=60 python monitoramento/healthcheck.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from monitoramento.monitor import ARQ_STATUS, DADOS_DIR, FORMATO_DATA  # noqa: E402

SAIDAS_OBRIGATORIAS = [
    "trusted/leituras_processadas.csv",
    "refined/alertas.csv",
    "refined/status_talhoes.json",
    "refined/predicoes_risco.csv",
]


def verificar(max_idade_min: float, agora: datetime | None = None) -> dict:
    agora = agora or datetime.now()
    checks = {}
    try:
        status = json.loads(ARQ_STATUS.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        status = None
    checks["status_existe"] = status is not None

    if status:
        em_execucao = status.get("status") == "em_execucao"
        # durante um ciclo em andamento vale o resultado do ciclo anterior
        checks["ultimo_ciclo_ok"] = status.get("status") == "ok" or (
            em_execucao and status.get("ultimo_sucesso") is not None)
        ultimo = status.get("ultimo_sucesso")
        idade = ((agora - datetime.strptime(ultimo, FORMATO_DATA)).total_seconds() / 60) if ultimo else None
        checks["dados_recentes"] = idade is not None and idade <= max_idade_min
    else:
        idade = None
        checks["ultimo_ciclo_ok"] = checks["dados_recentes"] = False

    faltando = [s for s in SAIDAS_OBRIGATORIAS if not (DADOS_DIR / s).exists()]
    checks["saidas_refined"] = not faltando

    return {
        "saudavel": all(checks.values()),
        "checks": checks,
        "idade_ultimo_sucesso_min": round(idade, 1) if idade is not None else None,
        "max_idade_min": max_idade_min,
        "saidas_faltando": faltando,
        "ultimo_run_id": status.get("run_id") if status else None,
        "indicadores": status.get("indicadores", {}) if status else {},
    }


def main() -> int:
    resultado = verificar(float(os.environ.get("AGRO_MAX_IDADE_MIN", "15")))
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["saudavel"] else 1


if __name__ == "__main__":
    sys.exit(main())
