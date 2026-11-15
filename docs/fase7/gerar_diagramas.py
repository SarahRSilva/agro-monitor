"""
Gera docs/fase7/arquitetura_final.png — diagrama da arquitetura final do AgroSmart (Fase 7).
Feito com matplotlib para não depender de ferramentas externas (Graphviz/Mermaid CLI).

Uso:  python docs/fase7/gerar_diagramas.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "arquitetura_final.png"

CORES = {
    "fonte": "#e3eefa", "proc": "#e6f4ea", "intel": "#fff4dc", "saida": "#f3e8fb",
    "ops": "#eceff1", "dados": "#ffffff", "f4": "#fbe9e7",
}


def caixa(ax, x, y, w, h, titulo, texto="", cor="#ffffff", borda="#37474f", negrito=True, fs=8.5, cilindro=False):
    estilo = "round,pad=0.02,rounding_size=0.12" if not cilindro else "round,pad=0.02,rounding_size=0.35"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=estilo, fc=cor, ec=borda, lw=1.1, zorder=3,
                                linestyle="--" if cilindro else "-"))
    ax.text(x + w / 2, y + h - 0.16, titulo, ha="center", va="top", fontsize=fs + 0.5,
            fontweight="bold" if negrito else "normal", zorder=4)
    if texto:
        ax.text(x + w / 2, y + h - 0.5, texto, ha="center", va="top", fontsize=fs + 0.9, color="#37474f",
                zorder=4, linespacing=1.25)
    return (x, y, w, h)


def grupo(ax, x, y, w, h, titulo, cor):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc=cor, ec="#90a4ae", lw=1, zorder=1))
    ax.text(x + 0.15, y + h - 0.12, titulo, ha="left", va="top", fontsize=10.5, fontweight="bold",
            color="#263238", zorder=2)


def seta(ax, a, b, rotulo="", cor="#455a64", estilo="-|>", rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=13, lw=1.4, color=cor, zorder=2,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls))
    if rotulo:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.12, rotulo, ha="center", va="bottom", fontsize=7,
                color=cor, zorder=5, bbox={"fc": "white", "ec": "none", "alpha": 0.85, "pad": 0.5})


def direita(c):
    return (c[0] + c[2], c[1] + c[3] / 2)


def esquerda(c):
    return (c[0], c[1] + c[3] / 2)


def topo(c):
    return (c[0] + c[2] / 2, c[1] + c[3])


def base(c):
    return (c[0] + c[2] / 2, c[1])


def main():
    fig, ax = plt.subplots(figsize=(22, 13))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 13)
    ax.axis("off")
    ax.text(11, 12.75, "AgroSmart — Arquitetura final da solução (Fase 7)", ha="center", fontsize=17, fontweight="bold")
    ax.text(11, 12.35, "Entrada → Processamento → Automação/Inteligência → Saída, operada por containers, "
            "monitoramento contínuo e pipeline DevSecOps", ha="center", fontsize=10.5, color="#455a64")

    # 1. Entrada
    grupo(ax, 0.2, 4.0, 3.9, 8.0, "1 · ENTRADA (IoT / simulação)", CORES["fonte"])
    ard = caixa(ax, 0.45, 9.6, 3.4, 1.7, "Arduino Uno (TinkerCad)",
                "TMP36 · umidade do solo\nLDR · PIR · automação de borda\n(bomba, LEDs, buzzer) — serial CSV")
    sim = caixa(ax, 0.45, 7.55, 3.4, 1.7, "Simulador de campo",
                "5 talhões × 7 dias · 30 min\ncenários: seca, calor, praga, geada\n+ falhas de qualidade injetadas")
    cam = caixa(ax, 0.45, 5.95, 3.4, 1.25, "Câmera (visão computacional)", "% folhas doentes · praga")
    plu = caixa(ax, 0.45, 4.35, 3.4, 1.25, "Pluviômetro", "precipitação (mm)")

    # 2. Processamento
    grupo(ax, 4.5, 4.0, 4.1, 8.0, "2 · PROCESSAMENTO (Data Lake)", CORES["proc"])
    raw = caixa(ax, 4.75, 10.0, 3.6, 1.3, "dados/raw", "CSV do simulador + serial", cilindro=True)
    proc = caixa(ax, 4.75, 7.35, 3.6, 2.2, "processar_dados.py",
                 "padroniza · deduplica\nvalida faixas físicas\nimputa (interpolação)\ncria 9 features temporais")
    rej = caixa(ax, 4.75, 5.95, 2.9, 1.0, "raw/rejeitados", "auditoria com motivo", cilindro=True)
    tru = caixa(ax, 4.75, 4.3, 3.6, 1.3, "dados/trusted", "leituras_processadas.csv\nqualidade_dados.json",
                cilindro=True)

    # 3. Automação e inteligência
    grupo(ax, 9.0, 4.0, 5.6, 8.0, "3 · AUTOMAÇÃO E INTELIGÊNCIA", CORES["intel"])
    regras = caixa(ax, 9.25, 9.55, 2.5, 1.6, "Motor de regras",
                   "5 regras graduadas\nherda MotorDeRegras\n(Fase 4) · episódios")
    ml = caixa(ax, 11.9, 9.55, 2.5, 1.6, "Random Forest",
               "risco de evento\ncrítico em 6h\nF1 0,95 vs 0,89")
    dec = caixa(ax, 9.25, 7.7, 5.15, 1.45, "Decisão combinada",
                "nível final = o mais grave entre alerta ativo e risco previsto\n+ recomendação priorizada por talhão")
    acao = caixa(ax, 9.25, 5.9, 2.5, 1.45, "Ações automáticas",
                 "IRRIGACAO_ON · manutenção\nnotificação → log de ações")
    ia = caixa(ax, 11.9, 5.9, 2.5, 1.45, "IA Generativa (Fase 5)",
               "relatório de apoio à\ndecisão por talhão")
    minera = caixa(ax, 9.25, 4.25, 5.15, 1.3, "Mineração de processos (Fase 7)",
                   "event log (CSV/XES) · variantes · DFG · gargalos")

    # 4. Saída
    grupo(ax, 15.0, 4.0, 6.8, 8.0, "4 · SAÍDA", CORES["saida"])
    ref = caixa(ax, 15.25, 9.3, 3.0, 2.05, "dados/refined",
                "alertas.csv · predições\nstatus_talhoes.json\nrelatórios IA · event log\nresumo_talhoes (Fase 5)",
                cilindro=True)
    dash = caixa(ax, 18.55, 9.3, 3.0, 2.05, "Dashboard Streamlit",
                 ":8501 · KPIs · séries\nalertas · risco ML · IA\nMonitoramento · Processo")
    log_acoes = caixa(ax, 15.25, 7.0, 3.0, 1.8, "Alertas e relatórios",
                      "acoes_automaticas.log\nrelatorio_decisao.md\nrelatorios_ia/*.md")
    gestor = caixa(ax, 18.55, 7.0, 3.0, 1.8, "Produtor / agrônomo",
                   "decide e age em campo\n(atuador = controlador\nde irrigação)")
    bi = caixa(ax, 15.25, 4.3, 6.3, 2.2, "Consumidores dos dados",
               "Power BI (CSV) · API Flask + Kafka (Fase 4)\nProM / Disco / pm4py (event_log.xes)\n"
               "seguradoras e cooperativas (Canvas v2)")

    # 5. Operação (Fase 7)
    grupo(ax, 0.2, 0.25, 21.6, 3.45, "5 · OPERAÇÃO — execução automatizada, monitoramento e DevSecOps (Fase 7)", CORES["ops"])
    orq = caixa(ax, 0.45, 0.5, 4.2, 2.6, "Orquestrador",
                "run_plataforma.py --loop\n1 ciclo a cada N s (AGRO_INTERVALO_S)\nnovo lote de sensores por ciclo\n"
                "falha isolada: ciclo seguinte segue")
    mon = caixa(ax, 4.95, 0.5, 5.0, 2.6, "Monitoramento",
                "logs/agrosmart.log (JSON, rotacionado)\nexecucoes.jsonl (etapa, duração, status)\n"
                "status.json (indicadores, disponibilidade)\nhealthcheck.py → Docker HEALTHCHECK")
    dock = caixa(ax, 10.25, 0.5, 5.0, 2.6, "Docker Compose",
                 "agrosmart_pipeline (loop) + agrosmart_dashboard\nmesma imagem · volumes dados/logs\n"
                 "non-root · read-only · cap_drop ALL\nlimites de CPU/memória · restart")
    ci = caixa(ax, 15.55, 0.5, 6.0, 2.6, "Pipeline DevSecOps (GitHub Actions)",
               "ruff (lint/complexidade) · pytest + cobertura\nbandit (SAST) · pip-audit (SCA) · gitleaks\n"
               "docker build · Trivy config + imagem (CVE)\nsmoke test do container · publica no GHCR")

    # fluxo de dados
    for fonte, rot in ((ard, "serial 9600"), (sim, "CSV"), (cam, ""), (plu, "")):
        seta(ax, direita(fonte), (raw[0], raw[1] + 0.65), rot)
    seta(ax, base(raw), topo(proc))
    seta(ax, (rej[0] + 1.45, proc[1]), topo(rej), "inválidos", cor="#c62828")
    seta(ax, (8.0, proc[1]), (8.0, tru[1] + tru[3]), "válidos", cor="#2e7d32")
    # barramento: as leituras limpas alimentam o motor de regras e o modelo
    seta(ax, direita(tru), (8.85, 11.42), "leituras limpas\n+ features", estilo="-", rad=0.15)
    seta(ax, (8.85, 11.42), (13.15, 11.42), estilo="-")
    seta(ax, (10.5, 11.42), topo(regras))
    seta(ax, (13.15, 11.42), topo(ml))
    seta(ax, base(regras), (regras[0] + 1.25, dec[1] + dec[3]))
    seta(ax, base(ml), (ml[0] + 1.25, dec[1] + dec[3]))
    seta(ax, (acao[0] + 1.25, dec[1]), topo(acao))
    seta(ax, (ia[0] + 1.25, dec[1]), topo(ia))
    seta(ax, (dec[0] + dec[2], dec[1] + 0.9), (ref[0], ref[1] + 0.5), "alertas · risco · status")
    seta(ax, direita(ia), (log_acoes[0], log_acoes[1] + 0.5), "relatórios")
    seta(ax, direita(ref), esquerda(dash))
    seta(ax, (dash[0] + 1.5, dash[1]), topo(gestor))
    seta(ax, direita(log_acoes), esquerda(gestor), "notificação")
    seta(ax, direita(minera), (bi[0], bi[1] + 1.0), "event log")
    seta(ax, (ref[0] + 1.5, ref[1]), (ref[0] + 1.5, log_acoes[1] + log_acoes[3]))
    seta(ax, (ref[0] - 0.05, ref[1] + 0.1), (minera[0] + minera[2] + 0.05, minera[1] + 1.1), cor="#6a1b9a")
    seta(ax, (gestor[0] + 1.5, gestor[1]), (bi[0] + 4.7, bi[1] + bi[3]), estilo="-", ls=":")

    # operação controla as etapas
    seta(ax, topo(orq), (proc[0] - 0.1, 4.0), "executa as etapas", cor="#546e7a", ls="--", rad=-0.2)
    seta(ax, direita(orq), esquerda(mon), "registra", cor="#546e7a")
    seta(ax, direita(mon), esquerda(dock), "healthcheck", cor="#546e7a")
    seta(ax, direita(ci), (ci[0] + ci[2] - 0.2, ci[1] + ci[3]), estilo="-")
    seta(ax, esquerda(ci), direita(dock), "imagem aprovada", cor="#2e7d32")
    seta(ax, (mon[0] + 4.0, mon[1] + mon[3]), (dash[0] + 1.5, 4.0), "aba Monitoramento", cor="#546e7a",
         ls="--", rad=-0.08)

    fig.tight_layout()
    fig.savefig(SAIDA, dpi=120)
    print(f"diagrama salvo em {SAIDA}")


if __name__ == "__main__":
    main()
