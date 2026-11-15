# 4. Monitoramento e execução automatizada (10%)

## 4.1 Execução contínua

`run_plataforma.py --loop` roda a plataforma sem intervenção humana:

- um **ciclo completo** (coleta → processamento → automação → IA → mineração) a cada `AGRO_INTERVALO_S`
  segundos (padrão 300); cada ciclo simula um lote novo de sensores;
- **falha isolada**: se uma etapa falha, o ciclo é marcado como erro, registrado, e o próximo ciclo roda normalmente;
- **parada segura**: ao receber `SIGTERM` (ex.: `docker compose stop`) termina o ciclo atual antes de sair;
- no Docker, o serviço `pipeline` roda nesse modo com `restart: unless-stopped`.

## 4.2 O que é monitorado

| Instrumento | Arquivo | Conteúdo | Quem usa |
|---|---|---|---|
| **Log da aplicação** | `logs/agrosmart.log` (+ stdout) | Uma linha JSON por evento: horário, nível, componente, mensagem, `run_id`, etapa, duração. Rotação a cada 2 MB (3 arquivos) | `docker compose logs`, `jq`, Loki/ELK |
| **Status de execução** | `dados/monitoramento/execucoes.jsonl` | Uma linha por etapa de cada ciclo: início, fim, duração, `ok`/`erro`, mensagem de erro | Aba Monitoramento, mineração de processos |
| **Indicadores** | `dados/monitoramento/status.json` | Último ciclo, último sucesso, histórico (ciclos ok/erro, disponibilidade %) e indicadores de negócio | Healthcheck, dashboard |
| **Saúde** | `monitoramento/healthcheck.py` | 4 verificações → `saudavel: true/false` (código de saída 0/1) | `HEALTHCHECK` do Docker, CI |

### Indicadores de funcionamento (`status.json → indicadores`)

| Indicador | Por que importa |
|---|---|
| `linhas_recebidas`, `linhas_processadas`, `taxa_rejeicao_pct`, `duplicadas_removidas` | Saúde da **coleta** — um sensor com defeito aparece como aumento de rejeição |
| `ultima_leitura_dados` | Atualidade dos dados de campo |
| `f1_modelo` vs `f1_baseline` | **Drift** do modelo — se o F1 cair abaixo do baseline, o modelo deixou de agregar valor |
| `episodios_alerta`, `episodios_criticos`, `alertas_ativos` | Volume operacional |
| `talhoes_monitorados`, `talhoes_criticos`, `talhoes_atencao` | Situação do negócio |
| `historico.disponibilidade_pct`, `ciclos_ok`, `ciclos_erro` | Confiabilidade da plataforma |
| duração por etapa (`execucoes.jsonl`) | Desempenho e gargalos técnicos |

### Regras do healthcheck

| Verificação | Falha quando |
|---|---|
| `status_existe` | Nenhum ciclo jamais rodou |
| `ultimo_ciclo_ok` | O último ciclo terminou com erro |
| `dados_recentes` | O último sucesso tem mais de `AGRO_MAX_IDADE_MIN` minutos (padrão 15) — pega o pipeline travado |
| `saidas_refined` | Algum arquivo essencial (trusted, alertas, status, predições) não existe |

## 4.3 Como acompanhar o sistema

| Pergunta | Como responder |
|---|---|
| Está tudo rodando? | `docker compose ps` → coluna STATUS `(healthy)`; ou aba **🩺 Monitoramento** do dashboard |
| Por que não está saudável? | `docker exec agrosmart_pipeline python monitoramento/healthcheck.py` → mostra qual verificação falhou |
| O que está acontecendo agora? | `docker compose logs -f pipeline` |
| Quando falhou e por quê? | Aba Monitoramento → tabela de erros; ou `grep '"erro"' dados/monitoramento/execucoes.jsonl` |
| A plataforma está ficando lenta? | Aba Monitoramento → gráfico de duração por ciclo/etapa; aba Processo → etapas do pipeline |
| Quantos recursos usa? | `docker stats agrosmart_pipeline agrosmart_dashboard` |
| Filtrar o log por ciclo | `jq 'select(.run_id=="<id>")' logs/agrosmart.log` |

## 4.4 Evidências (stack em containers, ciclos a cada 20 s)

Arquivos em `evidencias/monitoramento/`:

| Arquivo | O que mostra |
|---|---|
| `01_docker_compose_ps.txt` | `agrosmart_pipeline` e `agrosmart_dashboard` **Up (healthy)** |
| `02_docker_health_pipeline.json` | Histórico do `HEALTHCHECK` do Docker (saídas do `healthcheck.py`) |
| `03_healthcheck.json` | Diagnóstico completo com indicadores |
| `04_status.json` | Status: 7 ciclos — **6 ok, 1 erro, disponibilidade 85,7%** |
| `05_execucoes.jsonl` | 32 registros de etapa (inclui a falha) |
| `06_agrosmart_log.jsonl` | Log estruturado da aplicação |
| `07_docker_logs_pipeline.txt` | Saída do container |
| `08_docker_stats.txt` | Consumo: pipeline ~18 MiB, dashboard ~71 MiB (limite 1 GiB) |

### Teste de falha controlada

Para provar que o monitoramento detecta problemas, corrompemos o arquivo serial do TinkerCad dentro do container
com a plataforma rodando:

```bash
docker exec agrosmart_pipeline sh -c 'printf "cabecalho_invalido\n1,2\n" > dados/raw/tinkercad_serial.txt'
```

Resultado observado:

1. O ciclo 3 falhou na etapa **Processamento** e foi registrado:
   ```json
   {"run_id": "20261115-170904-2f3ca2", "ciclo": 3, "etapa": "Processamento", "status": "erro",
    "erro": "EtapaFalhou: processamento/processar_dados.py saiu com código 1: ... KeyError: 'millis'", "duracao_s": 0.449}
   ```
2. O log registrou em nível `ERROR`:
   `Etapa 'Processamento' erro em 0.449s — EtapaFalhou: ... KeyError: 'millis'` e `Ciclo 3 finalizado com status=erro`.
3. O healthcheck passou a responder **`"saudavel": false`** com `"ultimo_ciclo_ok": false`.
4. Restauramos o arquivo; o ciclo 4 rodou normalmente e a plataforma voltou a **healthy**, sem reiniciar o container.
5. A disponibilidade registrada caiu para **85,7%** (6 de 7 ciclos) — o incidente fica no histórico.

## 4.5 Próximos passos

Exportar os indicadores no formato Prometheus (`/metrics`) para um Grafana com alertas (ex.: disponibilidade < 95%,
`f1_modelo < f1_baseline`, taxa de rejeição > 2%) e enviar o log JSON para Loki/ELK.
