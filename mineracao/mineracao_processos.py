"""
mineracao_processos.py — Mineração de processos da plataforma AgroSmart (Fase 7).

Analisa DOIS processos, cada um com o seu event log (case_id, atividade, timestamp):

  A) Processo OPERACIONAL — "ciclo de vida de uma ocorrência no talhão"
     Case = um episódio de alerta (talhão + regra + início). Os eventos são
     reconstruídos a partir das saídas reais da plataforma:
       - predicoes_risco.csv   -> "Risco previsto pelo ML" (até 6h antes do alerta)
       - alertas.csv           -> "Alerta disparado", "Ação automática executada",
                                   "Gestor notificado", "Ordem de manutenção aberta",
                                   "Reincidência detectada" (mesma regra em < 24h)
       - leituras_processadas  -> "Escalado para CRÍTICO" (nível piorou durante o
                                   episódio) e "Condição normalizada" (1ª leitura em
                                   que a regra deixa de disparar) / "Ocorrência em aberto"

  B) Processo TÉCNICO — "execução do pipeline"
     Case = um ciclo (run_id); atividades = etapas, com início/fim reais medidos
     pelo monitoramento (dados/monitoramento/execucoes.jsonl).

Para cada processo calcula: variantes, grafo de sucessão direta (DFG) com
frequência e tempo médio entre atividades, gargalos e indicadores, e gera um
relatório com insights. O event log também é exportado em XES (padrão IEEE
1849) para abrir no ProM, Disco, Celonis ou pm4py.

Saídas em dados/refined/processo/:
  event_log.csv, event_log.xes, event_log_pipeline.csv, variantes.csv, dfg.csv,
  desempenho_regras.csv, etapas_pipeline.csv, dfg_operacional.dot, dfg_operacional.png,
  etapas_pipeline.png, analise_processo.json, analise_processo.md

Uso:
    python mineracao/mineracao_processos.py
"""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "automacao"))
from automacao_inteligente import REGRAS  # noqa: E402

from monitoramento.monitor import ARQ_EXECUCOES, ler_execucoes  # noqa: E402

TRUSTED_DIR = ROOT_DIR / "dados" / "trusted"
REFINED_DIR = ROOT_DIR / "dados" / "refined"
SAIDA_DIR = REFINED_DIR / "processo"

INICIO, FIM = "▶ Início", "■ Fim"
# Ordem lógica das atividades (desempate de eventos no mesmo instante e layout do diagrama)
ATIVIDADES = {
    "Risco previsto pelo ML":      {"ordem": 1, "camada": 1, "recurso": "Modelo ML"},
    "Reincidência detectada":      {"ordem": 2, "camada": 1, "recurso": "Motor de regras"},
    "Alerta disparado":            {"ordem": 3, "camada": 2, "recurso": "Motor de regras"},
    "Ação automática executada":   {"ordem": 4, "camada": 3, "recurso": "Automação"},
    "Gestor notificado":           {"ordem": 5, "camada": 4, "recurso": "Automação"},
    "Ordem de manutenção aberta":  {"ordem": 6, "camada": 4, "recurso": "Equipe de manutenção"},
    "Escalado para CRÍTICO":       {"ordem": 7, "camada": 5, "recurso": "Motor de regras"},
    "Condição normalizada":        {"ordem": 8, "camada": 6, "recurso": "Sensor de campo"},
    "Ocorrência em aberto":        {"ordem": 9, "camada": 6, "recurso": "Gestor"},
}
REGRAS_COBERTAS_ML = {"FALHA_IRRIGACAO", "DEFICIT_HIDRICO", "TEMPERATURA_EXTREMA", "INFESTACAO"}
REGRAS_NOTIFICAM = {"FALHA_IRRIGACAO", "TEMPERATURA_EXTREMA", "INFESTACAO"}
JANELA_ANTECIPACAO = pd.Timedelta("6h")
JANELA_REINCIDENCIA = pd.Timedelta("24h")


# ───────────────────────────── A) event log operacional ─────────────────────────────

