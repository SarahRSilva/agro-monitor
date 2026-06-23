"""
consumer.py — Motor de Regras do AgroSmart.

Consome mensagens do tópico Kafka 'sensor-readings', aplica as três
regras booleanas (INFESTAÇÃO, IRRIGAÇÃO, TEMPERATURA) e publica
alertas no tópico 'alerts'. Mantém uma janela deslizante das últimas
50 leituras em memória para avaliação contínua.
"""

import json
import os
import time
from collections import deque
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable

BOOTSTRAP  = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_IN   = os.getenv("KAFKA_TOPIC_IN", "sensor-readings")
TOPIC_OUT  = os.getenv("KAFKA_TOPIC_OUT", "alerts")
JANELA     = 50  # tamanho da janela deslizante

# Janela deslizante em memória
janela: deque = deque(maxlen=JANELA)


# ── Regras booleanas ────────────────────────────────────────────────────────

def verificar_infestacao(leitura: dict) -> dict | None:
    """INFESTAÇÃO: perc_folhas_doentes > 30 AND praga_detectada != 'nenhuma'"""
    if leitura["perc_folhas_doentes"] > 30 and leitura["praga_detectada"] != "nenhuma":
        return {
            "regra": "INFESTAÇÃO",
            "nivel": "CRÍTICO",
            "icone": "🚨",
            "talhao_id": leitura["talhao_id"],
            "timestamp": leitura["timestamp"],
            "detalhe": (
                f"Folhas doentes: {leitura['perc_folhas_doentes']:.1f}% | "
                f"Praga: {leitura['praga_detectada']}"
            ),
            "recomendacoes": [
                "Isolar o talhão afetado imediatamente",
                "Acionar equipe de controle fitossanitário",
                "Aplicar defensivo agrícola aprovado para a praga identificada",
                "Registrar ocorrência no sistema de gestão",
            ],
            "acoes_automaticas": [
                "Talhão marcado para monitoramento intensivo",
                "Notificação enviada ao agrônomo responsável",
                "Alerta registrado no histórico do sistema",
            ],
        }
    return None


def verificar_irrigacao(leitura: dict) -> dict | None:
    """IRRIGAÇÃO: umidade_solo_pct < 30 AND nivel_irrigacao == 'baixo'"""
    if leitura["umidade_solo_pct"] < 30 and leitura["nivel_irrigacao"] == "baixo":
        return {
            "regra": "IRRIGAÇÃO",
            "nivel": "ATENÇÃO",
            "icone": "💧",
            "talhao_id": leitura["talhao_id"],
            "timestamp": leitura["timestamp"],
            "detalhe": (
                f"Umidade: {leitura['umidade_solo_pct']:.1f}% | "
                f"Irrigação: {leitura['nivel_irrigacao']}"
            ),
            "recomendacoes": [
                "Verificar sistema de irrigação do talhão",
                "Aumentar nível de irrigação para 'alto' imediatamente",
                "Monitorar umidade nas próximas 2 horas",
                "Avaliar possível falha no sistema de irrigação",
            ],
            "acoes_automaticas": [
                "Solicitação de irrigação emergencial criada",
                "Notificação enviada à equipe de manutenção",
                "Frequência de monitoramento aumentada para 1 min",
            ],
        }
    return None


def verificar_temperatura(leitura: dict) -> dict | None:
    """TEMPERATURA: temperatura_c > 35 OR temperatura_c < 12"""
    if leitura["temperatura_c"] > 35 or leitura["temperatura_c"] < 12:
        extremo = "alta" if leitura["temperatura_c"] > 35 else "baixa"
        return {
            "regra": "TEMPERATURA",
            "nivel": "AVISO",
            "icone": "🌡",
            "talhao_id": leitura["talhao_id"],
            "timestamp": leitura["timestamp"],
            "detalhe": f"Temperatura {extremo}: {leitura['temperatura_c']:.1f}°C",
            "recomendacoes": [
                f"Monitorar impacto da temperatura {extremo} nas culturas",
                "Verificar previsão meteorológica para as próximas 24h",
                "Considerar medidas de proteção térmica se tendência persistir",
            ],
            "acoes_automaticas": [
                "Anomalia climática registrada no histórico",
                "Frequência de monitoramento aumentada",
            ],
        }
    return None


def avaliar_regras(leitura: dict) -> list[dict]:
    alertas = []
    for fn in [verificar_infestacao, verificar_irrigacao, verificar_temperatura]:
        alerta = fn(leitura)
        if alerta:
            alertas.append(alerta)
    return alertas


# ── Conexão Kafka ────────────────────────────────────────────────────────────

def conectar_consumer(retries=15, delay=5) -> KafkaConsumer:
    for i in range(1, retries + 1):
        try:
            consumer = KafkaConsumer(
                TOPIC_IN,
                bootstrap_servers=BOOTSTRAP,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                group_id="agro-rules-engine",
            )
            print(f"[RULES-ENGINE] Consumer conectado — escutando '{TOPIC_IN}'")
            return consumer
        except NoBrokersAvailable:
            print(f"[RULES-ENGINE] Broker indisponível. Tentativa {i}/{retries}. Aguardando {delay}s...")
            time.sleep(delay)
    raise RuntimeError("Não foi possível conectar ao Kafka.")


def conectar_producer(retries=15, delay=5) -> KafkaProducer:
    for i in range(1, retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            return producer
        except NoBrokersAvailable:
            time.sleep(delay)
    raise RuntimeError("Não foi possível conectar ao Kafka.")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    consumer = conectar_consumer()
    producer = conectar_producer()

    print(f"[RULES-ENGINE] Publicando alertas em '{TOPIC_OUT}'")

    for msg in consumer:
        leitura = msg.value
        janela.append(leitura)

        alertas = avaliar_regras(leitura)
        for alerta in alertas:
            producer.send(TOPIC_OUT, alerta)
            producer.flush()
            print(f"[RULES-ENGINE] ALERTA [{alerta['nivel']}] {alerta['regra']} — Talhão {alerta['talhao_id']}")

        if not alertas:
            print(f"[RULES-ENGINE] OK — {leitura['talhao_id']} | janela={len(janela)} msgs")
