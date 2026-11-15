import pandas as pd
import processar_dados as proc


def test_separar_invalidos_registra_motivo():
    df = pd.DataFrame({
        "temperatura_c": [25.0, -99.0], "umidade_solo_pct": [40.0, 137.4],
        "luminosidade_pct": [50.0, 50.0], "perc_folhas_doentes": [1.0, 1.0],
    })
    validos, rejeitados = proc.separar_invalidos(df)
    assert len(validos) == 1
    assert len(rejeitados) == 1
    motivo = rejeitados["motivo_rejeicao"].iloc[0]
    assert "temperatura_c=-99.0" in motivo and "umidade_solo_pct=137.4" in motivo


def test_valor_ausente_nao_e_rejeitado():
    df = pd.DataFrame({"temperatura_c": [None], "umidade_solo_pct": [40.0],
                       "luminosidade_pct": [50.0], "perc_folhas_doentes": [1.0]})
    validos, rejeitados = proc.separar_invalidos(df)
    assert len(validos) == 1 and rejeitados.empty


def test_imputacao_por_interpolacao_marca_linha():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-10-01", periods=3, freq="30min"),
        "talhao_id": ["T1"] * 3,
        "temperatura_c": [20.0, None, 24.0], "umidade_solo_pct": [40.0, 40.0, 40.0],
        "luminosidade_pct": [10.0, 10.0, 10.0],
    })
    resultado = proc.imputar_ausentes(df)
    assert resultado["temperatura_c"].tolist() == [20.0, 22.0, 24.0]
    assert resultado["valor_imputado"].tolist() == [0, 1, 0]


def test_periodo_do_dia():
    assert [proc.periodo_do_dia(h) for h in (2, 8, 14, 20)] == ["madrugada", "manha", "tarde", "noite"]
