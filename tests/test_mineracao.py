import automacao_inteligente as auto
import mineracao_processos as mp
import pandas as pd


def _event_log(leituras):
    alertas = auto.detectar_episodios(leituras)
    predicoes = leituras[["timestamp", "talhao_id"]].assign(prob_evento_6h=0.9, risco_previsto="ALTO")
    return mp.construir_event_log(leituras, alertas, predicoes), alertas


def test_event_log_tem_colunas_padrao(leituras):
    log, _ = _event_log(leituras)
    assert {"case_id", "atividade", "timestamp", "recurso"} <= set(log.columns)
    assert log.groupby("case_id")["timestamp"].apply(lambda s: s.is_monotonic_increasing).all()


def test_ciclo_de_vida_da_seca(leituras):
    log, _ = _event_log(leituras)
    caso = log[log["regra"] == "DEFICIT_HIDRICO"]
    atividades = caso["atividade"].tolist()
    assert atividades[0] == "Risco previsto pelo ML"
    assert atividades.index("Alerta disparado") < atividades.index("Ação automática executada")
    assert "Escalado para CRÍTICO" in atividades          # começou ATENCAO e virou CRITICO
    assert atividades[-1] == "Condição normalizada"


def test_variantes_e_dfg(leituras):
    log, _ = _event_log(leituras)
    var = mp.variantes(log)
    assert var["casos"].sum() == log["case_id"].nunique()
    assert abs(var["pct_casos"].sum() - 100) < 0.5
    dfg = mp.dfg(log)
    inicio = dfg[dfg["de"] == mp.INICIO]["frequencia"].sum()
    assert inicio == log["case_id"].nunique()        # todo caso sai do início exatamente uma vez


def test_xes_exportado(tmp_path, leituras):
    log, _ = _event_log(leituras)
    destino = tmp_path / "log.xes"
    mp.exportar_xes(log, destino)
    texto = destino.read_text(encoding="utf-8")
    assert texto.count("<trace>") == log["case_id"].nunique()
    assert texto.count("<event>") == len(log)


def test_analise_pipeline():
    execs = [
        {"run_id": "r1", "ciclo": 1, "etapa": "Coleta", "inicio": "2026-11-15 10:00:00",
         "fim": "2026-11-15 10:00:01", "duracao_s": 1.0, "status": "ok"},
        {"run_id": "r1", "ciclo": 1, "etapa": "Automação", "inicio": "2026-11-15 10:00:01",
         "fim": "2026-11-15 10:00:04", "duracao_s": 3.0, "status": "erro"},
    ]
    tabela = mp.analisar_pipeline(mp.event_log_pipeline(execs))
    automacao = tabela.set_index("atividade").loc["Automação"]
    assert automacao["erros"] == 1
    assert automacao["pct_tempo_ciclo"] == 75.0
    assert isinstance(tabela, pd.DataFrame)