def construir_event_log(leituras: pd.DataFrame, alertas: pd.DataFrame, predicoes: pd.DataFrame) -> pd.DataFrame:
    eventos = []
    for talhao_id, grupo in leituras.groupby("talhao_id"):
        grupo = grupo.sort_values("timestamp").reset_index(drop=True)
        tempos = grupo["timestamp"]
        pred = predicoes[(predicoes["talhao_id"] == talhao_id) & (predicoes["risco_previsto"] == "ALTO")]
        niveis_por_regra = {nome: regra["avaliar"](grupo) for nome, regra in REGRAS.items()}
        fim_anterior: dict[str, pd.Timestamp] = {}

        for ep in alertas[alertas["talhao_id"] == talhao_id].sort_values("inicio").itertuples():
            case_id = f"{talhao_id}|{ep.regra}|{ep.inicio:%Y%m%d-%H%M%S}"
            base = {"case_id": case_id, "talhao_id": talhao_id, "regra": ep.regra, "nivel": ep.nivel}

            def evento(atividade, ts, **extra):
                eventos.append({**base, "atividade": atividade, "timestamp": ts,
                                "recurso": ATIVIDADES[atividade]["recurso"], **extra})

            if ep.regra in REGRAS_COBERTAS_ML:
                janela = pred[(pred["timestamp"] >= ep.inicio - JANELA_ANTECIPACAO) & (pred["timestamp"] < ep.inicio)]
                if len(janela):
                    evento("Risco previsto pelo ML", janela["timestamp"].iloc[0],
                           detalhe=f"probabilidade {janela['prob_evento_6h'].iloc[0]:.0%}")
            anterior = fim_anterior.get(ep.regra)
            if anterior is not None and ep.inicio - anterior <= JANELA_REINCIDENCIA:
                evento("Reincidência detectada", ep.inicio,
                       detalhe=f"{(ep.inicio - anterior).total_seconds() / 3600:.1f}h após o episódio anterior")
            evento("Alerta disparado", ep.inicio, detalhe=ep.descricao)
            evento("Ação automática executada", ep.inicio, detalhe=ep.acao_automatica)
            if ep.regra in REGRAS_NOTIFICAM:
                evento("Gestor notificado", ep.inicio)
            if ep.regra == "FALHA_IRRIGACAO":
                evento("Ordem de manutenção aberta", ep.inicio)

            no_episodio = (tempos >= ep.inicio) & (tempos <= ep.fim)
            niveis = niveis_por_regra[ep.regra][no_episodio].dropna()
            if len(niveis) and niveis.iloc[0] != "CRITICO" and (niveis == "CRITICO").any():
                evento("Escalado para CRÍTICO", grupo.loc[niveis[niveis == "CRITICO"].index[0], "timestamp"],
                       detalhe=f"começou como {niveis.iloc[0]}")

            depois = tempos[tempos > ep.fim]
            if not ep.ativo_agora and len(depois):
                evento("Condição normalizada", depois.iloc[0])
            else:
                evento("Ocorrência em aberto", tempos.iloc[-1], detalhe="ainda ativa no fim da janela analisada")
            fim_anterior[ep.regra] = ep.fim

    log = pd.DataFrame(eventos)
    log["ordem"] = log["atividade"].map(lambda a: ATIVIDADES[a]["ordem"])
    log = log.sort_values(["case_id", "timestamp", "ordem"]).drop(columns="ordem").reset_index(drop=True)
    return log[["case_id", "atividade", "timestamp", "recurso", "talhao_id", "regra", "nivel", "detalhe"]]


# ───────────────────────────── análise genérica de event log ─────────────────────────────

def variantes(log: pd.DataFrame) -> pd.DataFrame:
    seq = log.groupby("case_id", sort=False)["atividade"].agg(" → ".join)
    tabela = seq.value_counts().rename_axis("variante").reset_index(name="casos")
    tabela["pct_casos"] = (100 * tabela["casos"] / tabela["casos"].sum()).round(1)
    regras = log.drop_duplicates("case_id").set_index("case_id")["regra"]
    tabela["regras"] = tabela["variante"].map(
        lambda v: ", ".join(sorted(regras[seq[seq == v].index].unique())))
    return tabela


