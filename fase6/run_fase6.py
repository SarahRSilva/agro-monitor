"""
run_fase6.py
Executa a plataforma AgroSmart integrada, de ponta a ponta:

  1) Coleta      iot/simulador_sensores.py          -> dados/raw/sensores_campo.csv
                 (+ dados/raw/tinkercad_serial.txt capturado do Arduino no TinkerCad)
  2) Processamento processamento/processar_dados.py -> dados/processed/
  3) Automação   automacao/automacao_inteligente.py -> dados/output/
  4) Dashboard   dashboard/app.py (Streamlit)       -> http://localhost:8501

Uso:
    python fase6/run_fase6.py                 # pipeline completo (passos 1-3)
    python fase6/run_fase6.py --dashboard     # pipeline + abre o dashboard
    python fase6/run_fase6.py --seed 7        # outro cenário aleatório
"""
import argparse
import subprocess
import sys
from pathlib import Path

FASE6_DIR = Path(__file__).resolve().parent


def rodar(titulo, script, *args):
    print(f"\n{'#' * 70}\n# {titulo}\n{'#' * 70}")
    subprocess.run([sys.executable, str(FASE6_DIR / script), *args], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="42")
    parser.add_argument("--dias", default="7")
    parser.add_argument("--dashboard", action="store_true", help="abrir o dashboard ao final")
    args = parser.parse_args()

    rodar("1/3 Coleta de dados (simulador de sensores)", "iot/simulador_sensores.py",
          "--seed", args.seed, "--dias", args.dias)
    rodar("2/3 Processamento e preparação", "processamento/processar_dados.py")
    rodar("3/3 Automação inteligente (regras + ML)", "automacao/automacao_inteligente.py")

    print("\nPipeline concluído. Resultados em fase6/dados/processed e fase6/dados/output.")
    if args.dashboard:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(FASE6_DIR / "dashboard" / "app.py")])
    else:
        print("Para abrir o dashboard: streamlit run fase6/dashboard/app.py")
