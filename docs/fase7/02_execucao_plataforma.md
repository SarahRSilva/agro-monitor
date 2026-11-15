# 2. Execução da plataforma — sistema funcional (20%)

## 2.1 Como executar

**Opção A — containers (modo produto, execução contínua):**

```bash
docker compose up --build -d          # sobe "pipeline" (ciclo a cada 5 min) e "dashboard"
docker compose ps                     # ambos devem ficar (healthy)
open http://localhost:8501            # dashboard
docker compose logs -f pipeline       # acompanhar os ciclos
AGRO_INTERVALO_S=30 docker compose up -d   # ciclos a cada 30 s (bom para demonstração)
docker compose down                   # parar (use -v para apagar também os dados)
```

**Opção B — local (Python 3.11+):**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_plataforma.py                                  # 1 ciclo completo
python run_plataforma.py --loop --intervalo 60            # execução contínua
streamlit run dashboard/app.py                            # dashboard
```

## 2.2 Funcionamento do sistema

| Etapa | O que faz | Entrada | Saída |
|---|---|---|---|
| **Entrada de dados** | Simulador de campo (5 talhões) + captura serial do Arduino no TinkerCad | — | `dados/raw/sensores_campo.csv`, `dados/raw/tinkercad_serial.txt` |
| **Processamento** | Deduplica, valida faixas físicas, imputa campos vazios, cria features (médias 3h, tendência 6h, chuva 24h, extremos 24h, período do dia) | raw | `dados/trusted/leituras_processadas.csv`, `raw/rejeitados/rejeitados.csv`, `qualidade_dados.json` |
| **Automação baseada em decisões** | 5 regras graduadas → episódios com ação automática; Random Forest → risco 6h; decisão combinada → nível final e recomendação | trusted | `alertas.csv`, `acoes_automaticas.log`, `predicoes_risco.csv`, `status_talhoes.json`, `relatorio_decisao.md` |
| **Apoio à decisão (IA)** | Relatório em linguagem natural por talhão | refined | `relatorios_ia/<talhão>_<data>.md` |
| **Análise de processo** | Event log, variantes, DFG, gargalos | refined + monitoramento | `refined/processo/*` |
| **Saída** | Dashboard (7 abas), alertas, relatórios, log de ações, CSVs para BI | refined | http://localhost:8501 |

Ações automáticas por regra:

| Regra | Dispara quando | Ação automática |
|---|---|---|
| FALHA_IRRIGACAO | solo < 30% **e** bomba desligada **e** chuva 24h < 2 mm | Abre ordem de manutenção; notifica o gestor |
| DEFICIT_HIDRICO | solo < 20% (crítico) / < 30% sem chuva / queda > 6 p.p. em 6h | Envia `IRRIGACAO_ON` ao controlador (ciclo de 30 min) |
| TEMPERATURA_EXTREMA | > 38 °C ou < 3 °C (crítico) / fora de 12–35 °C | Eleva a frequência de leitura para 5 min; alerta o gestor |
| INFESTACAO | praga detectada **e** folhas doentes > 30% (crítico) / > 15% | Monitoramento intensivo; aciona a equipe de campo |
| MOVIMENTO_NOTURNO | PIR = 1 **e** luminosidade < 10% | Grava evento; aciona a câmera |

## 2.3 Exemplo de entrada e saída (rastreando o TAL-02, irrigação quebrada)

**Entrada** — leitura bruta do sensor (`evidencias/execucao/exemplos/entrada_sensores_campo.csv`):

```csv
timestamp,talhao_id,sensor_id,temperatura_c,umidade_solo_pct,luminosidade_pct,movimento_detectado,irrigacao_ligada,precipitacao_mm,perc_folhas_doentes,praga_detectada
2026-10-04 23:30:00,TAL-02,SNS-02,21.8,3.5,0.0,0,0,0.0,7.6,nenhuma
```

**Entrada inválida rejeitada com motivo** (`exemplos/rejeitados.csv`): a leitura não some — fica auditável,
ex.: `umidade_solo_pct=137.4 fora da faixa [0, 100]`.

**Processado (trusted)** — a mesma leitura com features (`exemplos/processado_trusted.csv`):

```
umidade_media_3h=3.2  tendencia_umidade_6h=+0.5  chuva_24h_mm=0.0  temp_max_24h=34.1  temp_min_24h=18.1  periodo_dia=noite
```

**Decisão automática** (`exemplos/status_talhoes.json` e `relatorio_decisao.md`):

```
## TAL-02 — CRITICO
- Última leitura (2026-10-04 23:30): 21.8 °C, umidade do solo 3.5%, luminosidade 0.0%, folhas doentes 7.6%
- Risco previsto para as próximas 6h: ALTO (probabilidade 92%)
- Alertas ativos: FALHA_IRRIGACAO (CRITICO), DEFICIT_HIDRICO (CRITICO)
- Recomendação:
  1. Inspecionar bomba, válvulas e linhas de gotejamento imediatamente
  2. Confirmar irrigação em campo e manter umidade entre 45-55%
```

**Ações executadas** (`exemplos/acoes_automaticas.log`):

```
2026-10-01 06:00 | TAL-02 | CRITICO | FALHA_IRRIGACAO     | Ordem de manutenção aberta para o sistema de irrigação; gestor notificado
2026-10-01 06:00 | TAL-02 | CRITICO | DEFICIT_HIDRICO     | Comando IRRIGACAO_ON enviado ao controlador do talhão (ciclo de 30 min)
```

**Relatório da IA Generativa** (`exemplos/relatorio_ia_TAL-02.md`): identifica déficit hídrico de alta prioridade,
os alertas críticos ativos e o risco de 92%, e recomenda inspecionar a bomba antes de programar a irrigação.

## 2.4 Evidências da execução

| Evidência | Arquivo |
|---|---|
| Log completo de um ciclo (terminal) | `evidencias/execucao/01_execucao_run_plataforma.txt` |
| Exemplos de entrada e saída de cada camada | `evidencias/execucao/exemplos/` |
| Containers rodando e saudáveis | `evidencias/monitoramento/01_docker_compose_ps.txt` |
| Ciclos contínuos dentro do container | `evidencias/monitoramento/07_docker_logs_pipeline.txt` |
| Prints do dashboard (Fase 6) | `docs/prints/01..06_*.png` |
| Prints das abas novas (Fase 7) | `docs/prints/10_monitoramento.png`, `11_processo.png` *(capturar — ver checklist no README)* |

Resumo do ciclo (semente 42), extraído do log:

```
[processamento] 1706 linhas recebidas (simulador_campo: 1686, tinkercad: 20)
[processamento] 6 duplicadas removidas · 5 rejeitadas · 10 imputadas · 1695 válidas
[automacao] 55 episódios de alerta ({'AVISO': 36, 'CRITICO': 18, 'ATENCAO': 1})
[automacao] modelo treinado: F1=0.949 recall=0.924 precisao=0.976 (baseline regra atual: F1=0.887 recall=0.809)
  - TAL-01: NORMAL   risco 6h BAIXO (7%)   · TAL-02: CRITICO risco 6h ALTO (92%)
  - TAL-03: ATENCAO  risco 6h MEDIO (33%)  · TAL-04: CRITICO risco 6h ALTO (92%)
  - TAL-05: CRITICO  risco 6h ALTO  (89%)  · TAL-TC: ATENCAO risco 6h MEDIO (33%)
[ia] 6 relatório(s) de apoio à decisão -> refined/relatorios_ia/
[mineracao] event log: 55 casos, 246 eventos, 16 variantes
Ciclo 1 finalizado com status=ok em 2.6s
```