def dfg(log: pd.DataFrame) -> pd.DataFrame:
    """Grafo de sucessão direta: (a -> b), frequência e tempo entre eventos (horas)."""
    pares = []
    for _, caso in log.groupby("case_id", sort=False):
        atividades = [INICIO, *caso["atividade"], FIM]
        tempos = [caso["timestamp"].iloc[0], *caso["timestamp"], caso["timestamp"].iloc[-1]]
        for i in range(len(atividades) - 1):
            pares.append((atividades[i], atividades[i + 1], (tempos[i + 1] - tempos[i]).total_seconds() / 3600))
    df = pd.DataFrame(pares, columns=["de", "para", "horas"])
    return (df.groupby(["de", "para"])["horas"]
              .agg(frequencia="size", tempo_medio_h="mean", tempo_mediana_h="median", tempo_max_h="max",
                   tempo_total_h="sum")
              .round(2).reset_index().sort_values("frequencia", ascending=False))


def desempenho_por_regra(log: pd.DataFrame, alertas: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for regra, casos in log.groupby("regra"):
        por_caso = casos.groupby("case_id")
        n = por_caso.ngroups
        tem = lambda atv: por_caso["atividade"].apply(lambda s: atv in set(s))  # noqa: E731
        abertos = tem("Ocorrência em aberto")
        disparo = casos[casos["atividade"] == "Alerta disparado"].set_index("case_id")["timestamp"]
        normal = casos[casos["atividade"] == "Condição normalizada"].set_index("case_id")["timestamp"]
        resolucao = ((normal - disparo.reindex(normal.index)).dt.total_seconds() / 3600).dropna()
        ml = casos[casos["atividade"] == "Risco previsto pelo ML"].set_index("case_id")["timestamp"]
        antecedencia = ((disparo.reindex(ml.index) - ml).dt.total_seconds() / 3600).dropna()
        linhas.append({
            "regra": regra,
            "casos": n,
            "criticos": int((alertas[alertas["regra"] == regra]["nivel"] == "CRITICO").sum()),
            "pct_em_aberto": round(100 * abertos.mean(), 1),
            "resolucao_media_h": round(resolucao.mean(), 1) if len(resolucao) else None,
            "resolucao_mediana_h": round(resolucao.median(), 1) if len(resolucao) else None,
            "resolucao_max_h": round(resolucao.max(), 1) if len(resolucao) else None,
            "pct_reincidencia": round(100 * tem("Reincidência detectada").mean(), 1),
            "pct_escalados": round(100 * tem("Escalado para CRÍTICO").mean(), 1),
            "pct_antecipado_ml": round(100 * tem("Risco previsto pelo ML").mean(), 1) if regra in REGRAS_COBERTAS_ML else None,
            "antecedencia_ml_media_h": round(antecedencia.mean(), 1) if len(antecedencia) else None,
        })
    return pd.DataFrame(linhas).sort_values("casos", ascending=False)


# ───────────────────────────── B) event log técnico (pipeline) ─────────────────────────────

def event_log_pipeline(execucoes: list[dict]) -> pd.DataFrame:
    if not execucoes:
        return pd.DataFrame(columns=["case_id", "atividade", "inicio", "fim", "duracao_s", "status"])
    df = pd.DataFrame(execucoes).rename(columns={"run_id": "case_id", "etapa": "atividade"})
    for col in ("inicio", "fim"):
        df[col] = pd.to_datetime(df[col])
    return df[["case_id", "ciclo", "atividade", "inicio", "fim", "duracao_s", "status"]]


def analisar_pipeline(log_pipe: pd.DataFrame) -> pd.DataFrame:
    if log_pipe.empty:
        return pd.DataFrame()
    ordem = list(dict.fromkeys(log_pipe["atividade"]))
    tabela = (log_pipe.groupby("atividade")
              .agg(execucoes=("case_id", "size"),
                   erros=("status", lambda s: int((s == "erro").sum())),
                   duracao_media_s=("duracao_s", "mean"),
                   duracao_p95_s=("duracao_s", lambda s: s.quantile(0.95)),
                   duracao_max_s=("duracao_s", "max"))
              .reindex(ordem).round(2).reset_index())
    tabela["pct_tempo_ciclo"] = (100 * tabela["duracao_media_s"] / tabela["duracao_media_s"].sum()).round(1)
    return tabela


# ───────────────────────────── exportação ─────────────────────────────

def exportar_xes(log: pd.DataFrame, caminho: Path):
    """XES mínimo (IEEE 1849): um <trace> por caso, um <event> por atividade."""
    def attr(chave, valor, tipo="string"):
        return f'<{tipo} key="{chave}" value="{escape(str(valor), quote=True)}"/>'

    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<log xes.version="1.0" xmlns="http://www.xes-standard.org/">',
              '<extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>',
              '<extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext"/>',
              '<extension name="Organizational" prefix="org" uri="http://www.xes-standard.org/org.xesext"/>']
    for case_id, caso in log.groupby("case_id", sort=False):
        primeiro = caso.iloc[0]
        linhas.append("<trace>" + attr("concept:name", case_id) + attr("talhao_id", primeiro["talhao_id"])
                      + attr("regra", primeiro["regra"]) + attr("nivel", primeiro["nivel"]))
        for ev in caso.itertuples():
            linhas.append("  <event>" + attr("concept:name", ev.atividade)
                          + attr("time:timestamp", ev.timestamp.strftime("%Y-%m-%dT%H:%M:%S.000-03:00"), "date")
                          + attr("org:resource", ev.recurso) + "</event>")
        linhas.append("</trace>")
    linhas.append("</log>")
    caminho.write_text("\n".join(linhas), encoding="utf-8")


