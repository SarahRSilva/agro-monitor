"""
processar_dados.py
Etapa de processamento e preparação dos dados (Fase 6). Segue a mesma ideia
de camadas do Data Lake da Fase 5 (raw -> trusted/processed):

  1. Leitura   — sensores_campo.csv (simulador) + tinkercad_serial.txt (Arduino)
  2. Padronização — schema único, tipos numéricos, timestamp em datetime
  3. Deduplicação — por (talhao_id, timestamp)
  4. Validação — faixas físicas plausíveis; o que está fora vai para
                 rejeitados.csv com o motivo (não é descartado em silêncio)
  5. Imputação — campos vazios preenchidos por interpolação temporal no
                 próprio talhão (marcados com valor_imputado=1)
  6. Features  — médias móveis, tendência de umidade, chuva acumulada,
                 extremos de temperatura em 24h, período do dia
  7. Agregação — resumo diário por talhão (insumo do dashboard)

Uso:
    python fase6/processamento/processar_dados.py
    python fase6/processamento/processar_dados.py --inicio-tinkercad "2026-10-04 12:00:00"
"""
import argparse
import json
from pathlib import Path

import pandas as pd

FASE6_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = FASE6_DIR / "dados" / "raw"
PROCESSED_DIR = FASE6_DIR / "dados" / "processed"

FAIXAS_VALIDAS = {
    "temperatura_c": (-10, 55),
    "umidade_solo_pct": (0, 100),
    "luminosidade_pct": (0, 100),
    "perc_folhas_doentes": (0, 100),
}
COLUNAS_NUMERICAS = list(FAIXAS_VALIDAS) + [
    "movimento_detectado", "irrigacao_ligada", "precipitacao_mm",
]


def carregar_sensores_campo() -> pd.DataFrame:
    caminho = RAW_DIR / "sensores_campo.csv"
    if not caminho.exists():
        raise SystemExit(f"Arquivo {caminho} não encontrado. Rode antes: python fase6/iot/simulador_sensores.py")
    df = pd.read_csv(caminho)
    df["fonte"] = "simulador_campo"
    return df


def carregar_tinkercad(inicio: str) -> pd.DataFrame:
    """Converte a saída serial do Arduino (millis) para o schema comum."""
    caminho = RAW_DIR / "tinkercad_serial.txt"
    if not caminho.exists():
        print("[processamento] tinkercad_serial.txt não encontrado — seguindo só com o simulador")
        return pd.DataFrame()
    df = pd.read_csv(caminho)
    df["timestamp"] = pd.Timestamp(inicio) + pd.to_timedelta(df["millis"], unit="ms")
    df["sensor_id"] = "ARDUINO-TC"
    df["precipitacao_mm"] = 0.0
    df["perc_folhas_doentes"] = 0.0  # estação TinkerCad não tem câmera
    df["praga_detectada"] = "nenhuma"
    df["fonte"] = "tinkercad"
    return df.drop(columns=["millis", "status"])


def padronizar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for coluna in COLUNAS_NUMERICAS:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df["praga_detectada"] = df["praga_detectada"].fillna("nenhuma").str.strip().str.lower()
    return df


def separar_invalidos(df: pd.DataFrame):
    def motivo(linha):
        problemas = [f"{coluna}={linha[coluna]} fora da faixa [{minimo}, {maximo}]"
                     for coluna, (minimo, maximo) in FAIXAS_VALIDAS.items()
                     if pd.notna(linha[coluna]) and not minimo <= linha[coluna] <= maximo]
        return "; ".join(problemas)

    motivos = df.apply(motivo, axis=1)
    invalido = motivos != ""
    rejeitados = df[invalido].assign(motivo_rejeicao=motivos[invalido])
    return df[~invalido].copy(), rejeitados


def imputar_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    colunas = ["temperatura_c", "umidade_solo_pct", "luminosidade_pct"]
    df["valor_imputado"] = df[colunas].isna().any(axis=1).astype(int)
    df = df.set_index("timestamp")
    df[colunas] = df.groupby("talhao_id")[colunas].transform(
        lambda s: s.interpolate(method="time").ffill().bfill())
    return df.reset_index()


def periodo_do_dia(hora: int) -> str:
    if hora < 6:
        return "madrugada"
    if hora < 12:
        return "manha"
    if hora < 18:
        return "tarde"
    return "noite"


