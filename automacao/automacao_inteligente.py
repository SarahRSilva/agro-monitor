"""
automacao_inteligente.py
Automação baseada em dados (Fase 6). Combina duas abordagens:

  A) Motor de regras inferencial — herda o MotorDeRegras da Fase 4
     (docker/api/regras.py): as 3 regras booleanas de lá (infestação,
     irrigação, temperatura) são a condição base das regras graduadas
     daqui (AVISO/ATENCAO/CRITICO). Avalia cada leitura da camada trusted, agrupa leituras consecutivas que
     disparam a mesma regra em um único EPISÓDIO de alerta (evita gerar um
     alerta a cada 30 min para o mesmo problema), executa a ação automática
     correspondente (simulada — ex.: comando de irrigação) e registra uma
     recomendação para o operador.

  B) Machine Learning preditivo (Random Forest)
     Prevê a probabilidade de um EVENTO CRÍTICO acontecer nas próximas 6h
     a partir das condições atuais (umidade, tendência, temperatura,
     chuva acumulada, folhas doentes...). A regra só reage ao que já
     aconteceu; o modelo antecipa. A probabilidade vira uma classe de risco
     (BAIXO / MÉDIO / ALTO).

A decisão final de cada talhão combina as duas: o nível mais grave entre o
alerta ativo e o risco previsto, com a recomendação priorizada.

Lê dados/trusted/ e grava na camada dados/refined/ (mesmas camadas do Data
Lake da Fase 5).

Uso:
    python automacao/automacao_inteligente.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

ROOT_DIR = Path(__file__).resolve().parent.parent
TRUSTED_DIR = ROOT_DIR / "dados" / "trusted"
REFINED_DIR = ROOT_DIR / "dados" / "refined"

# Motor de regras da Fase 4 — o mesmo módulo usado pela API Flask em docker/api/
sys.path.insert(0, str(ROOT_DIR / "docker" / "api"))
from regras import (LIMIAR_FOLHAS_DOENTES_PCT, LIMIAR_TEMP_ALTA_C,  # noqa: E402
                    LIMIAR_TEMP_BAIXA_C, LIMIAR_UMIDADE_SECA_PCT, MotorDeRegras)

NIVEIS = {"AVISO": 1, "ATENCAO": 2, "CRITICO": 3}
HORIZONTE_PREVISAO = "6h"
DIAS_TREINO = 5  # primeiros 5 dias treinam, o restante testa (divisão temporal)

FEATURES = [
    "temperatura_c", "umidade_solo_pct", "luminosidade_pct", "movimento_detectado",
    "irrigacao_ligada", "perc_folhas_doentes", "praga_presente", "umidade_media_3h",
    "temp_media_3h", "tendencia_umidade_6h", "chuva_24h_mm", "temp_max_24h",
    "temp_min_24h", "hora",
]


# ─────────────────────────────── A) Motor de regras ───────────────────────────────
# Limiares novos da Fase 6; os da Fase 4 (30% de umidade, 30% de folhas doentes,
# 12-35 °C) vêm de docker/api/regras.py.
LIMIAR_UMIDADE_CRITICA_PCT = 20
LIMIAR_UMIDADE_PREVENTIVA_PCT = 40
QUEDA_UMIDADE_6H_PP = 6
CHUVA_RELEVANTE_24H_MM = 2
LIMIAR_FOLHAS_ATENCAO_PCT = 15
LIMIAR_CALOR_CRITICO_C = 38
LIMIAR_GEADA_C = 3
LIMIAR_LUZ_NOITE_PCT = 10


class MotorDeRegrasInferencial(MotorDeRegras):
    """Evolução do motor da Fase 4. Cada regra recebe o DataFrame e devolve uma
    Series com o nível por leitura (None quando a regra não dispara)."""

    @staticmethod
    def schema_fase4(df: pd.DataFrame) -> pd.DataFrame:
        # A Fase 4 recebia nivel_irrigacao (baixo/medio/alto); a Fase 6 mede se a bomba está ligada
        return df.assign(nivel_irrigacao=np.where(df["irrigacao_ligada"] == 1, "alto", "baixo"))

    @staticmethod
    def _vazio(df: pd.DataFrame) -> pd.Series:
        return pd.Series(None, index=df.index, dtype=object)

    def nivel_hidrico(self, df):
        nivel = self._vazio(df)
        preventivo = ((df["tendencia_umidade_6h"] < -QUEDA_UMIDADE_6H_PP)
                      & (df["umidade_solo_pct"] < LIMIAR_UMIDADE_PREVENTIVA_PCT))
        nivel[preventivo] = "AVISO"
        nivel[(df["umidade_solo_pct"] < LIMIAR_UMIDADE_SECA_PCT) & (df["chuva_24h_mm"] < CHUVA_RELEVANTE_24H_MM)] = "ATENCAO"
        nivel[df["umidade_solo_pct"] < LIMIAR_UMIDADE_CRITICA_PCT] = "CRITICO"
        return nivel

    def nivel_falha_irrigacao(self, df):
        # regra IRRIGAÇÃO da Fase 4 (solo seco E irrigação baixa) + sem chuva que explique
        nivel = self._vazio(df)
        nivel[self.mascara_irrigacao(self.schema_fase4(df)) & (df["chuva_24h_mm"] < CHUVA_RELEVANTE_24H_MM)] = "CRITICO"
        return nivel

    def nivel_temperatura(self, df):
        # regra TEMPERATURA da Fase 4 (fora de 12-35 °C), graduada pelos extremos
        nivel = self._vazio(df)
        fora_da_faixa = self.mascara_temperatura(df)
        nivel[fora_da_faixa & (df["temperatura_c"] < LIMIAR_TEMP_BAIXA_C)] = "AVISO"
        nivel[fora_da_faixa & (df["temperatura_c"] > LIMIAR_TEMP_ALTA_C)] = "ATENCAO"
        nivel[(df["temperatura_c"] > LIMIAR_CALOR_CRITICO_C) | (df["temperatura_c"] < LIMIAR_GEADA_C)] = "CRITICO"
        return nivel

    def nivel_infestacao(self, df):
        # regra INFESTAÇÃO da Fase 4 (praga E folhas doentes > 30%) + nível de atenção antecipado
        nivel = self._vazio(df)
        nivel[(df["praga_presente"] == 1) & (df["perc_folhas_doentes"] > LIMIAR_FOLHAS_ATENCAO_PCT)] = "ATENCAO"
        nivel[self.mascara_infestacao(df)] = "CRITICO"
        return nivel

    def nivel_movimento_noturno(self, df):
        nivel = self._vazio(df)
        nivel[(df["movimento_detectado"] == 1) & (df["luminosidade_pct"] < LIMIAR_LUZ_NOITE_PCT)] = "AVISO"
        return nivel


motor = MotorDeRegrasInferencial()

REGRAS = {
    "FALHA_IRRIGACAO": {
        "avaliar": motor.nivel_falha_irrigacao,
        "metrica": "umidade_solo_pct", "pior": "min",
        "descricao": f"Solo seco (<{LIMIAR_UMIDADE_SECA_PCT}%) e irrigação não acionou",
        "acao": "Ordem de manutenção aberta para o sistema de irrigação; gestor notificado",
        "recomendacao": "Inspecionar bomba, válvulas e linhas de gotejamento imediatamente",
    },
    "DEFICIT_HIDRICO": {
        "avaliar": motor.nivel_hidrico,
        "metrica": "umidade_solo_pct", "pior": "min",
        "descricao": "Umidade do solo baixa ou caindo rápido sem chuva",
        "acao": "Comando IRRIGACAO_ON enviado ao controlador do talhão (ciclo de 30 min)",
        "recomendacao": "Confirmar irrigação em campo e manter umidade entre 45-55%",
    },
    "TEMPERATURA_EXTREMA": {
        "avaliar": motor.nivel_temperatura,
        "metrica": "temperatura_c", "pior": "extremo",
        "descricao": f"Temperatura fora da faixa segura ({LIMIAR_TEMP_BAIXA_C}-{LIMIAR_TEMP_ALTA_C} °C)",
        "acao": "Frequência de leitura elevada para 5 min; alerta enviado ao gestor",
        "recomendacao": lambda pior: ("Calor: irrigar no fim da tarde e suspender aplicação de defensivos"
                                      if pior > 23 else
                                      "Frio/geada: irrigação noturna de proteção e cobertura das mudas sensíveis"),
    },
    "INFESTACAO": {
        "avaliar": motor.nivel_infestacao,
        "metrica": "perc_folhas_doentes", "pior": "max",
        "descricao": "Praga detectada pela câmera com folhas doentes acima do limite",
        "acao": "Talhão marcado como 'Monitoramento Intensivo'; equipe de campo acionada",
        "recomendacao": "Inspeção visual e aplicação de controle específico conforme receituário agronômico",
    },
    "MOVIMENTO_NOTURNO": {
        "avaliar": motor.nivel_movimento_noturno,
        "metrica": "movimento_detectado", "pior": "max",
        "descricao": "Movimento detectado pelo PIR durante a noite",
        "acao": "Registro de evento gravado; câmera do talhão acionada",
        "recomendacao": "Verificar presença de animais ou pragas noturnas na área",
    },
}


def detectar_episodios(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa leituras consecutivas que disparam a mesma regra em um episódio."""
    episodios = []
    for talhao_id, grupo in df.groupby("talhao_id"):
        grupo = grupo.sort_values("timestamp")
        ultimo_ts = grupo["timestamp"].iloc[-1]
        for nome, regra in REGRAS.items():
            nivel = regra["avaliar"](grupo)
            ativo = nivel.notna()
            # cada transição falso->verdadeiro abre um novo episódio
            id_episodio = (ativo != ativo.shift(fill_value=False)).cumsum()[ativo]
            for _, idx in id_episodio.groupby(id_episodio).groups.items():
                trecho = grupo.loc[idx]
                niveis = nivel.loc[idx]
                serie = trecho[regra["metrica"]]
                if regra["pior"] == "min":
                    pior = serie.min()
                elif regra["pior"] == "max":
                    pior = serie.max()
                else:
                    pior = serie.loc[(serie - 23).abs().idxmax()]  # mais distante do conforto térmico
                inicio, fim = trecho["timestamp"].iloc[0], trecho["timestamp"].iloc[-1]
                episodios.append({
                    "talhao_id": talhao_id,
                    "regra": nome,
                    "nivel": max(niveis, key=NIVEIS.get),
                    "inicio": inicio,
                    "fim": fim,
                    "duracao_h": round((fim - inicio).total_seconds() / 3600, 1),
                    "leituras": len(trecho),
                    "metrica": regra["metrica"],
                    "valor_pior": round(float(pior), 1),
                    "ativo_agora": bool(fim == ultimo_ts),
                    "descricao": regra["descricao"],
                    "acao_automatica": regra["acao"],
                    "recomendacao": (regra["recomendacao"](pior) if callable(regra["recomendacao"])
                                     else regra["recomendacao"]),
                })
    return pd.DataFrame(episodios).sort_values(["inicio", "talhao_id"]).reset_index(drop=True)


