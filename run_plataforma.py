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
  5) Dashboard     dashboard/app.py (Streamlit)       -> http://localhost:8501

Uso:
    python run_plataforma.py                 # pipeline completo (passos 1-4)
    python run_plataforma.py --dashboard     # pipeline + abre o dashboard
    python run_plataforma.py --seed 7        # outro cenário aleatório
    python run_plataforma.py --real          # passo 4 com a API da Anthropic (ANTHROPIC_API_KEY)
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent


def rodar(titulo, script, *args):
    print(f"\n{'#' * 70}\n# {titulo}\n{'#' * 70}", flush=True)
    subprocess.run([sys.executable, str(ROOT_DIR / script), *args], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="42")
    parser.add_argument("--dias", default="7")
    parser.add_argument("--dashboard", action="store_true", help="abrir o dashboard ao final")
    parser.add_argument("--real", action="store_true", help="usar a API real da Anthropic na IA Generativa")
    args = parser.parse_args()

    rodar("1/4 Coleta de dados (simulador de sensores)", "iot/simulador_sensores.py",
          "--seed", args.seed, "--dias", args.dias)
    rodar("2/4 Processamento e preparação (raw -> trusted)", "processamento/processar_dados.py")
    rodar("3/4 Automação inteligente (regras + ML)", "automacao/automacao_inteligente.py")
    rodar("4/4 Apoio à decisão com IA Generativa", "automacao/apoio_decisao_ia.py",
          *(["--real"] if args.real else []))

    print("\nPipeline concluído. Resultados em dados/trusted e dados/refined.")
    if args.dashboard:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(ROOT_DIR / "dashboard" / "app.py")])
    else:
        print("Para abrir o dashboard: streamlit run dashboard/app.py")
