import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
for caminho in (ROOT, ROOT / "automacao", ROOT / "processamento", ROOT / "mineracao", ROOT / "docker" / "api"):
    sys.path.insert(0, str(caminho))


def _leituras(talhao, n=24, **valores):
    base = {
        "temperatura_c": 24.0, "umidade_solo_pct": 50.0, "luminosidade_pct": 60.0, "movimento_detectado": 0,
        "irrigacao_ligada": 0, "precipitacao_mm": 0.0, "perc_folhas_doentes": 5.0, "praga_detectada": "nenhuma",
        "praga_presente": 0, "tendencia_umidade_6h": 0.0, "chuva_24h_mm": 0.0, "fonte": "simulador_campo",
        "valor_imputado": 0,
    }
    tempos = pd.date_range("2026-10-01", periods=n, freq="30min")
    linhas = []
    for i, ts in enumerate(tempos):
        linha = {**base, "timestamp": ts, "talhao_id": talhao}
        for coluna, valor in valores.items():
            linha[coluna] = valor[i] if isinstance(valor, list) else valor
        linhas.append(linha)
    return pd.DataFrame(linhas)


@pytest.fixture
def leituras():
    """TAL-A: seca entre as leituras 3 e 7 (piorando até crítico) e normaliza; TAL-B: normal."""
    umidade = [50, 45, 40, 28, 25, 18, 15, 26, 50, 52, 53, 54] + [54] * 12
    a = _leituras("TAL-A", umidade_solo_pct=umidade)
    b = _leituras("TAL-B")
    return pd.concat([a, b], ignore_index=True)
