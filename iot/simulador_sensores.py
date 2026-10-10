"""
simulador_sensores.py
Gera o histórico de leituras dos sensores de campo do AgroSmart em escala
(vários talhões, vários dias), no mesmo formato de colunas que a estação
TinkerCad (agrosmart_tinkercad.ino) envia pela serial, acrescido dos dados
da câmera de visão computacional (folhas doentes / praga detectada) e do
pluviômetro.

Cada talhão tem um cenário, para que a automação tenha situações reais a
interpretar:
  TAL-01  normal, irrigação funcionando        (contraste, poucos alertas)
  TAL-02  seca progressiva, irrigação quebrada (déficit hídrico)
  TAL-03  onda de calor a partir do 4º dia     (estresse térmico)
  TAL-04  infestação de lagarta a partir do 3º dia (praga + folhas doentes)
  TAL-05  noites frias com risco de geada      (frio extremo)

Também injeta DE PROPÓSITO problemas de qualidade de dados para a etapa de
processamento tratar: leituras duplicadas, valores ausentes e valores
impossíveis (falha de sensor).

Uso:
    python iot/simulador_sensores.py                 # 7 dias, leitura a cada 30 min
    python iot/simulador_sensores.py --dias 14 --seed 7
"""
import argparse
import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "dados" / "raw"

INTERVALO_MIN = 30
INICIO = datetime(2026, 9, 28, 0, 0)

COLUNAS = [
    "timestamp", "talhao_id", "sensor_id", "temperatura_c", "umidade_solo_pct",
    "luminosidade_pct", "movimento_detectado", "irrigacao_ligada",
    "precipitacao_mm", "perc_folhas_doentes", "praga_detectada",
]

CENARIOS = {
    "TAL-01": {"irrigacao_ok": True,  "secagem_h": 0.35, "temp_base": 24, "umidade_ini": 55},
    "TAL-02": {"irrigacao_ok": False, "secagem_h": 0.30, "temp_base": 26, "umidade_ini": 56},
    "TAL-03": {"irrigacao_ok": True,  "secagem_h": 0.40, "temp_base": 27, "umidade_ini": 50, "onda_calor_dia": 3},
    "TAL-04": {"irrigacao_ok": True,  "secagem_h": 0.35, "temp_base": 24, "umidade_ini": 54, "praga_dia": 2},
    "TAL-05": {"irrigacao_ok": True,  "secagem_h": 0.30, "temp_base": 15, "umidade_ini": 58, "frio": True},
}

# Chuva prevista no cenário: (dia, hora_inicio, horas, mm/h) — afeta todos os talhões
EVENTOS_CHUVA = [(1, 15, 2, 3.0), (5, 3, 3, 2.0)]


def temperatura_do_momento(cfg, momento, dia):
    hora = momento.hour + momento.minute / 60
    # ciclo diário: mínimo ~5h, máximo ~15h
    amplitude = 9 if cfg.get("frio") else 7
    temp = cfg["temp_base"] + amplitude * math.sin((hora - 9) / 24 * 2 * math.pi)
    if cfg.get("onda_calor_dia") is not None and dia >= cfg["onda_calor_dia"]:
        temp += 9
    if cfg.get("frio") and (hora < 7 or hora > 22):
        temp -= 6
    return temp + random.gauss(0, 0.6)


def luminosidade_do_momento(momento, chovendo):
    hora = momento.hour + momento.minute / 60
    if hora < 6 or hora > 18.5:
        luz = random.uniform(0, 4)
    else:
        luz = 100 * math.sin((hora - 6) / 12.5 * math.pi)
    if chovendo:
        luz *= 0.35
    return max(0.0, min(100.0, luz + random.gauss(0, 2)))


def chuva_do_momento(momento, dia):
    for dia_chuva, hora_ini, horas, mm_h in EVENTOS_CHUVA:
        if dia == dia_chuva and hora_ini <= momento.hour < hora_ini + horas:
            return mm_h * INTERVALO_MIN / 60
    return 0.0


