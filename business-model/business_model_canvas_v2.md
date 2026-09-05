# Business Model Canvas — AgroSmart v2 (Fase 5)

> Evolução do canvas da Fase 4, incorporando o Data Lake e a IA Generativa como ativos centrais
> do negócio, não apenas como componentes técnicos.

## Proposta de Valor

O AgroSmart deixa de ser apenas um "sistema de alertas em tempo real" e passa a ser uma
**plataforma de inteligência de dados agrícolas**: além de monitorar sensores, ela consolida o
histórico de cada talhão em um Data Lake confiável e usa IA Generativa para transformar dados
brutos em recomendações compreensíveis, com rastreabilidade sobre de onde cada recomendação veio.
Isso reduz o tempo entre "o dado foi coletado" e "a decisão foi tomada", e permite comparar
desempenho entre safras e talhões ao longo do tempo — algo que o pipeline em tempo real sozinho
não entregava.

## Segmentos de Clientes
- Pequenos e médios produtores rurais (usuários diretos da plataforma)
- Cooperativas agrícolas (visão consolidada de múltiplos produtores associados)
- Agroindústrias (rastreabilidade de insumos e condições de cultivo)
- Centros de pesquisa e universidades (acesso a dados históricos anonimizados)
- Seguradoras e financiadoras do agronegócio (dados de risco para crédito/seguro rural)

## Canais
- Dashboard web e app mobile
- API para integração com ERPs agrícolas e cooperativas
- Relatórios em PDF/e-mail gerados pela IA Generativa

## Relacionamento com Clientes
- Onboarding assistido na instalação dos sensores
- Suporte via chat com a própria IA Generativa (respondendo dúvidas sobre os relatórios)
- Comunidade de produtores para troca de boas práticas, alimentada pelos próprios dados agregados

## Fontes de Receita
- **Assinatura SaaS por talhão** (mantida da Fase 4), agora com planos diferenciados por
  profundidade analítica (básico: alertas em tempo real; avançado: relatórios de IA + histórico)
- **Venda de kits de sensores** homologados
- **Monetização baseada em dados** (novo):
  - Relatórios agregados e anonimizados de tendências regionais, vendidos a cooperativas,
    seguradoras e centros de pesquisa
  - Módulo de "score de risco de talhão" (baseado no histórico do Data Lake) oferecido a
    seguradoras e instituições de crédito rural como insumo para análise de risco
  - API paga de insights de IA Generativa para ERPs agrícolas de terceiros

## Parcerias Estratégicas
- Fabricantes de sensores IoT (integração e homologação de hardware)
- Provedores de cloud/armazenamento (para custo do Data Lake em escala)
- Institutos de pesquisa agronômica (validação científica dos modelos de risco/pragas)
- Cooperativas agrícolas (canal de distribuição e fonte de dados em maior volume)
- Seguradoras/instituições financeiras do agronegócio (consumidoras do score de risco)

## Recursos-Chave
- Data Lake em camadas (Raw/Trusted/Refined) como ativo de dados de longo prazo
- Motor de regras + modelos de ML para detecção de risco e pragas
- Módulo de IA Generativa para geração de relatórios e recomendações
- Equipe multidisciplinar (dados, agronomia, engenharia)

## Atividades-Chave
- Ingestão, validação e manutenção contínua da qualidade dos dados
- Treinamento e curadoria dos prompts/modelos usados pela IA Generativa
- Governança de dados (privacidade dos produtores, anonimização para produtos de dados agregados)

## Estrutura de Custos
- Armazenamento e processamento em nuvem (escala com volume de dados do Data Lake)
- Custos de inferência dos modelos de IA Generativa
- Hardware de sensores e logística de instalação
- Equipe de dados/engenharia e suporte ao cliente

---

## Roteiro do Vídeo (2–3 minutos)

1. **0:00–0:20 — Abertura:** recapitular rapidamente o AgroSmart (monitoramento em tempo real via
   sensores IoT, Fase 4) e anunciar a evolução: "agora os dados também geram inteligência de
   negócio, não só alertas."
2. **0:20–1:00 — Data Lake:** mostrar o diagrama de camadas (Raw/Trusted/Refined) e explicar em
   1–2 frases por camada por que isso importa para o produtor (histórico confiável, comparação
   entre safras).
3. **1:00–1:40 — IA Generativa:** mostrar o exemplo de relatório gerado (`decision_support.md`) e
   explicar que a IA lê os dados já validados do Data Lake e devolve uma recomendação em linguagem
   simples, sem tomar a decisão no lugar do produtor.
4. **1:40–2:30 — Novo modelo de negócio:** apresentar as novas fontes de receita baseadas em dados
   (relatórios agregados, score de risco para seguradoras, API para ERPs) e as novas parcerias
   estratégicas que isso viabiliza.
5. **2:30–3:00 — Fechamento:** reforçar a proposta de valor atualizada — "de sistema de alertas a
   plataforma de inteligência agrícola" — e créditos da equipe.