# ─────────────────────────────── B) Machine Learning ───────────────────────────────

def evento_critico(df: pd.DataFrame) -> pd.Series:
    return ((df["umidade_solo_pct"] < LIMIAR_UMIDADE_CRITICA_PCT)
            | (df["temperatura_c"] > LIMIAR_CALOR_CRITICO_C) | (df["temperatura_c"] < LIMIAR_GEADA_C)
            | motor.mascara_infestacao(df)).astype(int)


def criar_alvo(df: pd.DataFrame) -> pd.DataFrame:
    """alvo = 1 se houver evento crítico em alguma leitura das próximas 6h.
    Leituras cujo horizonte de 6h passa do fim dos dados ficam sem alvo."""
    partes = []
    for _, grupo in df.groupby("talhao_id"):
        g = grupo.sort_values("timestamp").copy()
        evento = evento_critico(g).to_numpy()
        tempos = g["timestamp"].to_numpy()
        # para cada leitura i, conta eventos nas leituras (i, fim_da_janela]
        acumulado = np.concatenate([[0], np.cumsum(evento)])
        fim_janela = np.searchsorted(tempos, tempos + pd.Timedelta(HORIZONTE_PREVISAO), side="right")
        eventos_futuros = acumulado[fim_janela] - acumulado[np.arange(len(g)) + 1]
        g["evento_critico_agora"] = evento
        g["alvo_evento_6h"] = (eventos_futuros > 0).astype(float)
        horizonte_ok = g["timestamp"] + pd.Timedelta(HORIZONTE_PREVISAO) <= g["timestamp"].max()
        g.loc[~horizonte_ok, "alvo_evento_6h"] = float("nan")
        partes.append(g)
    return pd.concat(partes)


