# Data Lake Demo — AgroSmart (Fase 5)

Implementação executável da arquitetura descrita em [`data-lake/architecture.md`](../data-lake/architecture.md):
um Data Lake local em camadas (Raw → Trusted → Refined) que termina em relatórios de IA
Generativa, tudo em Python puro, sem dependências externas.

## Pré-requisitos

- Python 3.9+ (usa apenas a biblioteca padrão)
- A pasta `ingestion/samples/` precisa existir um nível acima de `datalake-demo/`
  (estrutura já presente neste repositório)
- Opcional: `pip install anthropic` + variável de ambiente `ANTHROPIC_API_KEY`, apenas se
  quiser rodar a etapa de IA com um modelo real em vez do modo simulado

## Estrutura esperada

```
agro-monitor/
├── ingestion/
│   └── samples/                ← os scripts de ingestão leem daqui
└── datalake-demo/
    ├── run_pipeline.py
    └── scripts/
        ├── 01_ingestao.py
        ├── 02_camada_trusted.py
        ├── 03_camada_refined.py
        └── 04_ia_generativa.py
```

## Como rodar

Pipeline completo, do zero:

```bash
cd datalake-demo
python3 run_pipeline.py
```

Isso executa, em sequência, as 4 etapas abaixo e recria a pasta `datalake/` a cada execução.

Para usar a API real da Anthropic na etapa de IA Generativa (em vez do modo simulado):

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sua-chave-aqui"
python3 run_pipeline.py --real
```

Se `--real` for passado sem a variável `ANTHROPIC_API_KEY` definida (ou sem o pacote `anthropic`
instalado), o script avisa no console e cai automaticamente para o modo simulado — não quebra a
execução.

## Etapas do pipeline

| Script | O que faz | Entrada | Saída |
|---|---|---|---|
| `01_ingestao.py` | Copia os exemplos de `ingestion/samples/` para a camada Raw, particionados por fonte/data, e gera 5 dias de histórico sintético para os talhões `TAL-07` (umidade em queda) e `TAL-12` (estável). Injeta de propósito uma leitura inválida (umidade 137,4%) em `2026-09-02` para testar a rejeição na etapa seguinte. | `ingestion/samples/*` | `datalake/raw/` |
| `02_camada_trusted.py` | Valida schema e faixas plausíveis (umidade 0–100%, temperatura -10–55°C, pH 0–14), deduplica por `talhao_id+data+hora` e normaliza para JSON Lines. Registros inválidos não são descartados: vão para `raw/rejeitados/` com o motivo. | `datalake/raw/` | `datalake/trusted/`, `datalake/raw/rejeitados/` |
| `03_camada_refined.py` | Agrega por talhão: médias, tendência (queda/estável/alta), detecções de praga relevantes (confiança ≥ 70%) e alertas de déficit hídrico (umidade atual < 40%). É o "contrato de dados" que a IA Generativa consome. | `datalake/trusted/` | `datalake/refined/resumo_talhoes.json` |
| `04_ia_generativa.py` | Monta um prompt estruturado por talhão e gera um relatório de apoio à decisão (situação atual, riscos, recomendação priorizada). Por padrão usa um motor de regras local que imita a saída de um LLM; com `--real` e `ANTHROPIC_API_KEY` definida, chama a API da Anthropic (`claude-sonnet-4-5`) com o mesmo prompt. | `datalake/refined/resumo_talhoes.json` | `datalake/refined/relatorios_ia/<TALHAO>_<data>.md` |

Cada etapa também pode ser rodada isoladamente (na ordem acima, já que cada uma lê a saída da
anterior):

```bash
python3 scripts/01_ingestao.py
python3 scripts/02_camada_trusted.py
python3 scripts/03_camada_refined.py
python3 scripts/04_ia_generativa.py            # modo simulado
python3 scripts/04_ia_generativa.py --talhao TAL-07   # só um talhão
python3 scripts/04_ia_generativa.py --real     # força uso da API real
```

## Onde olhar o resultado

- `datalake/raw/` — dados como chegaram (sensores, imagens, CSV), mais `raw/rejeitados/` com o
  que foi barrado na validação
- `datalake/trusted/` — `leituras_solo.jsonl` e `deteccoes_imagem.jsonl`, já limpos e no grão
  original
- `datalake/refined/resumo_talhoes.json` — agregados por talhão (médias, tendência, alertas)
- `datalake/refined/relatorios_ia/` — relatórios de apoio à decisão gerados por talhão

A pasta `datalake/` é recriada a cada `python3 run_pipeline.py` (o passo 1 apaga e recria antes de
popular de novo), então é seguro rodar quantas vezes quiser.

Para a fundamentação teórica de cada camada e do módulo de IA, ver
[`data-lake/architecture.md`](../data-lake/architecture.md) e
[`ia-generativa/decision_support.md`](../ia-generativa/decision_support.md).
