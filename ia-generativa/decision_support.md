# IA Generativa para Apoio à Decisão — AgroSmart

## Funcionamento e Contexto Utilizado

O módulo de IA Generativa consome dados exclusivamente da **camada Refinada** do Data Lake —
nunca a camada bruta — para garantir que os relatórios se baseiem em informações já validadas e
agregadas. O fluxo é:

1. Um job agendado (ex.: diário, às 07h) consulta a camada Refinada e monta um **contexto
   estruturado** por talhão: médias e tendências de umidade/temperatura/pH nas últimas 24h e 7
   dias, alertas do motor de regras (Fase 4) disparados no período, detecções de pragas por visão
   computacional e a previsão do tempo para os próximos 3 dias.
2. Esse contexto é inserido em um **prompt estruturado** enviado a um modelo de linguagem (LLM),
   pedindo explicitamente que a resposta seja baseada apenas nos dados fornecidos, em linguagem
   acessível ao produtor rural, com recomendação de ação priorizada por urgência.
3. A resposta do modelo é armazenada como um registro de relatório (com timestamp e referência aos
   dados de origem, para rastreabilidade) e exibida no dashboard como um cartão de recomendação.
4. Nenhuma ação é executada automaticamente pelo modelo — a IA gera **apoio** à decisão; a ação
   (irrigar, aplicar defensivo, etc.) continua sendo tomada pelo produtor ou agrônomo responsável.

### Exemplo de prompt (simplificado)

```
Você é um assistente agronômico. Com base apenas nos dados abaixo do Talhão TAL-07,
gere um relatório curto com: (1) situação atual, (2) riscos identificados,
(3) recomendação priorizada. Não invente dados que não estejam no contexto.

Dados (últimas 24h): umidade solo média 35.2% (tendência de queda),
temperatura média 24.9°C, pH 6.3, precipitação prevista para os próximos 3 dias: 0mm,
2 alertas de "déficit hídrico" nas últimas 6h, 1 detecção de lagarta desfolhadora
(confiança 87%) na imagem capturada às 07:45.
```

## Exemplo de Saída da IA (simulada)

> **Relatório de Apoio à Decisão — Talhão TAL-07 — 05/09/2026, 08h00**
>
> **Situação atual:** A umidade do solo está em 35,2% e em queda nas últimas 24 horas, com
> nenhuma chuva prevista para os próximos 3 dias. A temperatura e o pH seguem dentro da faixa
> normal para a cultura.
>
> **Riscos identificados:**
> 1. **Déficit hídrico (alta prioridade)** — a combinação de umidade em queda e ausência de chuva
>    prevista pode levar a estresse hídrico na cultura nas próximas 48–72h.
> 2. **Praga em observação (média prioridade)** — foi detectada a presença de lagarta desfolhadora
>    com 87% de confiança em uma área do talhão; recomenda-se inspeção visual para confirmar a
>    extensão da infestação antes de decidir por controle químico ou biológico.
>
> **Recomendação priorizada:**
> 1. Programar irrigação suplementar no Talhão TAL-07 nas próximas 24h, visando restabelecer a
>    umidade para a faixa de 45–55%.
> 2. Enviar equipe de campo para inspeção pontual da área onde a praga foi detectada antes de
>    aplicar qualquer defensivo.
> 3. Reavaliar a situação em 48h com base nas novas leituras dos sensores.
>
> *Relatório gerado automaticamente a partir de dados da camada Refinada do Data Lake AgroSmart.
> Decisão final cabe ao responsável técnico do talhão.*

## Observação sobre a Simulação

Para fins da entrega acadêmica, a chamada ao modelo pode ser simulada localmente (função Python
que monta o prompt acima e retorna um texto no mesmo formato) ou feita de fato a uma API de LLM
(ex.: Claude, GPT), passando o mesmo contexto estruturado extraído da camada Refinada. A estrutura
do prompt e do relatório de saída é a mesma nos dois casos — o que muda é apenas quem gera o texto
final.
