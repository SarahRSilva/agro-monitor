"""Teste de integração: roda a plataforma inteira (coleta -> mineração) numa cópia isolada."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NECESSARIOS = ["run_plataforma.py", "iot", "processamento", "automacao", "mineracao", "monitoramento",
               "docker/api/regras.py", "datalake-demo/scripts", "dados/raw/tinkercad_serial.txt"]


def test_pipeline_ponta_a_ponta(tmp_path):
    for rel in NECESSARIOS:
        origem, destino = ROOT / rel, tmp_path / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        if origem.is_dir():
            shutil.copytree(origem, destino, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy(origem, destino)

    resultado = subprocess.run([sys.executable, "run_plataforma.py", "--dias", "3"], cwd=tmp_path,
                               capture_output=True, text=True, timeout=300)
    assert resultado.returncode == 0, resultado.stderr[-2000:]

    dados = tmp_path / "dados"
    for rel in ["trusted/leituras_processadas.csv", "refined/alertas.csv", "refined/status_talhoes.json",
                "refined/processo/event_log.csv", "refined/processo/event_log.xes", "monitoramento/status.json"]:
        assert (dados / rel).exists(), rel

    status = json.loads((dados / "monitoramento" / "status.json").read_text())
    assert status["status"] == "ok"
    assert [e["etapa"] for e in status["etapas"]] == [
        "Coleta de dados", "Processamento", "Automação (regras + ML)", "IA Generativa", "Mineração de processos"]
    assert status["indicadores"]["talhoes_monitorados"] == 6

    saude = subprocess.run([sys.executable, "monitoramento/healthcheck.py"], cwd=tmp_path, capture_output=True)
    assert saude.returncode == 0