def gerar_dot(tabela_dfg: pd.DataFrame, freq_atividade: pd.Series) -> str:
    """DFG em Graphviz DOT (renderizado no dashboard com st.graphviz_chart)."""
    maior = tabela_dfg["frequencia"].max()
    linhas = ['digraph DFG {', '  rankdir=LR; bgcolor="transparent";',
              '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11];',
              '  edge [fontname="Helvetica", fontsize=9];']
    for no in [INICIO, *ATIVIDADES, FIM]:
        if no in (INICIO, FIM):
            linhas.append(f'  "{no}" [shape=circle, fillcolor="#e0e0e0", label="{no.split()[0]}", width=0.5];')
        elif no in freq_atividade:
            cor = "#fde2e1" if no in ("Ocorrência em aberto", "Escalado para CRÍTICO") else "#e3f0e3"
            linhas.append(f'  "{no}" [fillcolor="{cor}", label="{no}\\n({freq_atividade[no]})"];')
    for r in tabela_dfg.itertuples():
        largura = 1 + 4 * r.frequencia / maior
        tempo = f" · {r.tempo_medio_h:.1f}h" if r.tempo_medio_h >= 0.05 else ""
        cor = "#c0392b" if r.tempo_medio_h >= 12 else "#555555"
        linhas.append(f'  "{r.de}" -> "{r.para}" [label="{r.frequencia}{tempo}", penwidth={largura:.1f}, color="{cor}"];')
    linhas.append("}")
    return "\n".join(linhas)


# Posição fixa de cada atividade no mapa (x, y) — fluxo da esquerda para a direita
POSICOES_DFG = {
    INICIO: (0, 0), "Risco previsto pelo ML": (2.6, 1.3), "Reincidência detectada": (2.6, -1.3),
    "Alerta disparado": (5.2, 0), "Ação automática executada": (7.8, 0),
    "Gestor notificado": (10.4, 1.6), "Ordem de manutenção aberta": (10.4, -1.9),
    "Escalado para CRÍTICO": (13.0, -0.7), "Condição normalizada": (15.6, 1.0),
    "Ocorrência em aberto": (15.6, -1.9), FIM: (18.2, 0),
}