def classe_risco(prob: float) -> str:
    if prob >= 0.6:
        return "ALTO"
    if prob >= 0.3:
        return "MEDIO"
    return "BAIXO"


def treinar_modelo(df: pd.DataFrame):
    campo = df[(df["fonte"] == "simulador_campo") & df["alvo_evento_6h"].notna()]
    corte = campo["timestamp"].min().normalize() + pd.Timedelta(days=DIAS_TREINO)
    treino, teste = campo[campo["timestamp"] < corte], campo[campo["timestamp"] >= corte]

    modelo = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=3,
                                    class_weight="balanced", random_state=42)
    modelo.fit(treino[FEATURES], treino["alvo_evento_6h"].astype(int))

    y_true = teste["alvo_evento_6h"].astype(int)
    y_pred = modelo.predict(teste[FEATURES])
    # baseline: "vai ter evento crítico nas próximas 6h se já tem agora" (o que uma regra faria)
    y_base = teste["evento_critico_agora"]

    def metricas(y_hat):
        return {
            "acuracia": round(accuracy_score(y_true, y_hat), 3),
            "precisao": round(precision_score(y_true, y_hat, zero_division=0), 3),
            "recall": round(recall_score(y_true, y_hat, zero_division=0), 3),
            "f1": round(f1_score(y_true, y_hat, zero_division=0), 3),
        }

    importancias = sorted(zip(FEATURES, modelo.feature_importances_), key=lambda x: -x[1])
    relatorio = {
        "modelo": "RandomForestClassifier(n_estimators=200, max_depth=8, class_weight='balanced')",
        "alvo": f"evento crítico nas próximas {HORIZONTE_PREVISAO} "
                f"(umidade<{LIMIAR_UMIDADE_CRITICA_PCT}% | temp>{LIMIAR_CALOR_CRITICO_C}°C | "
                f"temp<{LIMIAR_GEADA_C}°C | praga com folhas doentes>{LIMIAR_FOLHAS_DOENTES_PCT}%)",
        "divisao": f"temporal — treino antes de {corte.date()}, teste a partir de {corte.date()}",
        "amostras_treino": int(len(treino)),
        "amostras_teste": int(len(teste)),
        "proporcao_positivos_teste": round(float(y_true.mean()), 3),
        "metricas_modelo": metricas(y_pred),
        "metricas_baseline_regra_atual": metricas(y_base),
        "matriz_confusao_modelo": {
            "linhas=real, colunas=previsto": [0, 1],
            "valores": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
        },
        "importancia_features": {nome: round(float(v), 3) for nome, v in importancias},
    }
    return modelo, relatorio


