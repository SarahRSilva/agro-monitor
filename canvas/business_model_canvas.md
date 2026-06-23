# Business Model Canvas — AgroSmart

## Proposta de Valor (centro)

O AgroSmart é uma plataforma de **monitoramento agrícola em tempo real** que combina sensores IoT, streaming de dados com Apache Kafka e um motor de regras booleanas para detectar automaticamente infestações de pragas, déficit hídrico e anomalias climáticas em talhões rurais — antes que causem perdas irreversíveis.

**Diferenciais:**
- Alertas inteligentes classificados por severidade (CRÍTICO / ATENÇÃO / AVISO) em segundos
- Dashboard web sem instalação, acessível de qualquer dispositivo
- Relatórios automáticos por talhão em HTML/PDF para rastreabilidade
- Escalável do pequeno produtor ao grande grupo agroindustrial
- Arquitetura containerizada (Docker) para deploy em qualquer cloud

---

## Segmentos de Clientes

| Segmento | Perfil | Necessidade |
|---|---|---|
| Pequenos/médios produtores | 1–50 talhões, culturas anuais | Alerta precoce sem equipe técnica dedicada |
| Cooperativas agrícolas | Centenas de produtores associados | Padronização do monitoramento e relatórios |
| Consultoras agronômicas | Prestadores de serviço rural | Ferramenta de diferenciação para clientes |
| Agroindústrias | Produção própria em múltiplas fazendas | Gestão centralizada de toda a operação |
| Centros de pesquisa | Embrapa, universidades | Dados históricos e validação de modelos |

---

## Canais

- **Site e aplicativo web** (acesso ao dashboard via browser)
- **Parceiros distribuidores** no agronegócio (revendas de insumos e equipamentos)
- **Feiras agrícolas** (Agrishow, AgroBrasília, Show Rural)
- **Indicação de cooperativas** — crescimento orgânico B2B

---

## Relacionamento com Clientes

- Onboarding assistido por agrônomo parceiro (implantação dos sensores)
- Suporte técnico via chat, e-mail e videochamada
- Portal self-service para configuração de talhões e regras
- Webinars mensais sobre boas práticas e novidades da plataforma
- Comunidade de produtores para troca de experiências

---

## Fontes de Receita

| Fonte | Modelo | Estimativa |
|---|---|---|
| Assinatura mensal por talhão | SaaS recorrente | R$ 80–300/talhão/mês |
| Venda de kit de sensores | Hardware one-time | R$ 800–2.500/kit (4 sensores) |
| Análises avançadas (add-on) | Feature premium | R$ 200–500/fazenda/mês |
| API para ERPs agrícolas | Integração B2B | R$ 1.000–5.000/mês |
| Licenciamento para pesquisa | Contrato anual | R$ 10.000–50.000/ano |

---

## Recursos-chave

- **Tecnológicos:** Plataforma Python/Flask, Apache Kafka, containers Docker, banco de dados para histórico
- **Humanos:** Engenheiros de dados, desenvolvedores backend, agrônomos parceiros
- **Físicos:** Infraestrutura cloud (AWS/Azure), kits de sensores homologados
- **Intelectuais:** Algoritmos de detecção de pragas, base histórica de alertas

---

## Atividades-chave

- Coleta e streaming de dados dos sensores em tempo real
- Execução do motor de regras booleanas (INFESTAÇÃO AND/OR IRRIGAÇÃO/TEMPERATURA)
- Desenvolvimento contínuo da plataforma SaaS
- Validação e calibração dos algoritmos com dados de campo
- Integração com APIs externas (previsão climática, preços de commodities)

---

## Parcerias-chave

- **Fabricantes de sensores IoT agrícolas** (hardware)
- **Provedores de cloud** AWS / Azure / GCP (infraestrutura)
- **Embrapa e universidades** (validação científica dos modelos)
- **Cooperativas rurais** (canal de distribuição + base de usuários)
- **Distribuidores de defensivos agrícolas** (indicação cruzada pós-alerta)
- **INMET / CPTEC** (dados meteorológicos complementares)

---

## Estrutura de Custos

| Custo | Natureza |
|---|---|
| Infraestrutura cloud (Kafka, containers, banco) | Variável com escala |
| Desenvolvimento e manutenção de software | Fixo (equipe) |
| Suporte técnico e agrônomos parceiros | Semi-variável |
| Marketing e aquisição de clientes | Variável |
| P&D de novos sensores e algoritmos | Fixo |
| Logística dos kits de sensores | Variável |

**Ponto de equilíbrio estimado:** ~500 talhões monitorados com assinatura média de R$ 150/mês cobrindo os custos fixos de operação.

---

## Métricas de Sucesso (KPIs)

- Redução média de perdas agrícolas por hectare monitorado (meta: -25%)
- Tempo médio do alerta ao produtor (meta: <5 minutos da leitura)
- Precisão dos alertas (meta: >90% corretos / total gerado)
- Churn rate mensal (meta: <3%)
- NPS do produtor rural (meta: >60)
- Talhões ativos na plataforma (crescimento MoM)
