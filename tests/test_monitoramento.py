import json
from datetime import datetime, timedelta

import pytest

from monitoramento import healthcheck, monitor


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """Redireciona os arquivos de monitoramento para uma pasta temporária."""
    dados = tmp_path / "dados"
    mon = dados / "monitoramento"
    for modulo in (monitor, healthcheck):
        monkeypatch.setattr(modulo, "DADOS_DIR", dados, raising=False)
        monkeypatch.setattr(modulo, "ARQ_STATUS", mon / "status.json", raising=False)
    monkeypatch.setattr(monitor, "MONITOR_DIR", mon)
    monkeypatch.setattr(monitor, "ARQ_EXECUCOES", mon / "execucoes.jsonl")
    return dados


def test_execucao_registra_etapas_e_status(ambiente):
    with monitor.Execucao(ciclo=1) as execucao:
        with execucao.etapa("Coleta"):
            pass
    linhas = monitor.ler_execucoes(monitor.ARQ_EXECUCOES)
    assert [linha["etapa"] for linha in linhas] == ["Coleta"]
    assert linhas[0]["status"] == "ok" and linhas[0]["duracao_s"] >= 0
    status = json.loads(monitor.ARQ_STATUS.read_text())
    assert status["status"] == "ok"
    assert status["historico"]["ciclos_ok"] == 1


def test_erro_em_etapa_e_registrado_e_propagado(ambiente):
    with pytest.raises(ValueError):
        with monitor.Execucao(ciclo=1) as execucao:
            with execucao.etapa("Automação"):
                raise ValueError("sensor offline")
    linha = monitor.ler_execucoes(monitor.ARQ_EXECUCOES)[-1]
    assert linha["status"] == "erro" and "sensor offline" in linha["erro"]
    status = json.loads(monitor.ARQ_STATUS.read_text())
    assert status["status"] == "erro"
    assert status["historico"]["disponibilidade_pct"] == 0.0


def _criar_saidas(dados):
    for rel in healthcheck.SAIDAS_OBRIGATORIAS:
        (dados / rel).parent.mkdir(parents=True, exist_ok=True)
        (dados / rel).write_text("x")


def test_healthcheck_saudavel_e_dados_velhos(ambiente):
    _criar_saidas(ambiente)
    with monitor.Execucao(ciclo=1):
        pass
    assert healthcheck.verificar(max_idade_min=15)["saudavel"]
    daqui_a_1h = datetime.now() + timedelta(hours=1)
    resultado = healthcheck.verificar(max_idade_min=15, agora=daqui_a_1h)
    assert not resultado["saudavel"]
    assert resultado["checks"]["dados_recentes"] is False


def test_healthcheck_sem_execucao(ambiente):
    resultado = healthcheck.verificar(max_idade_min=15)
    assert not resultado["saudavel"] and resultado["checks"]["status_existe"] is False