# ─────────────────────────────── Decisão combinada ───────────────────────────────

def montar_status(df: pd.DataFrame, episodios: pd.DataFrame) -> dict:
    status = {}
    for talhao_id, grupo in df.groupby("talhao_id"):
        ultima = grupo.sort_values("timestamp").iloc[-1]
        ativos = episodios[(episodios["talhao_id"] == talhao_id) & episodios["ativo_agora"]]
        # mais grave primeiro; no empate, a ordem do dicionário REGRAS define a prioridade
        prioridade = {nome: i for i, nome in enumerate(REGRAS)}
        ativos = ativos.assign(_g=-ativos["nivel"].map(NIVEIS), _p=ativos["regra"].map(prioridade))
        ativos = ativos.sort_values(["_g", "_p"])

        nivel_regra = ativos["nivel"].iloc[0] if len(ativos) else None
        risco = ultima["risco_previsto"]
        nivel_ml = {"ALTO": "CRITICO", "MEDIO": "ATENCAO"}.get(risco)
        candidatos = [n for n in (nivel_regra, nivel_ml) if n]
        nivel_final = max(candidatos, key=NIVEIS.get) if candidatos else "NORMAL"

        recomendacoes = ativos["recomendacao"].tolist()
        if not recomendacoes and risco in ("ALTO", "MEDIO"):
            recomendacoes.append("Sem alerta ativo, mas o modelo prevê risco nas próximas 6h: "
                                 "antecipar vistoria e checar irrigação")
        if not recomendacoes:
            recomendacoes.append("Condições dentro do esperado — manter monitoramento de rotina")

        status[talhao_id] = {
            "ultima_leitura": ultima["timestamp"].strftime("%Y-%m-%d %H:%M"),
            "fonte": ultima["fonte"],
            "temperatura_c": float(ultima["temperatura_c"]),
            "umidade_solo_pct": float(ultima["umidade_solo_pct"]),
            "luminosidade_pct": float(ultima["luminosidade_pct"]),
            "perc_folhas_doentes": float(ultima["perc_folhas_doentes"]),
            "irrigacao_ligada": bool(ultima["irrigacao_ligada"]),
            "prob_evento_6h": round(float(ultima["prob_evento_6h"]), 3),
            "risco_previsto": risco,
            "alertas_ativos": ativos[["regra", "nivel", "valor_pior", "duracao_h"]].to_dict("records"),
            "nivel_final": nivel_final,
            "recomendacao_priorizada": recomendacoes,
        }
    return status


def gravar_log_acoes(episodios: pd.DataFrame):
    with open(REFINED_DIR / "acoes_automaticas.log", "w", encoding="utf-8") as f:
        for ep in episodios.itertuples():
            f.write(f"{ep.inicio:%Y-%m-%d %H:%M} | {ep.talhao_id} | {ep.nivel:<7} | {ep.regra:<19} | {ep.acao_automatica}\n")


