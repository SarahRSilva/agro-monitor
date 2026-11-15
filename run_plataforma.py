"""
run_plataforma.py
Executa a plataforma AgroSmart integrada, de ponta a ponta, nas camadas do
Data Lake da Fase 5 (dados/raw -> dados/trusted -> dados/refined):

  1) Coleta        iot/simulador_sensores.py          -> dados/raw/sensores_campo.csv
                   (+ dados/raw/tinkercad_serial.txt capturado do Arduino no TinkerCad)
  2) Processamento processamento/processar_dados.py   -> dados/trusted/ (+ raw/rejeitados/)
  3) Automação     automacao/automacao_inteligente.py -> dados/refined/
                   (motor de regras da Fase 4 estendido + Random Forest)
  4) IA Generativa automacao/apoio_decisao_ia.py      -> dados/refined/relatorios_ia/
                   (módulo de IA Generativa da Fase 5)
  5) Mineração     mineracao/mineracao_processos.py   -> dados/refined/processo/  (Fase 7)
  6) Dashboard     dashboard/app.py (Streamlit)       -> http://localhost:8501

Fase 7 — execução automatizada e monitoramento:
  - cada etapa é cronometrada e registrada em dados/monitoramento/execucoes.jsonl;
  - o status do último ciclo + indicadores ficam em dados/monitoramento/status.json;
  - o log estruturado (JSON) vai para logs/agrosmart.log;
  - com --loop a plataforma roda continuamente (um ciclo a cada --intervalo segundos),
    simulando um novo lote de sensores a cada ciclo — é o modo usado no container.

Uso:
    python run_plataforma.py                       # 1 ciclo (passos 1-5)
    python run_plataforma.py --dashboard           # 1 ciclo + abre o dashboard
    python run_plataforma.py --seed 7              # outro cenário aleatório
    python run_plataforma.py --real                # passo 4 com a API da Anthropic (ANTHROPIC_API_KEY)
    python run_plataforma.py --loop --intervalo 300            # execução contínua
    python run_plataforma.py --loop --intervalo 60 --max-ciclos 3
"""
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
from monitoramento.monitor import Execucao, configurar_logger  # noqa: E402

log = configurar_logger("agrosmart.orquestrador")
_parar = False


def _sinal_parada(signum, _frame):
    global _parar
    _parar = True
    log.warning(f"Sinal {signal.Signals(signum).name} recebido — encerrando após o ciclo atual")


class EtapaFalhou(RuntimeError):
    pass


def rodar(execucao: Execucao, titulo: str, script: str, *args):
    """Roda um script da plataforma como subprocesso, repassando a saída para o log."""
    componente = configurar_logger(f"agrosmart.{Path(script).stem}")
    with execucao.etapa(titulo):
        processo = subprocess.Popen(
            [sys.executable, str(ROOT_DIR / script), *args],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT_DIR,
            env={**os.environ, "PYTHONWARNINGS": "ignore"},
        )
        ultimas = []
        for linha in processo.stdout:
            linha = linha.rstrip()
            if linha:
                componente.info(linha, extra={"run_id": execucao.run_id, "etapa": titulo})
                ultimas = (ultimas + [linha])[-5:]
        if processo.wait() != 0:
            raise EtapaFalhou(f"{script} saiu com código {processo.returncode}: {' | '.join(ultimas)}")


def ciclo(numero: int, args) -> bool:
    seed = str(int(args.seed) + numero - 1) if args.loop else args.seed
    parametros = {"seed": seed, "dias": args.dias, "ia_real": args.real}
    try:
        with Execucao(ciclo=numero, parametros=parametros, logger=log) as execucao:
            rodar(execucao, "Coleta de dados", "iot/simulador_sensores.py", "--seed", seed, "--dias", args.dias)
            rodar(execucao, "Processamento", "processamento/processar_dados.py")
            rodar(execucao, "Automação (regras + ML)", "automacao/automacao_inteligente.py")
            rodar(execucao, "IA Generativa", "automacao/apoio_decisao_ia.py", *(["--real"] if args.real else []))
            rodar(execucao, "Mineração de processos", "mineracao/mineracao_processos.py")
        return True
    except EtapaFalhou:
        return False  # já registrado no monitoramento; no modo contínuo, segue para o próximo ciclo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="42")
    parser.add_argument("--dias", default="7")
    parser.add_argument("--dashboard", action="store_true", help="abrir o dashboard ao final")
    parser.add_argument("--real", action="store_true", help="usar a API real da Anthropic na IA Generativa")
    parser.add_argument("--loop", action="store_true", help="execução contínua (um ciclo a cada --intervalo)")
    parser.add_argument("--intervalo", type=int, default=int(os.environ.get("AGRO_INTERVALO_S", "300")),
                        help="segundos entre ciclos no modo --loop (padrão 300 ou $AGRO_INTERVALO_S)")
    parser.add_argument("--max-ciclos", type=int, default=0, help="no modo --loop, parar após N ciclos (0 = sem fim)")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, _sinal_parada)
    signal.signal(signal.SIGINT, _sinal_parada)

    if not args.loop:
        ok = ciclo(1, args)
        if not ok:
            sys.exit(1)
        log.info("Pipeline concluído. Resultados em dados/trusted, dados/refined e dados/monitoramento.")
        if args.dashboard:
            subprocess.run([sys.executable, "-m", "streamlit", "run", str(ROOT_DIR / "dashboard" / "app.py")])
        else:
            log.info("Para abrir o dashboard: streamlit run dashboard/app.py")
        return

    log.info(f"Modo contínuo: um ciclo a cada {args.intervalo}s"
             + (f", máximo de {args.max_ciclos} ciclos" if args.max_ciclos else ""))
    numero = 0
    while not _parar:
        numero += 1
        ciclo(numero, args)
        if args.max_ciclos and numero >= args.max_ciclos:
            break
        proximo = time.monotonic() + args.intervalo
        while not _parar and time.monotonic() < proximo:
            time.sleep(1)
    log.info(f"Execução contínua encerrada após {numero} ciclo(s)")


if __name__ == "__main__":
    main()
