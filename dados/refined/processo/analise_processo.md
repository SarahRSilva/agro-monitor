# Análise de processo — AgroSmart (gerado automaticamente)

**Event log operacional:** 55 casos (ocorrências), 246 eventos, 9 atividades distintas, **16 variantes**.

## Principais achados

- **Variante principal** (32.7% dos casos): `Reincidência detectada → Alerta disparado → Ação automática executada → Condição normalizada`. As 3 variantes mais comuns cobrem 70.9% dos casos.
- **Gargalo** (maior tempo acumulado de espera): `Escalado para CRÍTICO → Condição normalizada` — 13 ocorrências, média de 10.15h, 132.0h acumuladas.
- **Resolução mais lenta:** FALHA_IRRIGACAO (45.5h em média entre o alerta e a normalização).
- **Casos em aberto** no fim da janela: 6 (10.9%).
- **Retrabalho / reincidência:** TEMPERATURA_EXTREMA reincide em 78.6% dos casos (mesma regra em menos de 24h).
- **Antecipação pelo ML:** 61.1% das ocorrências críticas tiveram risco ALTO previsto antes do alerta, com 4.7h de antecedência média.
- **Pipeline técnico:** 4 ciclo(s), 0 com erro, 2.33s por ciclo; etapa mais lenta: **Mineração de processos** (44.3% do tempo do ciclo).

## Variantes (top 10)

| variante | casos | pct_casos | regras |
|---|---|---|---|
| Reincidência detectada → Alerta disparado → Ação automática executada → Condição normalizada | 18 | 32.7 | MOVIMENTO_NOTURNO |
| Alerta disparado → Ação automática executada → Condição normalizada | 14 | 25.5 | DEFICIT_HIDRICO, MOVIMENTO_NOTURNO |
| Risco previsto pelo ML → Reincidência detectada → Alerta disparado → Ação automática executada → Gestor notificado → Escalado para CRÍTICO → Condição normalizada | 7 | 12.7 | TEMPERATURA_EXTREMA |
| Alerta disparado → Ação automática executada → Escalado para CRÍTICO → Condição normalizada | 2 | 3.6 | DEFICIT_HIDRICO |
| Risco previsto pelo ML → Reincidência detectada → Alerta disparado → Ação automática executada → Condição normalizada | 2 | 3.6 | DEFICIT_HIDRICO |
| Reincidência detectada → Alerta disparado → Ação automática executada → Gestor notificado → Escalado para CRÍTICO → Condição normalizada | 2 | 3.6 | TEMPERATURA_EXTREMA |
| Risco previsto pelo ML → Reincidência detectada → Alerta disparado → Ação automática executada → Ocorrência em aberto | 1 | 1.8 | DEFICIT_HIDRICO |
| Alerta disparado → Ação automática executada → Gestor notificado → Ordem de manutenção aberta → Condição normalizada | 1 | 1.8 | FALHA_IRRIGACAO |
| Risco previsto pelo ML → Alerta disparado → Ação automática executada → Gestor notificado → Ordem de manutenção aberta → Ocorrência em aberto | 1 | 1.8 | FALHA_IRRIGACAO |
| Risco previsto pelo ML → Alerta disparado → Ação automática executada → Gestor notificado → Escalado para CRÍTICO → Condição normalizada | 1 | 1.8 | TEMPERATURA_EXTREMA |

## Desempenho por regra

| regra | casos | criticos | pct_em_aberto | resolucao_media_h | resolucao_mediana_h | resolucao_max_h | pct_reincidencia | pct_escalados | pct_antecipado_ml | antecedencia_ml_media_h |
|---|---|---|---|---|---|---|---|---|---|---|
| MOVIMENTO_NOTURNO | 29 | 0 | 3.4 | 0.6 | 0.5 | 1.5 | 65.5 | 0.0 | — | — |
| TEMPERATURA_EXTREMA | 14 | 12 | 14.3 | 9.9 | 9.5 | 14.0 | 78.6 | 85.7 | 71.4 | 3.8 |
| DEFICIT_HIDRICO | 9 | 3 | 11.1 | 8.4 | 3.2 | 47.0 | 33.3 | 22.2 | 33.3 | 4.2 |
| FALHA_IRRIGACAO | 2 | 2 | 50.0 | 45.5 | 45.5 | 45.5 | 0.0 | 0.0 | 50.0 | 6.0 |
| INFESTACAO | 1 | 1 | 100.0 | — | — | — | 0.0 | 100.0 | 0.0 | — |

## Etapas do pipeline

| atividade | execucoes | erros | duracao_media_s | duracao_p95_s | duracao_max_s | pct_tempo_ciclo |
|---|---|---|---|---|---|---|
| Coleta de dados | 4 | 0 | 0.04 | 0.05 | 0.05 | 1.5 |
| Processamento | 4 | 0 | 0.24 | 0.24 | 0.24 | 9.2 |
| Automação (regras + ML) | 4 | 0 | 0.97 | 0.97 | 0.98 | 37.0 |
| IA Generativa | 4 | 0 | 0.21 | 0.22 | 0.22 | 8.0 |
| Mineração de processos | 3 | 0 | 1.16 | 1.16 | 1.16 | 44.3 |