def gravar_relatorio(status: dict, relatorio_ml: dict, episodios: pd.DataFrame):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    linhas = [f"# Relatório de Apoio à Decisão — AgroSmart (gerado em {agora})", ""]
    linhas.append(f"Episódios de alerta no período: **{len(episodios)}** "
                  f"({(episodios['nivel'] == 'CRITICO').sum()} críticos). "
                  f"Modelo preditivo — F1 no teste: **{relatorio_ml['metricas_modelo']['f1']}** "
                  f"(baseline regra: {relatorio_ml['metricas_baseline_regra_atual']['f1']}).")
    linhas.append("")
    for talhao_id, s in sorted(status.items(), key=lambda kv: -NIVEIS.get(kv[1]["nivel_final"], 0)):
        linhas.append(f"## {talhao_id} — {s['nivel_final']}")
        linhas.append(f"- Última leitura ({s['ultima_leitura']}): {s['temperatura_c']} °C, "
                      f"umidade do solo {s['umidade_solo_pct']}%, luminosidade {s['luminosidade_pct']}%, "
                      f"folhas doentes {s['perc_folhas_doentes']}%")
        linhas.append(f"- Risco previsto para as próximas 6h: **{s['risco_previsto']}** "
                      f"(probabilidade {s['prob_evento_6h']:.0%})")
        alertas = ", ".join(f"{a['regra']} ({a['nivel']})" for a in s["alertas_ativos"]) or "nenhum"
        linhas.append(f"- Alertas ativos: {alertas}")
        linhas.append("- Recomendação:")
        linhas.extend(f"  {i}. {r}" for i, r in enumerate(s["recomendacao_priorizada"], 1))
        linhas.append("")
    linhas.append("*Decisão final cabe ao responsável técnico do talhão.*")
    (REFINED_DIR / "relatorio_decisao.md").write_text("\n".join(linhas), encoding="utf-8")


def main():
    caminho = TRUSTED_DIR / "leituras_processadas.csv"
    if not caminho.exists():
        raise SystemExit("Rode antes: python processamento/processar_dados.py")
    df = pd.read_csv(caminho, parse_dates=["timestamp"])
    REFINED_DIR.mkdir(parents=True, exist_ok=True)

    # A) regras
    episodios = detectar_episodios(df)
    episodios.to_csv(REFINED_DIR / "alertas.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    gravar_log_acoes(episodios)
    print(f"[automacao] {len(episodios)} episódios de alerta "
          f"({episodios['nivel'].value_counts().to_dict()}) -> refined/alertas.csv")

    # B) machine learning
    df = criar_alvo(df)
    modelo, relatorio_ml = treinar_modelo(df)
    df["prob_evento_6h"] = modelo.predict_proba(df[FEATURES])[:, 1].round(3)
    df["risco_previsto"] = df["prob_evento_6h"].map(classe_risco)
    joblib.dump(modelo, REFINED_DIR / "modelo_risco.joblib")
    with open(REFINED_DIR / "metricas_modelo.json", "w", encoding="utf-8") as f:
        json.dump(relatorio_ml, f, ensure_ascii=False, indent=2)
    colunas_pred = ["timestamp", "talhao_id", "fonte", "evento_critico_agora",
                    "alvo_evento_6h", "prob_evento_6h", "risco_previsto"]
    df[colunas_pred].to_csv(REFINED_DIR / "predicoes_risco.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    m, b = relatorio_ml["metricas_modelo"], relatorio_ml["metricas_baseline_regra_atual"]
    print(f"[automacao] modelo treinado: F1={m['f1']} recall={m['recall']} precisao={m['precisao']} "
          f"(baseline regra atual: F1={b['f1']} recall={b['recall']})")

    # decisão combinada
    status = montar_status(df, episodios)
    with open(REFINED_DIR / "status_talhoes.json", "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    gravar_relatorio(status, relatorio_ml, episodios)

    print("[automacao] status atual por talhão:")
    for talhao_id, s in status.items():
        print(f"  - {talhao_id}: {s['nivel_final']:<8} risco 6h {s['risco_previsto']:<5} "
              f"({s['prob_evento_6h']:.0%}) -> {s['recomendacao_priorizada'][0]}")
    print("[automacao] saídas em dados/refined/: alertas.csv, acoes_automaticas.log, predicoes_risco.csv, "
          "metricas_modelo.json, status_talhoes.json, relatorio_decisao.md")


if __name__ == "__main__":
    main()
