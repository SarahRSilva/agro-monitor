"""
pipeline_simulado.py — Simulação do pipeline de streaming do AgroSmart.

Demonstra o fluxo completo de dados sem necessidade de Kafka instalado:
  [Sensores] → [Canal de streaming em memória] → [Motor de Regras] → [Alertas]

Arquitetura baseada em threads + queue.Queue para simular o comportamento
de um tópico Kafka (publish/subscribe assíncrono).

Uso:
    pip install rich
    python pipeline_simulado.py
"""

import json
import queue
import random
import threading
import time
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.columns import Columns
    from rich import box
    USE_RICH = True
except ImportError:
    USE_RICH = False

# ── Configuração ─────────────────────────────────────────────────────────────

INTERVALO_PRODUCER  = 2   # segundos entre leituras
TOPIC_READINGS      = queue.Queue(maxsize=100)  # simula tópico Kafka
TOPIC_ALERTS        = queue.Queue(maxsize=100)  # simula tópico de alertas

TALHOES = ["T-01", "T-02", "T-03", "T-04", "T-05"]
PRAGAS  = ["nenhuma", "nenhuma", "nenhuma", "pulgao", "lagarta", "acaro"]
IRRIGS  = ["baixo", "medio", "alto"]

leituras_log: list[dict] = []
alertas_log:  list[dict] = []
stats = {"produzidas": 0, "consumidas": 0, "alertas": 0}
lock = threading.Lock()

console = Console() if USE_RICH else None


# ── Producer (simula sensores) ────────────────────────────────────────────────

def gerar_leitura() -> dict:
    return {
        "timestamp":           datetime.now().strftime("%H:%M:%S"),
        "talhao_id":           random.choice(TALHOES),
        "perc_folhas_doentes": round(random.uniform(0, 60), 1),
        "praga_detectada":     random.choice(PRAGAS),
        "umidade_solo_pct":    round(random.uniform(10, 80), 1),
        "temperatura_c":       round(random.uniform(8, 42), 1),
        "nivel_irrigacao":     random.choice(IRRIGS),
    }


def producer():
    """Thread: gera leituras e publica no 'tópico' (Queue)."""
    while True:
        leitura = gerar_leitura()
        try:
            TOPIC_READINGS.put_nowait(leitura)
            with lock:
                leituras_log.insert(0, leitura)
                leituras_log[:] = leituras_log[:15]
                stats["produzidas"] += 1
        except queue.Full:
            pass  # descarta se o tópico estiver cheio (backpressure simulado)
        time.sleep(INTERVALO_PRODUCER)


# ── Consumer / Motor de Regras ────────────────────────────────────────────────

def avaliar_regras(leitura: dict) -> list[dict]:
    alertas = []

    # Regra 1: INFESTAÇÃO (AND)
    if leitura["perc_folhas_doentes"] > 30 and leitura["praga_detectada"] != "nenhuma":
        alertas.append({
            "nivel": "CRÍTICO", "icone": "🚨",
            "regra": "INFESTAÇÃO",
            "talhao_id": leitura["talhao_id"],
            "timestamp": leitura["timestamp"],
            "detalhe": f"Folhas {leitura['perc_folhas_doentes']}% | Praga: {leitura['praga_detectada']}",
        })

    # Regra 2: IRRIGAÇÃO (AND)
    if leitura["umidade_solo_pct"] < 30 and leitura["nivel_irrigacao"] == "baixo":
        alertas.append({
            "nivel": "ATENÇÃO", "icone": "💧",
            "regra": "IRRIGAÇÃO",
            "talhao_id": leitura["talhao_id"],
            "timestamp": leitura["timestamp"],
            "detalhe": f"Umidade {leitura['umidade_solo_pct']}% | Irrigação: {leitura['nivel_irrigacao']}",
        })

    # Regra 3: TEMPERATURA (OR)
    if leitura["temperatura_c"] > 35 or leitura["temperatura_c"] < 12:
        extremo = "ALTA" if leitura["temperatura_c"] > 35 else "BAIXA"
        alertas.append({
            "nivel": "AVISO", "icone": "🌡",
            "regra": f"TEMP {extremo}",
            "talhao_id": leitura["talhao_id"],
            "timestamp": leitura["timestamp"],
            "detalhe": f"Temperatura: {leitura['temperatura_c']}°C",
        })

    return alertas


def rules_engine():
    """Thread: consome leituras, aplica regras e publica alertas."""
    while True:
        try:
            leitura = TOPIC_READINGS.get(timeout=1)
            with lock:
                stats["consumidas"] += 1

            alertas = avaliar_regras(leitura)
            for alerta in alertas:
                TOPIC_ALERTS.put_nowait(alerta)
                with lock:
                    alertas_log.insert(0, alerta)
                    alertas_log[:] = alertas_log[:10]
                    stats["alertas"] += 1

        except queue.Empty:
            continue


