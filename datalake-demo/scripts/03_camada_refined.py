"""
03_camada_refined.py
Le a camada Trusted e produz, por talhao, um resumo agregado pronto para
consumo (dashboard, ML ou IA Generativa): medias recentes, tendencia,
deteccoes de pragas relevantes e alertas de deficit hidrico. Este e o
"contrato de dados" que a IA Generativa (etapa 04) consome.

Uso:
    python scripts/03_camada_refined.py
"""
import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TRUSTED_DIR = BASE_DIR / "datalake" / "trusted"
REFINED_DIR = BASE_DIR / "datalake" / "refined"

LIMIAR_DEFICIT_HIDRICO_PCT = 40.0
CONFIANCA_MINIMA_ALERTA_PRAGA = 0.7

# Classes de deteccao que NAO representam problema (nao devem virar alerta,
# mesmo com confianca alta) — ex.: uma folha classificada como saudavel.
CLASSES_SEM_ALERTA = {"folha_saudavel"}

# Previsao de precipitacao simulada (em um cenario real viria de uma API de
# clima ingerida na camada Raw). Mantida fixa aqui apenas para a demo.
PREVISAO_PRECIPITACAO_3D_MM = {"TAL-07": 0.0, "TAL-12": 4.0}


def carregar_jsonl(caminho: Path):
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def calcular_tendencia(valores_ordenados):
    """Compara a media da primeira metade da serie com a da segunda metade."""
    if len(valores_ordenados) < 2:
        return "dados insuficientes"
    metade = len(valores_ordenados) // 2
    primeira = statistics.mean(valores_ordenados[:metade])
    segunda = statistics.mean(valores_ordenados[metade:])
    diferenca = segunda - primeira
    if diferenca <= -3:
        return "queda"
    if diferenca >= 3:
        return "alta"
    return "estavel"


def montar_resumo_por_talhao():
    leituras = carregar_jsonl(TRUSTED_DIR / "leituras_solo.jsonl")
    deteccoes = carregar_jsonl(TRUSTED_DIR / "deteccoes_imagem.jsonl")

    por_talhao = defaultdict(list)
    for leitura in leituras:
        por_talhao[leitura["talhao_id"]].append(leitura)

    deteccoes_por_talhao = defaultdict(list)
    for deteccao in deteccoes:
        deteccoes_por_talhao[deteccao["talhao_id"]].append(deteccao)

    resumo = {}
    for talhao_id, itens in por_talhao.items():
        itens.sort(key=lambda x: x["timestamp"])
        umidades = [i["umidade_solo_pct"] for i in itens]
        temperaturas = [i["temperatura_c"] for i in itens]
        ultima_leitura = itens[-1]

        alertas = []
        if ultima_leitura["umidade_solo_pct"] < LIMIAR_DEFICIT_HIDRICO_PCT:
            alertas.append({
                "tipo": "deficit_hidrico",
                "prioridade": "alta",
                "detalhe": f"umidade atual {ultima_leitura['umidade_solo_pct']}%, abaixo do limiar de {LIMIAR_DEFICIT_HIDRICO_PCT}%",
            })

        pragas_relevantes = [
            d for d in deteccoes_por_talhao.get(talhao_id, [])
            if d["confianca"] >= CONFIANCA_MINIMA_ALERTA_PRAGA
            and d["classe"] not in CLASSES_SEM_ALERTA
        ]
        for praga in pragas_relevantes:
            alertas.append({
                "tipo": "deteccao_praga",
                "prioridade": "media",
                "detalhe": f"{praga['classe']} detectada com confianca {praga['confianca']:.0%}",
            })

        resumo[talhao_id] = {
            "talhao_id": talhao_id,
            "periodo_analisado": {
                "inicio": itens[0]["timestamp"],
                "fim": itens[-1]["timestamp"],
                "total_leituras": len(itens),
            },
            "umidade_solo_pct": {
                "atual": ultima_leitura["umidade_solo_pct"],
                "media_periodo": round(statistics.mean(umidades), 1),
                "tendencia": calcular_tendencia(umidades),
            },
            "temperatura_c": {
                "atual": ultima_leitura["temperatura_c"],
                "media_periodo": round(statistics.mean(temperaturas), 1),
            },
            "ph_solo": ultima_leitura["ph_solo"],
            "previsao_precipitacao_3d_mm": PREVISAO_PRECIPITACAO_3D_MM.get(talhao_id, 0.0),
            "deteccoes_imagem_relevantes": pragas_relevantes,
            "alertas": alertas,
            "gerado_em": datetime.now().isoformat(timespec="seconds"),
        }

    return resumo


if __name__ == "__main__":
    resumo = montar_resumo_por_talhao()
    REFINED_DIR.mkdir(parents=True, exist_ok=True)
    caminho_saida = REFINED_DIR / "resumo_talhoes.json"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    print(f"[refined] resumo de {len(resumo)} talhao(oes) gravado em {caminho_saida}")
    for talhao_id, dados in resumo.items():
        n_alertas = len(dados["alertas"])
        print(f"  - {talhao_id}: umidade atual {dados['umidade_solo_pct']['atual']}% "
              f"(tendencia: {dados['umidade_solo_pct']['tendencia']}), {n_alertas} alerta(s)")
