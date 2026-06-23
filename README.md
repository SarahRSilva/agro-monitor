# AgroSmart — Entrega da Atividade Acadêmica (FIAP 4ESOA)

## Visão Geral

Este pacote complementa o repositório [`G3n4r00/agro_monitor`](https://github.com/G3n4r00/agro_monitor) com os três artefatos exigidos pela atividade.

---

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
| `agro_api` | python:3.11-slim (build local) | 5000 | API Flask + Dashboard |

### Como executar

```bash
# Clonar o repo original e copiar os arquivos Python para docker/api/
git clone https://github.com/G3n4r00/agro_monitor.git
cp agro_monitor/main.py agro_monitor/gerador.py agro_monitor/regras.py docker/api/

# Subir toda a stack
cd docker
docker compose up --build -d

# Verificar status
docker compose ps

# Logs em tempo real
docker compose logs -f
```

### Endpoints disponíveis

- `http://localhost:5000` — Dashboard web do AgroSmart
- `http://localhost:5000/api/dados` — API JSON com leituras e alertas
- `http://localhost:8080` — Kafka UI (tópicos em tempo real)

### Parar os containers

```bash
docker compose down
```

---

## 3. Modelo de Negócio com Canvas (40%)

O Business Model Canvas do AgroSmart está no arquivo `canvas/business_model_canvas.md` e resumido abaixo.

### Proposta de Valor

O AgroSmart entrega **monitoramento agrícola em tempo real** para produtores rurais via sensores IoT e um motor de regras inteligente que detecta infestações, deficiência hídrica e anomalias climáticas antes que causem perdas significativas. A solução roda em cloud, é acessada via browser (sem instalação) e gera alertas classificados por severidade com recomendações de ação.

### Modelo de Receita (SaaS + Hardware)

- **Assinatura mensal por talhão** (modelo SaaS escalável)
- **Venda de kits de sensores** homologados para a plataforma
- **Add-ons** de análise avançada e integração com ERPs agrícolas

### Segmentos

Pequenos e médios produtores → cooperativas → agroindústrias → centros de pesquisa.

---

## Estrutura de Arquivos

```
agro_monitor_entrega/
├── README.md                          ← este arquivo
├── pipeline/
│   ├── pipeline_simulado.py           ← simulação sem Kafka (executa direto)
│   └── kafka-topics.yml               ← spec dos tópicos Kafka
├── docker/
│   ├── docker-compose.yml             ← orquestração completa
│   ├── producer/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── producer.py                ← simula sensores → Kafka
│   ├── rules-engine/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── consumer.py                ← regras booleanas → alertas
│   └── api/
│       ├── Dockerfile
│       └── requirements.txt
└── canvas/
    └── business_model_canvas.md
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