def criar_features(df: pd.DataFrame) -> pd.DataFrame:
    partes = []
    for _, grupo in df.groupby("talhao_id"):
        g = grupo.sort_values("timestamp").set_index("timestamp")
        g["umidade_media_3h"] = g["umidade_solo_pct"].rolling("3h").mean().round(1)
        g["temp_media_3h"] = g["temperatura_c"].rolling("3h").mean().round(1)
        # tendência: umidade atual menos a umidade mais antiga da janela de 6h
        g["tendencia_umidade_6h"] = (g["umidade_solo_pct"]
                                     - g["umidade_solo_pct"].rolling("6h").apply(lambda x: x[0], raw=True)).round(1)
        g["chuva_24h_mm"] = g["precipitacao_mm"].rolling("24h").sum().round(1)
        g["temp_max_24h"] = g["temperatura_c"].rolling("24h").max()
        g["temp_min_24h"] = g["temperatura_c"].rolling("24h").min()
        partes.append(g.reset_index())

    df = pd.concat(partes, ignore_index=True)
    df["data"] = df["timestamp"].dt.date.astype(str)
    df["hora"] = df["timestamp"].dt.hour
    df["periodo_dia"] = df["hora"].map(periodo_do_dia)
    df["praga_presente"] = (df["praga_detectada"] != "nenhuma").astype(int)
    return df


def resumo_diario(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(["talhao_id", "data"])
              .agg(temp_media=("temperatura_c", "mean"),
                   temp_max=("temperatura_c", "max"),
                   temp_min=("temperatura_c", "min"),
                   umidade_media=("umidade_solo_pct", "mean"),
                   umidade_min=("umidade_solo_pct", "min"),
                   luminosidade_media=("luminosidade_pct", "mean"),
                   chuva_total_mm=("precipitacao_mm", "sum"),
                   eventos_movimento=("movimento_detectado", "sum"),
                   folhas_doentes_max=("perc_folhas_doentes", "max"),
                   leituras_com_irrigacao=("irrigacao_ligada", "sum"),
                   leituras=("timestamp", "count"))
              .round(1)
              .reset_index())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inicio-tinkercad", default="2026-10-04 12:00:00",
                        help="data/hora que corresponde ao millis=0 da captura do TinkerCad")
    args = parser.parse_args()

    campo = carregar_sensores_campo()
    tinkercad = carregar_tinkercad(args.inicio_tinkercad)
    bruto = pd.concat([campo, tinkercad], ignore_index=True)
    total_bruto = len(bruto)

    df = padronizar(bruto)
    antes = len(df)
    df = df.drop_duplicates(subset=["talhao_id", "timestamp"])
    duplicadas = antes - len(df)

    df, rejeitados = separar_invalidos(df)
    df = imputar_ausentes(df)
    df = criar_features(df)
    df = df.sort_values(["talhao_id", "timestamp"]).reset_index(drop=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "leituras_processadas.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    rejeitados.to_csv(PROCESSED_DIR / "rejeitados.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    diario = resumo_diario(df)
    diario.to_csv(PROCESSED_DIR / "resumo_diario.csv", index=False)

    qualidade = {
        "linhas_recebidas": total_bruto,
        "linhas_por_fonte": bruto["fonte"].value_counts().to_dict(),
        "duplicadas_removidas": int(duplicadas),
        "rejeitadas_fora_da_faixa": int(len(rejeitados)),
        "linhas_com_valor_imputado": int(df["valor_imputado"].sum()),
        "linhas_processadas": int(len(df)),
        "talhoes": sorted(df["talhao_id"].unique().tolist()),
        "periodo": [str(df["timestamp"].min()), str(df["timestamp"].max())],
    }
    with open(PROCESSED_DIR / "qualidade_dados.json", "w", encoding="utf-8") as f:
        json.dump(qualidade, f, ensure_ascii=False, indent=2)

    print(f"[processamento] {total_bruto} linhas recebidas "
          f"({', '.join(f'{k}: {v}' for k, v in qualidade['linhas_por_fonte'].items())})")
    print(f"[processamento] {duplicadas} duplicadas removidas")
    print(f"[processamento] {len(rejeitados)} rejeitadas por valor impossível -> processed/rejeitados.csv")
    print(f"[processamento] {qualidade['linhas_com_valor_imputado']} linhas com campo vazio imputado por interpolação")
    print(f"[processamento] {len(df)} linhas válidas -> processed/leituras_processadas.csv")
    print(f"[processamento] {len(diario)} linhas de resumo diário -> processed/resumo_diario.csv")


if __name__ == "__main__":
    main()
