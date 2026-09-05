"""
01_ingestao.py
Simula a etapa de ingestao: le os arquivos de exemplo (JSON/CSV) e grava na
camada Raw do Data Lake local, particionada por fonte/data. Tambem gera um
pequeno historico sintetico (5 dias) para os talhoes TAL-07 e TAL-12, para que
as camadas seguintes tenham dados suficientes para calcular tendencia.

Uso:
    python scripts/01_ingestao.py
"""
import csv
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE_DIR.parent / "ingestion" / "samples"
RAW_DIR = BASE_DIR / "datalake" / "raw"

DATA_REFERENCIA = datetime(2026, 9, 5)


def limpar_datalake():
    datalake_dir = BASE_DIR / "datalake"
    if datalake_dir.exists():
        shutil.rmtree(datalake_dir)


def ingerir_arquivo_sensor():
    """Copia o exemplo de leitura de sensor (Kafka) para raw/sensores/<data>/"""
    origem = SAMPLES_DIR / "leitura_sensor.json"
    destino_dir = RAW_DIR / "sensores" / DATA_REFERENCIA.strftime("%Y-%m-%d")
    destino_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(origem, destino_dir / origem.name)
    print(f"[ingestao] sensor -> {destino_dir / origem.name}")


def ingerir_arquivo_imagem():
    """Copia o exemplo de deteccao por visao computacional para raw/imagens/<data>/"""
    origem = SAMPLES_DIR / "deteccao_imagem.json"
    destino_dir = RAW_DIR / "imagens" / DATA_REFERENCIA.strftime("%Y-%m-%d")
    destino_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(origem, destino_dir / origem.name)
    print(f"[ingestao] imagem -> {destino_dir / origem.name}")


def ingerir_csv_do_dia():
    """Copia o CSV de exemplo (lote do dia 2026-09-05) tal como recebido."""
    origem = SAMPLES_DIR / "leituras_solo.csv"
    destino_dir = RAW_DIR / "leituras_solo" / DATA_REFERENCIA.strftime("%Y-%m-%d")
    destino_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(origem, destino_dir / origem.name)
    print(f"[ingestao] csv do dia -> {destino_dir / origem.name}")


def gerar_historico_sintetico():
    """
    Gera 5 dias de leituras anteriores para dar historico as camadas
    seguintes calcularem tendencia. TAL-07 tem umidade em queda (para
    disparar o alerta de deficit hidrico no relatorio final). TAL-12 fica
    estavel (para servir de contraste, sem alerta).

    Tambem injeta DE PROPOSITO uma leitura invalida (umidade > 100%) no dia
    2026-09-02 do TAL-07, para demonstrar a rejeicao de dados na camada
    Trusted (etapa 02).
    """
    horarios = ["06:00", "12:00", "18:00"]

    for dias_atras in range(5, 0, -1):
        data = DATA_REFERENCIA - timedelta(days=dias_atras)
        data_str = data.strftime("%Y-%m-%d")
        destino_dir = RAW_DIR / "leituras_solo" / data_str
        destino_dir.mkdir(parents=True, exist_ok=True)
        caminho_csv = destino_dir / f"leituras_solo_{data_str}.csv"

        # TAL-07: comeca em ~58% e cai ate ~41% (tendencia de queda)
        umidade_base_tal07 = 58 - (5 - dias_atras) * 4.2
        # TAL-12: estavel em torno de 47-50%
        umidade_base_tal12 = 48

        linhas = []
        for i, hora in enumerate(horarios):
            umidade_tal07 = round(umidade_base_tal07 - i * 1.5, 1)
            if data_str == "2026-09-02" and hora == "12:00":
                # leitura invalida proposital (sensor com defeito) -> deve
                # ser rejeitada pela camada Trusted
                umidade_tal07 = 137.4

            linhas.append({
                "talhao_id": "TAL-07",
                "data": data_str,
                "hora": hora,
                "umidade_solo_pct": umidade_tal07,
                "temperatura_c": round(20 + i * 2.5, 1),
                "ph_solo": 6.3,
                "precipitacao_mm": 0.0,
            })
            linhas.append({
                "talhao_id": "TAL-12",
                "data": data_str,
                "hora": hora,
                "umidade_solo_pct": round(umidade_base_tal12 + (i % 2), 1),
                "temperatura_c": round(19 + i * 2.3, 1),
                "ph_solo": 6.6,
                "precipitacao_mm": 0.0,
            })

        with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
            campos = ["talhao_id", "data", "hora", "umidade_solo_pct",
                      "temperatura_c", "ph_solo", "precipitacao_mm"]
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(linhas)

        print(f"[ingestao] historico sintetico -> {caminho_csv}")


if __name__ == "__main__":
    limpar_datalake()
    ingerir_arquivo_sensor()
    ingerir_arquivo_imagem()
    ingerir_csv_do_dia()
    gerar_historico_sintetico()
    print("\nCamada RAW populada com sucesso em datalake/raw/")
