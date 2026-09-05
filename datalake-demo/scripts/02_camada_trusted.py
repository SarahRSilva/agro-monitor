"""
02_camada_trusted.py
Le tudo que esta na camada Raw, valida (schema + faixas plausiveis),
deduplica e normaliza para um schema unico, gravando na camada Trusted em
formato JSON Lines. Registros invalidos NAO sao descartados: vao para
raw/rejeitados/ com o motivo da rejeicao, para auditoria (conforme descrito
em ingestion/ingestion_flow.md).

Uso:
    python scripts/02_camada_trusted.py
"""
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "datalake" / "raw"
TRUSTED_DIR = BASE_DIR / "datalake" / "trusted"
REJEITADOS_DIR = RAW_DIR / "rejeitados"

FAIXAS_VALIDAS = {
    "umidade_solo_pct": (0, 100),
    "temperatura_c": (-10, 55),
    "ph_solo": (0, 14),
}


def validar_leitura_solo(linha: dict):
    """Retorna (valido: bool, motivo: str|None)."""
    for campo, (minimo, maximo) in FAIXAS_VALIDAS.items():
        try:
            valor = float(linha[campo])
        except (KeyError, ValueError):
            return False, f"campo '{campo}' ausente ou nao numerico"
        if not (minimo <= valor <= maximo):
            return False, f"campo '{campo}'={valor} fora da faixa [{minimo}, {maximo}]"
    return True, None


def processar_leituras_solo():
    registros_validos = []
    registros_rejeitados = []
    chaves_vistas = set()

    csvs = sorted(RAW_DIR.glob("leituras_solo/**/*.csv"))
    for caminho in csvs:
        with open(caminho, newline="", encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                chave = (linha["talhao_id"], linha["data"], linha["hora"])
                if chave in chaves_vistas:
                    continue  # deduplicacao
                chaves_vistas.add(chave)

                valido, motivo = validar_leitura_solo(linha)
                if not valido:
                    linha_rejeitada = dict(linha)
                    linha_rejeitada["motivo_rejeicao"] = motivo
                    linha_rejeitada["arquivo_origem"] = str(caminho.relative_to(BASE_DIR))
                    registros_rejeitados.append(linha_rejeitada)
                    continue

                registros_validos.append({
                    "talhao_id": linha["talhao_id"],
                    "timestamp": f"{linha['data']}T{linha['hora']}:00",
                    "umidade_solo_pct": float(linha["umidade_solo_pct"]),
                    "temperatura_c": float(linha["temperatura_c"]),
                    "ph_solo": float(linha["ph_solo"]),
                    "precipitacao_mm": float(linha.get("precipitacao_mm", 0.0)),
                    "fonte": "leituras_solo",
                })

    TRUSTED_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRUSTED_DIR / "leituras_solo.jsonl", "w", encoding="utf-8") as f:
        for registro in sorted(registros_validos, key=lambda r: (r["talhao_id"], r["timestamp"])):
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    if registros_rejeitados:
        REJEITADOS_DIR.mkdir(parents=True, exist_ok=True)
        with open(REJEITADOS_DIR / "leituras_solo_rejeitadas.csv", "w", newline="", encoding="utf-8") as f:
            campos = list(registros_rejeitados[0].keys())
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(registros_rejeitados)

    print(f"[trusted] {len(registros_validos)} leituras de solo validas")
    print(f"[trusted] {len(registros_rejeitados)} leituras de solo rejeitadas -> raw/rejeitados/")
    return registros_validos, registros_rejeitados


def processar_leituras_sensor_kafka():
    registros = []
    for caminho in sorted(RAW_DIR.glob("sensores/**/*.json")):
        with open(caminho, encoding="utf-8") as f:
            dado = json.load(f)
        leituras = dado.get("leituras", {})
        linha_equivalente = {
            "umidade_solo_pct": leituras.get("umidade_solo_pct"),
            "temperatura_c": leituras.get("temperatura_c"),
            "ph_solo": leituras.get("ph_solo"),
        }
        valido, motivo = validar_leitura_solo(linha_equivalente)
        if not valido:
            print(f"[trusted] leitura de sensor rejeitada ({caminho.name}): {motivo}")
            continue
        registros.append({
            "talhao_id": dado["talhao_id"],
            "timestamp": dado["timestamp"],
            "umidade_solo_pct": leituras.get("umidade_solo_pct"),
            "temperatura_c": leituras.get("temperatura_c"),
            "ph_solo": leituras.get("ph_solo"),
            "precipitacao_mm": 0.0,
            "fonte": "sensor_kafka",
        })

    if registros:
        with open(TRUSTED_DIR / "leituras_solo.jsonl", "a", encoding="utf-8") as f:
            for registro in registros:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"[trusted] {len(registros)} leituras de sensor (Kafka) validas")
    return registros


def processar_deteccoes_imagem():
    registros = []
    for caminho in sorted(RAW_DIR.glob("imagens/**/*.json")):
        with open(caminho, encoding="utf-8") as f:
            dado = json.load(f)
        for deteccao in dado.get("deteccoes", []):
            confianca = deteccao.get("confianca", 0)
            if not (0 <= confianca <= 1):
                print(f"[trusted] deteccao rejeitada ({caminho.name}): confianca fora de [0,1]")
                continue
            registros.append({
                "talhao_id": dado["talhao_id"],
                "timestamp": dado["timestamp_captura"],
                "classe": deteccao["classe"],
                "confianca": confianca,
                "imagem_id": dado["imagem_id"],
                "fonte": "visao_computacional",
            })

    TRUSTED_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRUSTED_DIR / "deteccoes_imagem.jsonl", "w", encoding="utf-8") as f:
        for registro in registros:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"[trusted] {len(registros)} deteccoes de imagem validas")
    return registros


if __name__ == "__main__":
    processar_leituras_solo()
    processar_leituras_sensor_kafka()
    processar_deteccoes_imagem()
    print("\nCamada TRUSTED gravada em datalake/trusted/")
