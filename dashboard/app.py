"""
app.py — Dashboard analítico do AgroSmart (Fase 6)

Lê as camadas trusted e refined do pipeline (dados/trusted e dados/refined) e apresenta:
  - indicadores do ambiente (KPIs do período filtrado)
  - situação atual de cada talhão (decisão combinada regras + ML) e o
    relatório da IA Generativa (módulo da Fase 5)
  - evolução temporal de umidade, temperatura e luminosidade
  - alertas gerados e ações automáticas executadas
  - risco previsto pelo modelo de Machine Learning e suas métricas
  - qualidade dos dados e a estação TinkerCad

Uso:
    streamlit run dashboard/app.py
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
TRUSTED_DIR = ROOT_DIR / "dados" / "trusted"
REFINED_DIR = ROOT_DIR / "dados" / "refined"
REJEITADOS_DIR = ROOT_DIR / "dados" / "raw" / "rejeitados"

# Cor fixa por talhão (a cor segue o talhão, nunca a posição no filtro)
CORES_TALHAO = {
    "TAL-01": "#2a78d6", "TAL-02": "#eb6834", "TAL-03": "#1baf7a",
    "TAL-04": "#eda100", "TAL-05": "#e87ba4", "TAL-TC": "#008300",
}
# Cores de status são reservadas e sempre acompanham ícone + rótulo
STATUS = {
    "CRITICO": {"cor": "#d03b3b", "icone": "🔴", "rotulo": "Crítico"},
    "ATENCAO": {"cor": "#ec835a", "icone": "🟠", "rotulo": "Atenção"},
    "AVISO":   {"cor": "#fab219", "icone": "🟡", "rotulo": "Aviso"},
    "NORMAL":  {"cor": "#0ca30c", "icone": "🟢", "rotulo": "Normal"},
}
RISCO = {"ALTO": "🔴 Alto", "MEDIO": "🟠 Médio", "BAIXO": "🟢 Baixo"}
LIMIAR_COR = "#898781"

st.set_page_config(page_title="AgroSmart — Painel", page_icon="🌱", layout="wide")


@st.cache_data
def carregar():
    leituras = pd.read_csv(TRUSTED_DIR / "leituras_processadas.csv", parse_dates=["timestamp"])
    alertas = pd.read_csv(REFINED_DIR / "alertas.csv", parse_dates=["inicio", "fim"])
    predicoes = pd.read_csv(REFINED_DIR / "predicoes_risco.csv", parse_dates=["timestamp"])
    rejeitados = pd.read_csv(REJEITADOS_DIR / "rejeitados.csv")
    status = json.loads((REFINED_DIR / "status_talhoes.json").read_text(encoding="utf-8"))
    metricas = json.loads((REFINED_DIR / "metricas_modelo.json").read_text(encoding="utf-8"))
    qualidade = json.loads((TRUSTED_DIR / "qualidade_dados.json").read_text(encoding="utf-8"))
    acoes = (REFINED_DIR / "acoes_automaticas.log").read_text(encoding="utf-8")
    relatorios_ia = {caminho.stem.split("_")[0]: caminho.read_text(encoding="utf-8")
                     for caminho in sorted((REFINED_DIR / "relatorios_ia").glob("*.md"))}
    return leituras, alertas, predicoes, rejeitados, status, metricas, qualidade, acoes, relatorios_ia


def grafico_linha(df, coluna, titulo, unidade, limiares=(), faixa=None):
    fig = go.Figure()
    if faixa:
        fig.add_hrect(y0=faixa[0], y1=faixa[1], fillcolor="#0ca30c", opacity=0.06, line_width=0,
                      annotation_text="faixa segura", annotation_position="top left",
                      annotation_font_color=LIMIAR_COR)
    for talhao_id, grupo in df.groupby("talhao_id"):
        fig.add_trace(go.Scatter(
            x=grupo["timestamp"], y=grupo[coluna], name=talhao_id, mode="lines",
            line=dict(color=CORES_TALHAO.get(talhao_id), width=2),
            hovertemplate=f"{talhao_id}: %{{y:.1f}} {unidade}<extra></extra>"))
    for valor, texto in limiares:
        fig.add_hline(y=valor, line=dict(color=LIMIAR_COR, width=1, dash="dash"),
                      annotation_text=texto, annotation_position="bottom right",
                      annotation_font_color=LIMIAR_COR)
    fig.update_xaxes(tickformat="%d/%m", hoverformat="%d/%m %H:%M")
    fig.update_layout(title=titulo, height=340, hovermode="x unified",
                      margin=dict(l=10, r=10, t=50, b=10), yaxis_title=unidade,
                      legend=dict(orientation="h", y=-0.15))
    return fig


def bloco_reprocessar():
    st.sidebar.divider()
    st.sidebar.subheader("Gerar novos dados")
    seed = st.sidebar.number_input("Semente do simulador", min_value=1, value=42, step=1)
    if st.sidebar.button("Rodar pipeline completo", width="stretch"):
        with st.spinner("Coletando, processando, executando a automação e gerando os relatórios..."):
            resultado = subprocess.run([sys.executable, str(ROOT_DIR / "run_plataforma.py"), "--seed", str(seed)],
                                       capture_output=True, text=True)
        if resultado.returncode != 0:
            st.sidebar.error("Falha no pipeline")
            st.sidebar.code(resultado.stderr[-1500:])
        else:
            st.cache_data.clear()
            st.rerun()


# ─────────────────────────────── carga e filtros ───────────────────────────────
try:
    leituras, alertas, predicoes, rejeitados, status, metricas, qualidade, acoes, relatorios_ia = carregar()
except FileNotFoundError:
    st.error("Dados não encontrados. Rode antes: `python run_plataforma.py`")
    bloco_reprocessar()
    st.stop()

campo = leituras[leituras["fonte"] == "simulador_campo"]
talhoes_campo = sorted(campo["talhao_id"].unique())

st.sidebar.title("🌱 AgroSmart")
st.sidebar.caption("Plataforma integrada — Fases 4, 5 e 6")
selecionados = st.sidebar.multiselect("Talhões", talhoes_campo, default=talhoes_campo)
data_min, data_max = campo["timestamp"].min().date(), campo["timestamp"].max().date()
periodo = st.sidebar.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max)
if not isinstance(periodo, tuple) or len(periodo) != 2:
    st.stop()
inicio, fim = pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1]) + pd.Timedelta(days=1)
bloco_reprocessar()

filtro = campo[campo["talhao_id"].isin(selecionados) & campo["timestamp"].between(inicio, fim, inclusive="left")]
alertas_f = alertas[alertas["talhao_id"].isin(selecionados) & alertas["inicio"].between(inicio, fim, inclusive="left")]
pred_f = predicoes[predicoes["talhao_id"].isin(selecionados) & predicoes["timestamp"].between(inicio, fim, inclusive="left")]

if filtro.empty:
    st.warning("Nenhuma leitura para o filtro selecionado.")
    st.stop()

# ─────────────────────────────── cabeçalho e KPIs ───────────────────────────────
st.title("AgroSmart — Painel de Monitoramento Inteligente")
st.caption(f"Período: {periodo[0]:%d/%m/%Y} a {periodo[1]:%d/%m/%Y} · {len(filtro):,} leituras · "
           f"{len(selecionados)} talhão(ões)".replace(",", "."))

talhoes_risco_alto = [t for t in selecionados if status.get(t, {}).get("risco_previsto") == "ALTO"]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Temperatura média", f"{filtro['temperatura_c'].mean():.1f} °C",
          help=f"Mín {filtro['temperatura_c'].min():.1f} °C · Máx {filtro['temperatura_c'].max():.1f} °C")
k2.metric("Umidade média do solo", f"{filtro['umidade_solo_pct'].mean():.1f} %",
          help=f"Mínima no período: {filtro['umidade_solo_pct'].min():.1f} %")
k3.metric("Luminosidade média", f"{filtro['luminosidade_pct'].mean():.0f} %")
k4.metric("Alertas críticos", int((alertas_f["nivel"] == "CRITICO").sum()),
          help=f"{len(alertas_f)} episódios de alerta no total")
k5.metric("Talhões em risco alto (6h)", len(talhoes_risco_alto),
          help=", ".join(talhoes_risco_alto) or "nenhum")

# ─────────────────────────────── situação atual ───────────────────────────────
st.subheader("Situação atual por talhão")
st.caption("Nível final = o mais grave entre o alerta ativo (regras) e o risco previsto para as próximas 6h (ML).")
cards = [t for t in sorted(status) if t in selecionados or t == "TAL-TC"]
for linha in range(0, len(cards), 3):
    colunas = st.columns(3)
    for coluna, talhao_id in zip(colunas, cards[linha:linha + 3]):
        s = status[talhao_id]
        st_info = STATUS[s["nivel_final"]]
        with coluna.container(border=True):
            origem = " · estação TinkerCad" if s["fonte"] == "tinkercad" else ""
            st.markdown(f"**{talhao_id}**{origem} &nbsp; {st_info['icone']} **{st_info['rotulo']}**")
            st.markdown(f"Umidade **{s['umidade_solo_pct']:.1f}%** · Temp. **{s['temperatura_c']:.1f} °C** · "
                        f"Risco 6h **{s['prob_evento_6h']:.0%}**")
            st.caption(f"Risco previsto: {RISCO[s['risco_previsto']]} · "
                       f"Irrigação {'ligada' if s['irrigacao_ligada'] else 'desligada'} · "
                       f"leitura de {s['ultima_leitura']}")
            ativos = ", ".join(f"{STATUS[a['nivel']]['icone']} {a['regra']}" for a in s["alertas_ativos"])
            if ativos:
                st.markdown(f"Alertas ativos: {ativos}")
            st.markdown(f"➡️ {s['recomendacao_priorizada'][0]}")
            if talhao_id in relatorios_ia:
                with st.expander("📝 Relatório da IA Generativa"):
                    st.markdown(relatorios_ia[talhao_id])

# ─────────────────────────────── abas analíticas ───────────────────────────────
aba_tempo, aba_alertas, aba_ml, aba_tc, aba_qualidade = st.tabs([
    "📈 Evolução no tempo", "🚨 Alertas e ações", "🤖 Risco previsto (ML)",
    "🔌 Estação TinkerCad", "🧹 Qualidade dos dados"])

with aba_tempo:
    st.plotly_chart(grafico_linha(filtro, "umidade_solo_pct", "Umidade do solo", "%",
                                  limiares=[(30, "limite de irrigação (30%)"), (20, "crítico (20%)")]),
                    width="stretch")
    st.plotly_chart(grafico_linha(filtro, "temperatura_c", "Temperatura do ar", "°C",
                                  limiares=[(38, "calor crítico (38 °C)"), (3, "geada (3 °C)")],
                                  faixa=(12, 35)), width="stretch")
    st.plotly_chart(grafico_linha(filtro, "luminosidade_pct", "Luminosidade", "%"), width="stretch")

    diario = (filtro.assign(data=filtro["timestamp"].dt.date)
                    .groupby(["data", "talhao_id"], as_index=False)["perc_folhas_doentes"].max())
    fig = px.line(diario, x="data", y="perc_folhas_doentes", color="talhao_id", markers=True,
                  color_discrete_map=CORES_TALHAO, title="Folhas doentes (máximo diário, visão computacional)")
    fig.add_hline(y=30, line=dict(color=LIMIAR_COR, width=1, dash="dash"),
                  annotation_text="infestação (30%)", annotation_font_color=LIMIAR_COR)
    fig.update_traces(line_width=2, marker_size=8)
    fig.update_xaxes(tickformat="%d/%m")
    fig.update_layout(height=320, hovermode="x unified", yaxis_title="%", xaxis_title=None,
                      legend=dict(orientation="h", y=-0.2, title=None), margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, width="stretch")

with aba_alertas:
    if alertas_f.empty:
        st.info("Nenhum alerta no período selecionado.")
    else:
        contagem = alertas_f.groupby(["regra", "nivel"], as_index=False).size()
        ordem_niveis = ["CRITICO", "ATENCAO", "AVISO"]
        fig = px.bar(contagem, y="regra", x="size", color="nivel", orientation="h",
                     category_orders={"nivel": ordem_niveis},
                     color_discrete_map={n: STATUS[n]["cor"] for n in ordem_niveis},
                     labels={"size": "episódios", "regra": "", "nivel": "Nível"},
                     title="Episódios de alerta por regra e nível")
        fig.update_traces(marker_line_color="rgba(0,0,0,0)", hovertemplate="%{y}: %{x} episódio(s)<extra></extra>")
        fig.update_layout(height=320, bargap=0.35, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, width="stretch")

        tabela = alertas_f.sort_values("inicio", ascending=False).assign(
            nivel=lambda d: d["nivel"].map(lambda n: f"{STATUS[n]['icone']} {STATUS[n]['rotulo']}"))
        st.dataframe(tabela[["inicio", "talhao_id", "regra", "nivel", "duracao_h", "valor_pior",
                             "ativo_agora", "acao_automatica", "recomendacao"]],
                     hide_index=True, width="stretch",
                     column_config={"inicio": st.column_config.DatetimeColumn("Início", format="DD/MM HH:mm"),
                                    "duracao_h": "Duração (h)", "valor_pior": "Pior valor",
                                    "ativo_agora": "Ativo?", "acao_automatica": "Ação automática",
                                    "recomendacao": "Recomendação"})
    with st.expander("Log de ações automáticas executadas"):
        st.code(acoes, language=None)

with aba_ml:
    st.markdown(f"**Modelo:** {metricas['modelo']}  \n**Alvo:** {metricas['alvo']}  \n"
                f"**Validação:** {metricas['divisao']} "
                f"({metricas['amostras_treino']} amostras de treino, {metricas['amostras_teste']} de teste)")
    m, b = metricas["metricas_modelo"], metricas["metricas_baseline_regra_atual"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Acurácia", f"{m['acuracia']:.1%}", f"{(m['acuracia'] - b['acuracia']) * 100:+.1f} p.p. vs regra")
    c2.metric("Precisão", f"{m['precisao']:.1%}", f"{(m['precisao'] - b['precisao']) * 100:+.1f} p.p. vs regra")
    c3.metric("Recall", f"{m['recall']:.1%}", f"{(m['recall'] - b['recall']) * 100:+.1f} p.p. vs regra")
    c4.metric("F1", f"{m['f1']:.3f}", f"{m['f1'] - b['f1']:+.3f} vs regra")
    st.caption("Baseline = prever evento nas próximas 6h só quando já existe evento agora (o que uma regra reativa faz). "
               "O ganho de recall mostra os eventos que o modelo antecipa.")

    fig = go.Figure()
    for talhao_id, grupo in pred_f.groupby("talhao_id"):
        fig.add_trace(go.Scatter(x=grupo["timestamp"], y=grupo["prob_evento_6h"], name=talhao_id, mode="lines",
                                 line=dict(color=CORES_TALHAO.get(talhao_id), width=2),
                                 hovertemplate=f"{talhao_id}: %{{y:.0%}}<extra></extra>"))
    for valor, texto in [(0.6, "risco alto"), (0.3, "risco médio")]:
        fig.add_hline(y=valor, line=dict(color=LIMIAR_COR, width=1, dash="dash"),
                      annotation_text=texto, annotation_font_color=LIMIAR_COR)
    fig.update_xaxes(tickformat="%d/%m", hoverformat="%d/%m %H:%M")
    fig.update_layout(title="Probabilidade prevista de evento crítico nas próximas 6h", height=360,
                      hovermode="x unified", yaxis=dict(tickformat=".0%", range=[0, 1.02]),
                      legend=dict(orientation="h", y=-0.15), margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, width="stretch")

    importancias = pd.DataFrame(list(metricas["importancia_features"].items()), columns=["feature", "importancia"])
    fig = px.bar(importancias.sort_values("importancia"), x="importancia", y="feature", orientation="h",
                 title="Importância das variáveis no modelo", labels={"feature": "", "importancia": "importância"})
    fig.update_traces(marker_color="#2a78d6", hovertemplate="%{y}: %{x:.3f}<extra></extra>")
    fig.update_layout(height=420, bargap=0.35, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, width="stretch")

    matriz = metricas["matriz_confusao_modelo"]["valores"]
    st.markdown("**Matriz de confusão (teste)**")
    st.dataframe(pd.DataFrame(matriz, index=["real: sem evento", "real: com evento"],
                              columns=["previsto: sem evento", "previsto: com evento"]))

with aba_tc:
    tc = leituras[leituras["fonte"] == "tinkercad"]
    if tc.empty:
        st.info("Nenhuma captura do TinkerCad em dados/raw/tinkercad_serial.txt")
    else:
        st.markdown("Leituras do Arduino simulado no TinkerCad (TMP36, sensor de umidade do solo, "
                    "fotorresistor e PIR), integradas ao mesmo pipeline dos sensores de campo.")
        tc = tc.assign(segundos=(tc["timestamp"] - tc["timestamp"].min()).dt.total_seconds())
        longo = tc.melt(id_vars="segundos", value_vars=["temperatura_c", "umidade_solo_pct", "luminosidade_pct"],
                        var_name="sensor", value_name="valor")
        nomes = {"temperatura_c": "Temperatura (°C)", "umidade_solo_pct": "Umidade do solo (%)",
                 "luminosidade_pct": "Luminosidade (%)"}
        longo["sensor"] = longo["sensor"].map(nomes)
        fig = px.line(longo, x="segundos", y="valor", facet_row="sensor", markers=True, height=560,
                      labels={"segundos": "segundos desde o início da simulação", "valor": ""})
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_yaxes(matches=None)
        fig.update_traces(line=dict(color=CORES_TALHAO["TAL-TC"], width=2), marker_size=8)
        fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, width="stretch")
        st.dataframe(tc.drop(columns=["segundos"]), hide_index=True, width="stretch")

with aba_qualidade:
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Linhas recebidas", qualidade["linhas_recebidas"])
    q2.metric("Duplicadas removidas", qualidade["duplicadas_removidas"])
    q3.metric("Rejeitadas (valor impossível)", qualidade["rejeitadas_fora_da_faixa"])
    q4.metric("Campos vazios imputados", qualidade["linhas_com_valor_imputado"])
    st.markdown("**Leituras rejeitadas na validação** (não são descartadas: ficam registradas para auditoria)")
    st.dataframe(rejeitados, hide_index=True, width="stretch")
    st.download_button("Baixar leituras processadas (CSV)",
                       (TRUSTED_DIR / "leituras_processadas.csv").read_bytes(),
                       file_name="leituras_processadas.csv", mime="text/csv")
