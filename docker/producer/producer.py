"""
producer.py — Simulador de sensores agrícolas.

Gera leituras sintéticas a cada N segundos e as publica no tópico
Kafka 'sensor-readings' como JSON. Equivale ao gerador.py original,
mas em vez de salvar CSV, envia mensagens ao broker Kafka.
"""

import json
import os
import random
import time
from datetime import datetime

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC     = os.getenv("KAFKA_TOPIC", "sensor-readings")
INTERVALO = int(os.getenv("INTERVALO_SEGUNDOS", "5"))

TALHOES = ["T-01", "T-02", "T-03", "T-04", "T-05"]
PRAGAS  = ["nenhuma", "nenhuma", "nenhuma", "pulgao", "lagarta", "acaro"]
IRRIGS  = ["baixo", "medio", "alto"]


def gerar_leitura() -> dict:
    return {
        "timestamp":          datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "talhao_id":          random.choice(TALHOES),
        "perc_folhas_doentes": round(random.uniform(0, 60), 2),
        "praga_detectada":    random.choice(PRAGAS),
        "umidade_solo_pct":   round(random.uniform(10, 80), 2),
        "temperatura_c":      round(random.uniform(8, 42), 2),
        "nivel_irrigacao":    random.choice(IRRIGS),
    }


def conectar(retries: int = 15, delay: int = 5) -> KafkaProducer:
    for tentativa in range(1, retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            print(f"[PRODUCER] Conectado ao Kafka em {BOOTSTRAP}")
            return producer
        except NoBrokersAvailable:
            print(f"[PRODUCER] Broker indisponível. Tentativa {tentativa}/{retries}. Aguardando {delay}s...")
            time.sleep(delay)
    raise RuntimeError("Não foi possível conectar ao Kafka após várias tentativas.")


if __name__ == "__main__":
    producer = conectar()
    print(f"[PRODUCER] Publicando no tópico '{TOPIC}' a cada {INTERVALO}s")

    while True:
        leitura = gerar_leitura()
        producer.send(TOPIC, leitura)
        producer.flush()
        print(f"[PRODUCER] Enviado: {leitura['talhao_id']} | temp={leitura['temperatura_c']}°C | umid={leitura['umidade_solo_pct']}%")
        time.sleep(INTERVALO)
