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

---

## Roteiro do Pitch de Negócios (Duração Estimada: 2 a 4 minutos)

Este roteiro foi estruturado estrategicamente para apresentar a proposta de valor do AgroSmart para investidores e produtores rurais, dividindo a apresentação por minutos para garantir uma exposição fluida, profissional e direta ao ponto.

### Minuto 0:00 - 0:30 | O Gancho e a Dor do Mercado (Problema)
*   **Visual:** Apresentador em primeiro plano, com imagens de plantações saudáveis contrastando com talhões afetados por seca ou pragas ao fundo.
*   **Fala (Locução):**
    > "Você sabia que, anualmente, até 30% de toda a produção agrícola global é desperdiçada devido a pragas, falhas de irrigação e flutuações extremas de temperatura? Para o produtor rural, cada dia sem detectar um foco de pulgão ou um solo com déficit hídrico significa prejuízo direto no bolso e ameaça à segurança alimentar da sua safra. Detectar o problema tarde demais é o maior gargalo da agricultura moderna."

### Minuto 0:30 - 1:15 | A Apresentação da Solução (AgroSmart)
*   **Visual:** Apresentador aponta para a tela exibindo o dashboard interativo do AgroSmart rodando em tempo real. Gráficos subindo, leituras de sensores IoT sendo transmitidas instantaneamente.
*   **Fala (Locução):**
    > "Para resolver essa dor, nós criamos o **AgroSmart** — uma plataforma inteligente de agricultura de precisão e monitoramento em tempo real. Através de sensores IoT de alta frequência instalados nos talhões, transmitimos dados contínuos de temperatura, umidade do solo e saúde foliar usando a tecnologia robusta de streaming do Apache Kafka. Nosso motor de regras proprietário analisa esses dados instantaneamente, aplicando lógica booleana rigorosa. Quando qualquer parâmetro foge da normalidade, o AgroSmart gera alertas estruturados de severidade Crítica, Atenção ou Aviso, já com recomendações acionáveis na tela e notificações automáticas para a equipe de campo."

### Minuto 1:15 - 2:00 | Modelo de Negócios e Monetização (SaaS + Hardware)
*   **Visual:** Slide limpo mostrando os pilares de receita: Assinatura Mensal, Kits de Sensores e Serviços Corporativos (B2B).
*   **Fala (Locução):**
    > "Nosso modelo de negócios é extremamente escalável e previsível, focado em **SaaS (Software as a Service)**. Cobramos uma assinatura mensal recorrente que varia de R$ 80 a R$ 300 por talhão monitorado. Complementamos nossa receita com a venda única dos nossos kits de sensores homologados e com taxas de integração de APIs para grandes cooperativas que desejam consolidar os dados em seus ERPs agrícolas existentes. Isso nos garante uma receita recorrente previsível com margem bruta de software superior a 80%."

### Minuto 2:00 - 2:45 | Estratégia de Go-to-Market (Canais e Clientes)
*   **Visual:** Mapa mental de distribuição exibindo Cooperativas, Revendas de Insumos e Consultorias Agronômicas.
*   **Fala (Locução):**
    > "Como chegamos ao cliente? Focamos em canais de alto efeito multiplicador: **Cooperativas Agrícolas** e **Consultorias Agronômicas**. Ao fazer parcerias com agrônomos consultores e grandes cooperativas, conseguimos introduzir o AgroSmart de forma confiável para centenas de produtores associados em um único acordo comercial. Também marcamos presença ativa nas maiores feiras agrícolas do país, como a Agrishow, convertendo demonstrações práticas em assinaturas ativas."

### Minuto 2:45 - 3:30 | Estrutura de Custos e Viabilidade Financeira
*   **Visual:** Gráfico de pizza simples mostrando as despesas (Cloud, P&D, Equipe) e o Ponto de Equilíbrio.
*   **Fala (Locução):**
    > "Nossa estrutura de custos é otimizada. Os maiores investimentos estão alocados em infraestrutura de nuvem resiliente para manter o streaming de dados e na manutenção e refinamento do nosso software e algoritmos. Nosso ponto de equilíbrio operacional é atingido rapidamente: com apenas 500 talhões monitorados sob uma assinatura média de R$ 150/mês, cobrimos integralmente nossos custos de operação e suporte, tornando cada novo talhão escalado em nossa plataforma puro lucro líquido."

### Minuto 3:30 - 4:00 | Encerramento e Call to Action (Chamada para Ação)
*   **Visual:** Logo do AgroSmart, contatos e os nomes dos integrantes do grupo e RMs (FIAP 4ESOA).
*   **Fala (Locução):**
    > "O AgroSmart traz a agilidade digital e a segurança do monitoramento em tempo real para o coração da lavoura. Evite perdas, aumente sua produtividade e garanta a sustentabilidade do seu negócio. Venha com o AgroSmart colher o futuro hoje! Muito obrigado."
