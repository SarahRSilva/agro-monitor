"""
04_ia_generativa.py
Le o resumo da camada Refined e gera, para cada talhao, um relatorio de
apoio a decisao em linguagem natural — o mesmo tipo de saida descrito em
ia-generativa/decision_support.md.

Por padrao roda em modo SIMULADO (sem nenhuma dependencia externa, sem
custo e sem precisar de internet), com uma funcao baseada em regras que
imita a estrutura de saida de um LLM.

Se a variavel de ambiente ANTHROPIC_API_KEY estiver definida e o pacote
`anthropic` estiver instalado (pip install anthropic), o script usa a API
de verdade, mandando o mesmo contexto estruturado para o modelo.

Uso:
    python scripts/04_ia_generativa.py
    python scripts/04_ia_generativa.py --talhao TAL-07
    python scripts/04_ia_generativa.py --real   # forca uso da API real
"""
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REFINED_DIR = BASE_DIR / "datalake" / "refined"
RELATORIOS_DIR = REFINED_DIR / "relatorios_ia"


def montar_prompt(contexto: dict) -> str:
    talhao = contexto["talhao_id"]
    umid = contexto["umidade_solo_pct"]
    temp = contexto["temperatura_c"]
    chuva = contexto["previsao_precipitacao_3d_mm"]
    pragas = contexto["deteccoes_imagem_relevantes"]

    linhas_pragas = "\n".join(
        f"- {p['classe']} (confianca {p['confianca']:.0%})" for p in pragas
    ) or "- nenhuma deteccao relevante no periodo"

    return f"""Voce e um assistente agronomico. Com base APENAS nos dados abaixo do
Talhao {talhao}, gere um relatorio curto com: (1) situacao atual, (2) riscos
identificados, (3) recomendacao priorizada. Nao invente dados que nao
estejam no contexto.

Dados:
- Umidade do solo atual: {umid['atual']}% (media do periodo: {umid['media_periodo']}%, tendencia: {umid['tendencia']})
- Temperatura atual: {temp['atual']} C (media do periodo: {temp['media_periodo']} C)
- pH do solo: {contexto['ph_solo']}
- Previsao de precipitacao (proximos 3 dias): {chuva} mm
- Deteccoes de imagem relevantes:
{linhas_pragas}
"""


def gerar_relatorio_simulado(contexto: dict) -> str:
    """Gera o relatorio com um motor de regras local (sem chamar nenhuma API)."""
    talhao = contexto["talhao_id"]
    umid = contexto["umidade_solo_pct"]
    chuva = contexto["previsao_precipitacao_3d_mm"]
    pragas = contexto["deteccoes_imagem_relevantes"]
    agora = datetime.now().strftime("%d/%m/%Y, %Hh%M")

    situacao = (
        f"A umidade do solo esta em {umid['atual']}%, com tendencia de "
        f"**{umid['tendencia']}** no periodo analisado, e previsao de "
        f"{chuva:.0f}mm de chuva para os proximos 3 dias. A temperatura "
        f"media do periodo foi de {contexto['temperatura_c']['media_periodo']}C "
        f"e o pH do solo esta em {contexto['ph_solo']}."
    )

    riscos = []
    recomendacoes = []

    if umid["atual"] < 40 and umid["tendencia"] in ("queda", "estavel"):
        riscos.append(
            "1. **Deficit hidrico (alta prioridade)** — a umidade atual esta "
            f"abaixo do limiar seguro de 40% e a tendencia e de {umid['tendencia']}, "
            "com pouca ou nenhuma chuva prevista."
        )
        recomendacoes.append(
            f"Programar irrigacao suplementar no Talhao {talhao} nas proximas 24h, "
            "visando restabelecer a umidade para a faixa de 45-55%."
        )
    elif umid["tendencia"] == "queda":
        riscos.append(
            "1. **Queda de umidade em observacao (media prioridade)** — a tendencia "
            "e de queda, mas ainda dentro de faixa segura; acompanhar nos proximos dias."
        )
        recomendacoes.append(
            f"Monitorar o Talhao {talhao} diariamente e preparar irrigacao preventiva "
            "caso a tendencia de queda continue."
        )
    else:
        riscos.append("1. Nenhum risco hidrico relevante identificado no periodo.")

    if pragas:
        nomes = ", ".join(sorted({p["classe"] for p in pragas}))
        riscos.append(
            f"{len(riscos)+1}. **Praga em observacao (media prioridade)** — foi "
            f"detectada a presenca de {nomes}; recomenda-se inspecao visual antes "
            "de decidir por controle quimico ou biologico."
        )
        recomendacoes.append(
            f"Enviar equipe de campo para inspecao pontual da area do Talhao {talhao} "
            "onde a praga foi detectada, antes de aplicar qualquer defensivo."
        )
    else:
        riscos.append(f"{len(riscos)+1}. Nenhuma deteccao de praga relevante no periodo.")

    recomendacoes.append(f"Reavaliar a situacao do Talhao {talhao} em 48h com base em novas leituras.")

    recomendacoes_fmt = "\n".join(f"{i+1}. {r}" for i, r in enumerate(recomendacoes))
    riscos_fmt = "\n".join(riscos)

    return f"""**Relatorio de Apoio a Decisao — Talhao {talhao} — {agora}**

**Situacao atual:** {situacao}

**Riscos identificados:**
{riscos_fmt}

**Recomendacao priorizada:**
{recomendacoes_fmt}

*Relatorio gerado automaticamente a partir de dados da camada Refinada do Data Lake AgroSmart.
Decisao final cabe ao responsavel tecnico do talhao.*
"""


def gerar_relatorio_llm_real(prompt: str) -> str:
    """Chama a API da Anthropic de verdade. So e usada se --real for passado
    e ANTHROPIC_API_KEY estiver configurada."""
    from anthropic import Anthropic  # import tardio: so exige a lib se for usada

    client = Anthropic()  # le ANTHROPIC_API_KEY do ambiente
    resposta = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return resposta.content[0].text


def gerar_relatorio(contexto: dict, usar_api_real: bool) -> str:
    prompt = montar_prompt(contexto)
    if usar_api_real:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("[ia] ANTHROPIC_API_KEY nao definida — usando modo simulado.")
            return gerar_relatorio_simulado(contexto)
        try:
            return gerar_relatorio_llm_real(prompt)
        except ImportError:
            print("[ia] pacote 'anthropic' nao instalado (pip install anthropic) — usando modo simulado.")
            return gerar_relatorio_simulado(contexto)
    return gerar_relatorio_simulado(contexto)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--talhao", help="gerar relatorio apenas para este talhao (ex: TAL-07)")
    parser.add_argument("--real", action="store_true", help="usar a API real da Anthropic em vez do modo simulado")
    args = parser.parse_args()

    with open(REFINED_DIR / "resumo_talhoes.json", encoding="utf-8") as f:
        resumo_talhoes = json.load(f)

    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    talhoes_para_processar = [args.talhao] if args.talhao else list(resumo_talhoes.keys())

    for talhao_id in talhoes_para_processar:
        contexto = resumo_talhoes[talhao_id]
        relatorio = gerar_relatorio(contexto, usar_api_real=args.real)

        data_str = datetime.now().strftime("%Y-%m-%d")
        caminho_saida = RELATORIOS_DIR / f"{talhao_id}_{data_str}.md"
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(relatorio)

        print("=" * 70)
        print(relatorio)
        print(f"[ia] relatorio salvo em {caminho_saida}")