def simular_talhao(talhao_id, cfg, total_leituras):
    linhas = []
    umidade = cfg["umidade_ini"]
    irrigando = False
    folhas_doentes = random.uniform(2, 6)
    sensor_id = f"SNS-{talhao_id[-2:]}"

    for i in range(total_leituras):
        momento = INICIO + timedelta(minutes=INTERVALO_MIN * i)
        dia = (momento - INICIO).days
        chuva = chuva_do_momento(momento, dia)
        temp = temperatura_do_momento(cfg, momento, dia)
        luz = luminosidade_do_momento(momento, chuva > 0)

        # balanço hídrico do solo: evaporação cresce com temperatura e luz
        evaporacao = cfg["secagem_h"] * (INTERVALO_MIN / 60) * (0.6 + max(temp, 0) / 30 + luz / 200)
        umidade = max(3.0, min(95.0, umidade + chuva * 2.2 - evaporacao + random.gauss(0, 0.4)))

        # irrigação automática do campo (histerese 30% -> 45%), quebrada no TAL-02
        if cfg["irrigacao_ok"]:
            if umidade < 30:
                irrigando = True
            elif umidade > 45:
                irrigando = False
            if irrigando:
                umidade = min(95.0, umidade + 3.0)

        # visão computacional: folhas doentes e praga detectada
        praga = "nenhuma"
        if cfg.get("praga_dia") is not None and dia >= cfg["praga_dia"]:
            folhas_doentes = min(75.0, folhas_doentes + random.uniform(0.15, 0.55))
            praga = "lagarta" if folhas_doentes > 12 else "nenhuma"
        else:
            folhas_doentes = max(0.5, min(12.0, folhas_doentes + random.gauss(0, 0.2)))

        # sensor PIR: movimento esporádico; muito mais frequente com praga/animais
        prob_mov = 0.12 if praga != "nenhuma" else 0.02
        movimento = 1 if random.random() < prob_mov else 0

        linhas.append({
            "timestamp": momento.strftime("%Y-%m-%d %H:%M:%S"),
            "talhao_id": talhao_id,
            "sensor_id": sensor_id,
            "temperatura_c": round(temp, 1),
            "umidade_solo_pct": round(umidade, 1),
            "luminosidade_pct": round(luz, 1),
            "movimento_detectado": movimento,
            "irrigacao_ligada": int(irrigando),
            "precipitacao_mm": round(chuva, 1),
            "perc_folhas_doentes": round(folhas_doentes, 1),
            "praga_detectada": praga,
        })
    return linhas


def injetar_problemas_de_qualidade(linhas):
    """Simula falhas reais de campo para a etapa de processamento tratar."""
    n_dup = n_nulos = n_impossiveis = 0

    for idx in random.sample(range(len(linhas)), 6):  # retransmissões duplicadas
        linhas.append(dict(linhas[idx]))
        n_dup += 1

    for idx in random.sample(range(len(linhas)), 10):  # pacote perdido parcialmente
        campo = random.choice(["temperatura_c", "umidade_solo_pct", "luminosidade_pct"])
        linhas[idx][campo] = ""
        n_nulos += 1

    for idx in random.sample(range(len(linhas)), 5):  # sensor com defeito
        campo, valor = random.choice([("umidade_solo_pct", 137.4), ("temperatura_c", -99.0),
                                      ("temperatura_c", 85.3), ("luminosidade_pct", -12.0)])
        linhas[idx][campo] = valor
        n_impossiveis += 1

    random.shuffle(linhas)  # mensagens chegam fora de ordem, como em um broker real
    return n_dup, n_nulos, n_impossiveis


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dias", type=int, default=7)
    parser.add_argument("--seed", type=int, default=42, help="semente para resultados reproduzíveis")
    args = parser.parse_args()
    random.seed(args.seed)

    total_leituras = args.dias * 24 * 60 // INTERVALO_MIN
    linhas = []
    for talhao_id, cfg in CENARIOS.items():
        linhas.extend(simular_talhao(talhao_id, cfg, total_leituras))
        print(f"[simulador] {talhao_id}: {total_leituras} leituras geradas")

    n_dup, n_nulos, n_impossiveis = injetar_problemas_de_qualidade(linhas)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    caminho = RAW_DIR / "sensores_campo.csv"
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS)
        writer.writeheader()
        writer.writerows(linhas)

    print(f"[simulador] problemas injetados: {n_dup} duplicadas, {n_nulos} campos vazios, "
          f"{n_impossiveis} valores impossíveis")
    print(f"[simulador] {len(linhas)} linhas gravadas em {caminho.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