def _curvatura_livre(a, b, obstaculos, preferida):
    """Escolhe a curvatura (arc3) cuja curva não atravessa nenhuma outra caixa."""
    (x1, y1), (x2, y2) = a, b
    for rad in (preferida, 0.25, -0.25, 0.4, -0.4, 0.6, -0.6):
        cx, cy = (x1 + x2) / 2 + rad * (y2 - y1), (y1 + y2) / 2 - rad * (x2 - x1)
        pontos = [((1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2,
                   (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2) for t in [i / 40 for i in range(1, 40)]]
        if not any(abs(px - ox) < 0.95 and abs(py - oy) < 0.5 for px, py in pontos for ox, oy in obstaculos):
            return rad
    return preferida


def desenhar_dfg(tabela_dfg: pd.DataFrame, freq_atividade: pd.Series, caminho: Path):
    """Desenha o DFG em PNG com matplotlib (não exige Graphviz instalado)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(20, 8))
    caixas = {}
    for no, (x, y) in POSICOES_DFG.items():
        if no not in (INICIO, FIM) and no not in freq_atividade:
            continue
        terminal = no in (INICIO, FIM)
        cor = "#dddddd" if terminal else ("#f8d7d5" if no in ("Ocorrência em aberto", "Escalado para CRÍTICO")
                                          else "#dcefdc")
        largura = 0.9 if terminal else 1.7
        caixa = FancyBboxPatch((x - largura / 2, y - 0.4), largura, 0.8, boxstyle="round,pad=0.05",
                               fc=cor, ec="#333333", lw=1, zorder=3)
        ax.add_patch(caixa)
        caixas[no] = caixa
        rotulo = no if terminal else f"{no}\n({freq_atividade[no]} casos)"
        ax.text(x, y, rotulo, ha="center", va="center", fontsize=9, zorder=4)

    maior = tabela_dfg["frequencia"].max()
    for r in tabela_dfg.itertuples():
        if r.de not in caixas or r.para not in caixas:
            continue
        (x1, y1), (x2, y2) = POSICOES_DFG[r.de], POSICOES_DFG[r.para]
        rad = _curvatura_livre((x1, y1), (x2, y2), [POSICOES_DFG[n] for n in caixas if n not in (r.de, r.para)],
                               0.12 if abs(x2 - x1) > 2.7 else 0.0)
        cor = "#c0392b" if r.tempo_medio_h >= 12 else "#6b6b6b"
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), patchA=caixas[r.de], patchB=caixas[r.para],
                                     arrowstyle="-|>", mutation_scale=15, lw=0.8 + 4 * r.frequencia / maior,
                                     color=cor, alpha=0.8, connectionstyle=f"arc3,rad={rad}", zorder=2))
        # ponto médio da curva de Bézier usada pelo arc3
        mx = (x1 + x2) / 2 + 0.5 * rad * (y2 - y1)
        my = (y1 + y2) / 2 - 0.5 * rad * (x2 - x1)
        tempo = f" · {r.tempo_medio_h:.1f}h" if r.tempo_medio_h >= 0.05 else ""
        ax.text(mx, my, f"{r.frequencia}{tempo}", ha="center", va="center", fontsize=8.5, color=cor, zorder=5,
                bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})

    ax.set_xlim(-0.8, 19)
    ax.set_ylim(-2.8, 2.3)
    ax.axis("off")
    ax.set_title("AgroSmart — Mapa do processo de ocorrências (DFG: nº de casos · tempo médio entre atividades)\n"
                 "setas vermelhas = espera média ≥ 12h (gargalo)", fontsize=12)
    fig.tight_layout()
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


def desenhar_etapas(tabela_etapas: pd.DataFrame, caminho: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 3.8))
    t = tabela_etapas.iloc[::-1]
    cores = ["#c0392b" if p == t["pct_tempo_ciclo"].max() else "#2a78d6" for p in t["pct_tempo_ciclo"]]
    ax.barh(t["atividade"], t["duracao_media_s"], color=cores)
    for i, (d, p) in enumerate(zip(t["duracao_media_s"], t["pct_tempo_ciclo"], strict=True)):
        ax.text(d, i, f"  {d:.1f}s ({p:.0f}%)", va="center", fontsize=9)
    ax.set_xlabel("duração média por ciclo (s)")
    ax.set_title(f"Pipeline — duração média por etapa ({int(t['execucoes'].max())} ciclos)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, t["duracao_media_s"].max() * 1.3)
    fig.tight_layout()
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


# ───────────────────────────── insights ─────────────────────────────

def gerar_insights(log, tab_var, tab_dfg, tab_regras, tab_etapas, log_pipe) -> dict:
    n_casos = log["case_id"].nunique()
    abertos = log[log["atividade"] == "Ocorrência em aberto"]["case_id"].nunique()
    sem_inicio_fim = tab_dfg[(tab_dfg["de"] != INICIO) & (tab_dfg["para"] != FIM)]
    gargalo = sem_inicio_fim.sort_values("tempo_total_h", ascending=False).iloc[0]
    regras_resolvidas = tab_regras.dropna(subset=["resolucao_media_h"])
    regra_lenta = regras_resolvidas.sort_values("resolucao_media_h", ascending=False).iloc[0]
    reincidente = tab_regras.sort_values("pct_reincidencia", ascending=False).iloc[0]
    ml = tab_regras.dropna(subset=["pct_antecipado_ml"])
    criticos_ml = log[log["nivel"] == "CRITICO"].groupby("case_id")["atividade"].apply(
        lambda s: "Risco previsto pelo ML" in set(s))
    insights = {
        "casos": n_casos,
        "eventos": int(len(log)),
        "atividades": int(log["atividade"].nunique()),
        "variantes": int(len(tab_var)),
        "variante_principal": {"sequencia": tab_var.iloc[0]["variante"], "pct": float(tab_var.iloc[0]["pct_casos"])},
        "top3_variantes_pct": float(tab_var.head(3)["pct_casos"].sum()),
        "casos_em_aberto": int(abertos),
        "pct_casos_em_aberto": round(100 * abertos / n_casos, 1),
        "gargalo_transicao": {"de": gargalo["de"], "para": gargalo["para"], "frequencia": int(gargalo["frequencia"]),
                              "tempo_medio_h": float(gargalo["tempo_medio_h"]),
                              "tempo_total_h": float(gargalo["tempo_total_h"])},
        "regra_resolucao_mais_lenta": {"regra": regra_lenta["regra"],
                                       "resolucao_media_h": float(regra_lenta["resolucao_media_h"])},
        "regra_mais_reincidente": {"regra": reincidente["regra"], "pct": float(reincidente["pct_reincidencia"])},
        "pct_criticos_antecipados_ml": round(100 * criticos_ml.mean(), 1) if len(criticos_ml) else None,
        "antecedencia_ml_media_h": (round(float(ml["antecedencia_ml_media_h"].dropna().mean()), 1)
                                    if ml["antecedencia_ml_media_h"].notna().any() else None),
        "ocorrencias_por_talhao": log.drop_duplicates("case_id")["talhao_id"].value_counts().to_dict(),
    }
    if not tab_etapas.empty:
        lenta = tab_etapas.sort_values("duracao_media_s", ascending=False).iloc[0]
        ciclos = log_pipe.groupby("case_id")
        duracao_ciclo = ciclos["duracao_s"].sum()
        insights["pipeline"] = {
            "ciclos": int(ciclos.ngroups),
            "ciclos_com_erro": int(ciclos["status"].apply(lambda s: (s == "erro").any()).sum()),
            "duracao_media_ciclo_s": round(float(duracao_ciclo.mean()), 2),
            "etapa_gargalo": lenta["atividade"],
            "etapa_gargalo_pct_tempo": float(lenta["pct_tempo_ciclo"]),
            "etapa_gargalo_media_s": float(lenta["duracao_media_s"]),
        }
    return insights


def gerar_relatorio_md(ins: dict, tab_var, tab_regras, tab_etapas) -> str:
    def tabela_md(df: pd.DataFrame) -> str:
        df = df.fillna("—")
        cab = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
        return cab + "\n".join("| " + " | ".join(str(v) for v in linha) + " |" for linha in df.values)

    g = ins["gargalo_transicao"]
    linhas = [
        "# Análise de processo — AgroSmart (gerado automaticamente)", "",
        f"**Event log operacional:** {ins['casos']} casos (ocorrências), {ins['eventos']} eventos, "
        f"{ins['atividades']} atividades distintas, **{ins['variantes']} variantes**.", "",
        "## Principais achados", "",
        f"- **Variante principal** ({ins['variante_principal']['pct']}% dos casos): "
        f"`{ins['variante_principal']['sequencia']}`. As 3 variantes mais comuns cobrem "
        f"{ins['top3_variantes_pct']}% dos casos.",
        f"- **Gargalo** (maior tempo acumulado de espera): `{g['de']} → {g['para']}` — "
        f"{g['frequencia']} ocorrências, média de {g['tempo_medio_h']}h, {g['tempo_total_h']}h acumuladas.",
        f"- **Resolução mais lenta:** {ins['regra_resolucao_mais_lenta']['regra']} "
        f"({ins['regra_resolucao_mais_lenta']['resolucao_media_h']}h em média entre o alerta e a normalização).",
        f"- **Casos em aberto** no fim da janela: {ins['casos_em_aberto']} ({ins['pct_casos_em_aberto']}%).",
        f"- **Retrabalho / reincidência:** {ins['regra_mais_reincidente']['regra']} reincide em "
        f"{ins['regra_mais_reincidente']['pct']}% dos casos (mesma regra em menos de 24h).",
        f"- **Antecipação pelo ML:** {ins['pct_criticos_antecipados_ml']}% das ocorrências críticas tiveram risco ALTO "
        f"previsto antes do alerta, com {ins['antecedencia_ml_media_h']}h de antecedência média.",
    ]
    if "pipeline" in ins:
        p = ins["pipeline"]
        linhas.append(f"- **Pipeline técnico:** {p['ciclos']} ciclo(s), {p['ciclos_com_erro']} com erro, "
                      f"{p['duracao_media_ciclo_s']}s por ciclo; etapa mais lenta: **{p['etapa_gargalo']}** "
                      f"({p['etapa_gargalo_pct_tempo']}% do tempo do ciclo).")
    linhas += ["", "## Variantes (top 10)", "", tabela_md(tab_var.head(10)), "",
               "## Desempenho por regra", "", tabela_md(tab_regras), ""]
    if not tab_etapas.empty:
        linhas += ["## Etapas do pipeline", "", tabela_md(tab_etapas), ""]
    return "\n".join(linhas)


def main():
    caminho_alertas = REFINED_DIR / "alertas.csv"
    if not caminho_alertas.exists():
        raise SystemExit("Rode antes: python automacao/automacao_inteligente.py")
    leituras = pd.read_csv(TRUSTED_DIR / "leituras_processadas.csv", parse_dates=["timestamp"])
    alertas = pd.read_csv(caminho_alertas, parse_dates=["inicio", "fim"])
    predicoes = pd.read_csv(REFINED_DIR / "predicoes_risco.csv", parse_dates=["timestamp"])
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)

    log = construir_event_log(leituras, alertas, predicoes)
    log.to_csv(SAIDA_DIR / "event_log.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    exportar_xes(log, SAIDA_DIR / "event_log.xes")

    tab_var = variantes(log)
    tab_dfg = dfg(log)
    tab_regras = desempenho_por_regra(log, alertas)
    tab_var.to_csv(SAIDA_DIR / "variantes.csv", index=False)
    tab_dfg.to_csv(SAIDA_DIR / "dfg.csv", index=False)
    tab_regras.to_csv(SAIDA_DIR / "desempenho_regras.csv", index=False)
    freq = log["atividade"].value_counts()
    (SAIDA_DIR / "dfg_operacional.dot").write_text(gerar_dot(tab_dfg, freq), encoding="utf-8")
    desenhar_dfg(tab_dfg, freq, SAIDA_DIR / "dfg_operacional.png")

    log_pipe = event_log_pipeline(ler_execucoes(ARQ_EXECUCOES))
    log_pipe.to_csv(SAIDA_DIR / "event_log_pipeline.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    tab_etapas = analisar_pipeline(log_pipe)
    tab_etapas.to_csv(SAIDA_DIR / "etapas_pipeline.csv", index=False)
    if not tab_etapas.empty:
        desenhar_etapas(tab_etapas, SAIDA_DIR / "etapas_pipeline.png")

    insights = gerar_insights(log, tab_var, tab_dfg, tab_regras, tab_etapas, log_pipe)
    with open(SAIDA_DIR / "analise_processo.json", "w", encoding="utf-8") as f:
        json.dump(insights, f, ensure_ascii=False, indent=2, default=str)
    (SAIDA_DIR / "analise_processo.md").write_text(
        gerar_relatorio_md(insights, tab_var, tab_regras, tab_etapas), encoding="utf-8")

    print(f"[mineracao] event log: {insights['casos']} casos, {insights['eventos']} eventos, "
          f"{insights['variantes']} variantes -> refined/processo/event_log.csv (+ .xes)")
    g = insights["gargalo_transicao"]
    print(f"[mineracao] gargalo: {g['de']} -> {g['para']} ({g['tempo_medio_h']}h em média, {g['frequencia']} casos)")
    print(f"[mineracao] {insights['pct_casos_em_aberto']}% das ocorrências em aberto; "
          f"{insights['pct_criticos_antecipados_ml']}% das críticas antecipadas pelo ML")
    if "pipeline" in insights:
        p = insights["pipeline"]
        print(f"[mineracao] pipeline: {p['ciclos']} ciclo(s), etapa mais lenta = {p['etapa_gargalo']} "
              f"({p['etapa_gargalo_pct_tempo']}% do ciclo)")


if __name__ == "__main__":
    main()