# ── Display simples (sem rich) ────────────────────────────────────────────────

def display_simples():
    while True:
        print("\n" + "="*70)
        print(f"  🌱 AGROSMART PIPELINE | {datetime.now().strftime('%H:%M:%S')}")
        print(f"  Produzidas: {stats['produzidas']} | Consumidas: {stats['consumidas']} | Alertas: {stats['alertas']}")
        print("-"*70)

        if leituras_log:
            l = leituras_log[0]
            print(f"  Última leitura: {l['talhao_id']} | {l['temperatura_c']}°C | umid={l['umidade_solo_pct']}% | praga={l['praga_detectada']}")

        if alertas_log:
            print("\n  ALERTAS RECENTES:")
            for a in alertas_log[:3]:
                print(f"    [{a['nivel']}] {a['icone']} {a['regra']} — Talhão {a['talhao_id']} | {a['detalhe']}")
        else:
            print("\n  ✅ Sem alertas no momento")

        time.sleep(3)


# ── Display rich ─────────────────────────────────────────────────────────────

def display_rich():
    with Live(refresh_per_second=2, screen=True) as live:
        while True:
            with lock:
                s = dict(stats)
                lr = list(leituras_log)
                al = list(alertas_log)

            # Tabela de leituras
            t_leit = Table(title="📡 Últimas Leituras (tópico: sensor-readings)", box=box.ROUNDED, style="green")
            t_leit.add_column("Hora", style="dim")
            t_leit.add_column("Talhão", style="bold")
            t_leit.add_column("Folhas%")
            t_leit.add_column("Praga")
            t_leit.add_column("Umid%")
            t_leit.add_column("Temp°C")
            t_leit.add_column("Irrigação")

            for l in lr[:10]:
                praga_style = "red" if l["praga_detectada"] != "nenhuma" else "green"
                t_leit.add_row(
                    l["timestamp"], l["talhao_id"],
                    str(l["perc_folhas_doentes"]),
                    f"[{praga_style}]{l['praga_detectada']}[/{praga_style}]",
                    str(l["umidade_solo_pct"]),
                    str(l["temperatura_c"]),
                    l["nivel_irrigacao"],
                )

            # Tabela de alertas
            t_alrt = Table(title="🚨 Alertas (tópico: alerts)", box=box.ROUNDED, style="red")
            t_alrt.add_column("Hora", style="dim")
            t_alrt.add_column("Nível")
            t_alrt.add_column("Regra")
            t_alrt.add_column("Talhão")
            t_alrt.add_column("Detalhe")

            nivel_colors = {"CRÍTICO": "red bold", "ATENÇÃO": "yellow bold", "AVISO": "blue"}
            for a in al[:8]:
                cor = nivel_colors.get(a["nivel"], "white")
                t_alrt.add_row(
                    a["timestamp"],
                    f"[{cor}]{a['icone']} {a['nivel']}[/{cor}]",
                    a["regra"], a["talhao_id"], a["detalhe"],
                )

            # Stats
            header = Panel(
                f"[green]● PIPELINE ATIVO[/green]  |  "
                f"Produzidas: [cyan]{s['produzidas']}[/cyan]  |  "
                f"Consumidas: [cyan]{s['consumidas']}[/cyan]  |  "
                f"Alertas gerados: [red]{s['alertas']}[/red]  |  "
                f"Fila readings: [yellow]{TOPIC_READINGS.qsize()}[/yellow]  |  "
                f"Fila alerts: [yellow]{TOPIC_ALERTS.qsize()}[/yellow]",
                title="🌱 AgroSmart — Pipeline de Streaming",
            )

            live.update(Columns([Panel(header), t_leit, t_alrt]))
            time.sleep(0.5)


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🌱 Iniciando pipeline de streaming AgroSmart...")
    print(f"   Producer: gerando leituras a cada {INTERVALO_PRODUCER}s")
    print("   Rules Engine: escutando tópico 'sensor-readings'")
    print("   Ctrl+C para encerrar\n")

    # Inicia threads
    threading.Thread(target=producer,      daemon=True, name="Producer").start()
    threading.Thread(target=rules_engine,  daemon=True, name="RulesEngine").start()

    time.sleep(1)  # aguarda primeira leitura

    if USE_RICH:
        display_rich()
    else:
        print("[INFO] 'rich' não instalado. Usando exibição simples.")
        print("[INFO] Execute: pip install rich  para visual aprimorado\n")
        display_simples()
