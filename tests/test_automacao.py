import automacao_inteligente as auto


def test_episodio_de_seca_agrupa_leituras_consecutivas(leituras):
    episodios = auto.detectar_episodios(leituras)
    seca = episodios[(episodios["talhao_id"] == "TAL-A") & (episodios["regra"] == "DEFICIT_HIDRICO")]
    assert len(seca) == 1, "leituras consecutivas devem virar UM episódio"
    ep = seca.iloc[0]
    assert ep["nivel"] == "CRITICO"          # pior nível do episódio
    assert ep["valor_pior"] == 15.0
    assert not ep["ativo_agora"]             # a umidade voltou ao normal


def test_falha_de_irrigacao_herda_regra_da_fase4(leituras):
    episodios = auto.detectar_episodios(leituras)
    falha = episodios[episodios["regra"] == "FALHA_IRRIGACAO"]
    assert set(falha["talhao_id"]) == {"TAL-A"}
    assert "manutenção" in falha.iloc[0]["acao_automatica"]


def test_talhao_normal_nao_gera_alerta(leituras):
    episodios = auto.detectar_episodios(leituras)
    assert "TAL-B" not in set(episodios["talhao_id"])


def test_classe_de_risco_do_ml():
    assert auto.classe_risco(0.05) == "BAIXO"
    assert auto.classe_risco(0.30) == "MEDIO"
    assert auto.classe_risco(0.60) == "ALTO"


def test_alvo_olha_6h_a_frente(leituras):
    df = auto.criar_alvo(leituras)
    a = df[df["talhao_id"] == "TAL-A"].sort_values("timestamp")
    # a 1ª leitura (umidade 50%) já "enxerga" a umidade 18% que vem 2h30 depois
    assert a["alvo_evento_6h"].iloc[0] == 1.0
    # o fim da série não tem horizonte de 6h completo -> sem alvo
    assert a["alvo_evento_6h"].isna().iloc[-1]
