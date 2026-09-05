# AgroSmart — Entrega da Atividade Acadêmica (FIAP 4ESOA)

## Visão Geral

Este pacote complementa o repositório [`G3n4r00/agro_monitor`](https://github.com/G3n4r00/agro_monitor)
com os artefatos exigidos pela atividade, organizados em duas fases:

- **Fase 4** — Pipeline de dados com streaming, containerização com Docker e Business Model Canvas (v1).
- **Fase 5** — Arquitetura de Data Lake, processo de ingestão/manutenção de dados, IA Generativa
  como apoio à decisão e evolução do modelo de negócio (Canvas v2).

---

# Fase 4

## 1. Pipeline de Dados com Streaming (30%)

### Arquitetura do Pipeline

```
[Sensores IoT] → [Kafka Producer] → [Tópico: sensor-readings] → [Motor de Regras] → [Tópico: alerts] → [API Flask] → [Dashboard]
```

### Opção A — Simulação sem Kafka (execução imediata)

```bash
pip install rich
python pipeline/pipeline_simulado.py
```

O script `pipeline_simulado.py` simula o comportamento completo de um pipeline Kafka usando `queue.Queue` e threads Python, mostrando em tempo real:
- Leituras geradas pelo "producer" (sensores)
- Avaliação das 3 regras booleanas pelo "consumer" (motor de regras)
- Alertas publicados no "tópico" de saída

### Opção B — Kafka real via Docker

```bash
cd docker
docker compose up -d zookeeper kafka kafka-ui sensor-producer rules-engine
```

Acesse o Kafka UI em `http://localhost:8080` para visualizar os tópicos `sensor-readings` e `alerts` em tempo real.

### Configuração dos tópicos Kafka

Ver `pipeline/kafka-topics.yml` para especificação de partições, retenção e exemplos de mensagem.

---

## 2. Containerização com Docker (30%)

### Estrutura dos containers

| Container | Imagem | Porta | Função |
|---|---|---|---|
| `agro_zookeeper` | confluentinc/cp-zookeeper:7.6.0 | — | Coordenação do Kafka |
| `agro_kafka` | confluentinc/cp-kafka:7.6.0 | 9092 | Broker de mensagens |
| `agro_kafka_ui` | provectuslabs/kafka-ui | 8080 | Visualização dos tópicos |
| `agro_sensor_producer` | python:3.11-slim (build local) | — | Geração de dados dos sensores |
| `agro_rules_engine` | python:3.11-slim (build local) | — | Motor de regras e alertas |
| `agro_api` | python:3.11-slim (build local) | 5001 (host) -> 5000 (container) | API Flask + Dashboard (porta alterada de 5000 para 5001 para evitar conflito com AirPlay no macOS) |

### Como executar

```bash
# Clonar o repo original e copiar os arquivos Python para docker/api/
git clone https://github.com/SarahRSilva/agro-monitor
cp agro-monitor/main.py agro-monitor/gerador.py agro-monitor/regras.py docker/api/

# Subir toda a stack
cd docker
docker compose up --build -d

# Verificar status
docker compose ps

# Logs em tempo real
docker compose logs -f
```

### Endpoints disponíveis

- `http://localhost:5001` — Dashboard web do AgroSmart (mapeado de 5000 do container para evitar colisão de porta 5000 com AirPlay no macOS)
- `http://localhost:5001/api/dados` — API JSON com leituras e alertas
- `http://localhost:8080` — Kafka UI (tópicos em tempo real)

### Parar os containers

```bash
docker compose down
```

---

## 3. Modelo de Negócio com Canvas v1 (40%)

O Business Model Canvas original do AgroSmart está no arquivo `canvas/business_model_canvas.md`
e resumido abaixo. **Este canvas foi atualizado na Fase 5** — ver `business-model/business_model_canvas_v2.md`.

### Proposta de Valor

O AgroSmart entrega **monitoramento agrícola em tempo real** para produtores rurais via sensores IoT e um motor de regras inteligente que detecta infestações, deficiência hídrica e anomalias climáticas antes que causem perdas significativas. A solução roda em cloud, é acessada via browser (sem instalação) e gera alertas classificados por severidade com recomendações de ação.

### Modelo de Receita (SaaS + Hardware)

- **Assinatura mensal por talhão** (modelo SaaS escalável)
- **Venda de kits de sensores** homologados para a plataforma
- **Add-ons** de análise avançada e integração com ERPs agrícolas

### Segmentos

Pequenos e médios produtores → cooperativas → agroindústrias → centros de pesquisa.

---

# Fase 5

A Fase 5 evolui a arquitetura para um **Data Lake em camadas**, incorpora **IA Generativa** como
apoio à decisão e atualiza o **modelo de negócio** para incluir monetização baseada em dados. Ver
detalhes completos em cada artefato listado abaixo.

## 4. Arquitetura de Dados com Data Lake

Diagrama da arquitetura (fontes → ingestão → camadas Raw/Trusted/Refined → consumo) e explicação
textual de cada camada em [`data-lake/architecture.md`](data-lake/architecture.md).

> **Versão executável:** a pasta [`datalake-demo/`](datalake-demo/) implementa essa arquitetura de
> verdade em Python puro (sem dependências externas) — rode `python3 datalake-demo/run_pipeline.py`
> para ver a ingestão, validação, agregação e o relatório de IA rodando de ponta a ponta. Detalhes em
> [`datalake-demo/README.md`](datalake-demo/README.md).

### Como rodar o Data Lake Demo

**Importante:** os 4 scripts precisam estar dentro de `datalake-demo/scripts/`, e não soltos
direto em `datalake-demo/` — o `run_pipeline.py` procura especificamente em
`datalake-demo/scripts/01_ingestao.py`. A pasta `ingestion/samples/` também precisa existir um
nível acima de `datalake-demo/`, pois `01_ingestao.py` lê os exemplos de lá. A estrutura correta é:

```
agro_monitor_entrega/
├── ingestion/
│   └── samples/                ← os scripts leem daqui
└── datalake-demo/
    ├── run_pipeline.py
    └── scripts/                 ← os 4 .py precisam estar AQUI DENTRO
        ├── 01_ingestao.py
        ├── 02_camada_trusted.py
        ├── 03_camada_refined.py
        └── 04_ia_generativa.py
```

Com a estrutura correta, rode o pipeline completo:

```bash
cd datalake-demo
python3 run_pipeline.py
```

Isso executa, em sequência: ingestão (popula `datalake/raw/`, incluindo uma leitura inválida de
propósito para testar a rejeição) → validação/limpeza (`datalake/trusted/`) → agregação por
talhão (`datalake/refined/resumo_talhoes.json`) → geração do relatório de IA por talhão
(`datalake/refined/relatorios_ia/`).

Também é possível rodar cada etapa isoladamente ou plugar uma IA real (Anthropic) no lugar do
motor de regras simulado — ver instruções completas em
[`datalake-demo/README.md`](datalake-demo/README.md).

## 5. Processo de Ingestão, Administração e Manutenção de Dados

Diagrama de sequência do fluxo de ingestão, exemplos de dados ingeridos e a estratégia de
validação/retenção/backup em [`ingestion/ingestion_flow.md`](ingestion/ingestion_flow.md), com
exemplos em `ingestion/samples/`:
- `leitura_sensor.json` — leitura pontual de sensor IoT
- `leituras_solo.csv` — lote diário de leituras de solo
- `deteccao_imagem.json` — metadados de detecção de praga via visão computacional

## 6. Inteligência Artificial Generativa para Apoio à Decisão

Descrição do funcionamento, contexto utilizado (dados da camada Refinada) e exemplo completo de
relatório gerado em [`ia-generativa/decision_support.md`](ia-generativa/decision_support.md).

## 7. Modelo de Negócio e Inteligência de Dados (Canvas v2)

Canvas atualizado com monetização baseada em dados (score de risco para seguradoras, relatórios
agregados, API paga de insights) e roteiro do vídeo de 2–3 minutos em
[`business-model/business_model_canvas_v2.md`](business-model/business_model_canvas_v2.md).

---

## Estrutura de Arquivos

```
agro_monitor_entrega/
├── README.md                              ← este arquivo
│
│   # Fase 4
├── pipeline/
│   ├── pipeline_simulado.py               ← simulação sem Kafka (executa direto)
│   └── kafka-topics.yml                   ← spec dos tópicos Kafka
├── docker/
│   ├── docker-compose.yml                 ← orquestração completa
│   ├── producer/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── producer.py                    ← simula sensores → Kafka
│   ├── rules-engine/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── consumer.py                    ← regras booleanas → alertas
│   └── api/
│       ├── Dockerfile
│       └── requirements.txt
├── canvas/
│   └── business_model_canvas.md           ← Canvas v1 (Fase 4)
│
│   # Fase 5
├── data-lake/
│   └── architecture.md                    ← diagrama (Mermaid) + explicação das camadas
├── datalake-demo/                         ← IMPLEMENTAÇÃO EXECUTÁVEL da arquitetura acima
│   ├── README.md                          ← como rodar (python3 run_pipeline.py)
│   ├── run_pipeline.py
│   └── scripts/
│       ├── 01_ingestao.py
│       ├── 02_camada_trusted.py
│       ├── 03_camada_refined.py
│       └── 04_ia_generativa.py
├── ingestion/
│   ├── ingestion_flow.md                  ← diagrama de sequência + estratégia de manutenção
│   └── samples/
│       ├── leitura_sensor.json
│       ├── leituras_solo.csv
│       └── deteccao_imagem.json
├── ia-generativa/
│   └── decision_support.md                ← prompt, contexto usado e exemplo de relatório gerado
└── business-model/
    └── business_model_canvas_v2.md        ← Canvas v2 (Fase 5) + roteiro do vídeo
```

---

## Time

| Nome | RM | Turma |
|---|---|---|
| Gabriel Genaro Dalaqua | 551986 | 4ESOA |
| Alairton Rocha Scabelli | 551454 | 4ESOA |
| Carolina Nascimento Amorim | 97930 | 4ESOA |
| Eduardo Marins | 551892 | 4ESOA |
| Sarah Ribeiro da Silva | 97747 | 4ESOA |