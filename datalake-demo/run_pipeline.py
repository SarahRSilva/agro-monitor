"""
run_pipeline.py
Orquestra as 4 etapas do Data Lake demo, na ordem correta:
  1) Ingestao          -> popula datalake/raw/
  2) Camada Trusted    -> valida e limpa       datalake/raw/       -> datalake/trusted/
  3) Camada Refined    -> agrega               datalake/trusted/   -> datalake/refined/
  4) IA Generativa     -> le datalake/refined/ e gera os relatorios

Uso:
    python run_pipeline.py            # tudo em modo simulado (sem API)
    python run_pipeline.py --real     # usa a API real da Anthropic no passo 4,
                                       # se ANTHROPIC_API_KEY estiver definida
"""
import argparse
import runpy
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"


def rodar_etapa(nome_arquivo: str, argv_extra=None):
    print(f"\n{'#' * 70}\n# {nome_arquivo}\n{'#' * 70}")
    argv_original = sys.argv
    sys.argv = [nome_arquivo] + (argv_extra or [])
    try:
        runpy.run_path(str(SCRIPTS_DIR / nome_arquivo), run_name="__main__")
    finally:
        sys.argv = argv_original


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="usar a API real da Anthropic no passo de IA Generativa")
    args = parser.parse_args()

    rodar_etapa("01_ingestao.py")
    rodar_etapa("02_camada_trusted.py")
    rodar_etapa("03_camada_refined.py")
    rodar_etapa("04_ia_generativa.py", ["--real"] if args.real else [])

    print("\nPipeline completo executado. Veja os resultados em datalake/raw, "
          "datalake/trusted, datalake/refined e datalake/refined/relatorios_ia/")
