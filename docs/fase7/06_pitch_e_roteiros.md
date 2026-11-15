# 6. Apresentação do produto (pitch) e roteiros dos vídeos (10%)

Slides: [`AgroSmart_Pitch.pptx`](AgroSmart_Pitch.pptx) (gerado por `docs/fase7/gerar_slides.py`).

> Os números de desempenho citados (F1, antecedência, tempo de resolução) foram medidos **na simulação** da
> plataforma (5 talhões, 7 dias). No pitch, apresente-os assim: "na nossa simulação…".

## 6.1 Conteúdo do pitch

### Problema resolvido
O produtor descobre os problemas **tarde demais**. Seca com a bomba quebrada, geada de madrugada, uma lagarta
que se espalha: quando alguém percebe andando pelo talhão, a perda já aconteceu. Os sensores que existem no
mercado geram dados, mas não dizem **o que fazer**, e o produtor recebe tantos avisos que para de olhar.

### Solução proposta
O **AgroSmart** é uma plataforma de monitoramento agrícola que **mede, decide e age**:

1. **Mede** — sensores de solo, clima, câmera e chuva em cada talhão (kit IoT próprio ou sensores existentes).
2. **Decide** — um motor de regras agronômicas e um modelo de Machine Learning que **prevê o problema 6 horas antes**.
3. **Age** — liga a irrigação, abre a ordem de manutenção e avisa o gestor automaticamente; a IA Generativa
   explica a situação em linguagem simples.
4. **Melhora sozinha** — a mineração de processos mostra onde as ocorrências travam (ex.: manutenção que demora
   45h) e o que automatizar a seguir.

### Diferencial competitivo

| | Planilha / visita a campo | Estação meteorológica / telemetria comum | **AgroSmart** |
|---|---|---|---|
| Detecta o problema | dias depois | quando já aconteceu | **até 6h antes** (ML) |
| Diz o que fazer | ❌ | ❌ | ✅ recomendação + relatório em linguagem natural |
| Age sozinho | ❌ | parcial | ✅ irrigação, manutenção, notificação |
| Mostra onde o processo trava | ❌ | ❌ | ✅ mineração de processos |
| Confiabilidade operacional | — | variável | ✅ autocontrole de saúde, pipeline com segurança verificada |

Em uma frase: **os concorrentes mostram dados; o AgroSmart entrega a decisão e executa a primeira ação.**

### Público-alvo
- **Primário:** pequenos e médios produtores de grãos, hortifrúti e café, com 5 a 200 talhões, que já têm ou
  podem ter irrigação automatizável.
- **Canal/escala:** cooperativas agrícolas (contratam para os associados e recebem a visão consolidada).
- **Secundário (produtos de dados):** seguradoras e crédito rural (score de risco por talhão), agroindústrias
  (rastreabilidade) e centros de pesquisa (dados anonimizados) — conforme o Canvas v2.

### Proposta de valor
> **"Do sensor à decisão em minutos, não em dias."**
> O AgroSmart antecipa a perda, executa a primeira resposta sozinho e mostra ao produtor exatamente o que
> fazer — com histórico confiável para negociar seguro e crédito.

Resultados na simulação:
- **F1 0,95** do modelo contra **0,89** da regra reativa; **+11,5 p.p.** de eventos críticos detectados (recall).
- **61%** das ocorrências críticas previstas com **4,7h** de antecedência média.
- Irrigação automática resolve o déficit hídrico em **~3h** (mediana).
- Plataforma com **autocontrole de saúde**, imagem com **0 vulnerabilidades HIGH/CRITICAL** e pipeline com 9 verificações.

### Modelo de receita (do Canvas v2)
- **SaaS por talhão/mês** — Básico (alertas + dashboard) e Avançado (ML preditivo + IA + histórico + mineração).
- **Kit de sensores** homologado (venda ou comodato).
- **Produtos de dados** — score de risco para seguradoras e crédito rural; relatórios regionais; API de insights.

### Próximos passos (roadmap)
Sensores físicos via MQTT/LoRaWAN · app mobile com notificação por WhatsApp · ações preventivas disparadas pelo ML ·
SLA de manutenção integrado · piloto com uma cooperativa.

## 6.2 Estrutura dos slides

| # | Slide | Mensagem |
|---|---|---|
| 1 | Capa | AgroSmart — do sensor à decisão |
| 2 | O problema | O produtor descobre tarde; dados sem decisão; excesso de avisos |
| 3 | A solução | Mede → Decide → Age → Melhora |
| 4 | Como funciona | Arquitetura em 5 camadas (diagrama) |
| 5 | Diferencial | Tabela comparativa |
| 6 | Resultados | Números da simulação |
| 7 | Mineração de processos | Gargalos encontrados e melhorias |
| 8 | Pronto para o mercado | Containers, monitoramento, DevSecOps |
| 9 | Público-alvo | Produtores, cooperativas, seguradoras |
| 10 | Proposta de valor e modelo de receita | SaaS + kit + dados |
| 11 | Roadmap e equipe | Próximos passos + integrantes |

## 6.3 Roteiro do vídeo pitch (até 5 min)

| Tempo | Slide | Fala sugerida |
|---|---|---|
| 0:00–0:30 | 1–2 | "Imagine acordar e descobrir que a geada da madrugada queimou parte da lavoura, ou que a bomba de irrigação quebrou há dois dias e ninguém viu. É assim que o produtor descobre a maioria dos problemas: tarde demais." |
| 0:30–1:10 | 2 | "Hoje existem sensores, mas eles entregam números, não decisões. E quando avisam, avisam tanto que o produtor deixa de olhar." |
| 1:10–2:00 | 3–4 | "O AgroSmart mede, decide e age. Sensores no talhão; um motor de regras agronômicas e um modelo de Machine Learning que prevê o problema 6 horas antes; e a plataforma já liga a irrigação, abre a ordem de manutenção e explica a situação em linguagem simples." |
| 2:00–2:40 | 5 | "A diferença: os concorrentes mostram dados; nós entregamos a decisão e executamos a primeira ação. E usamos mineração de processos para descobrir onde as ocorrências travam." |
| 2:40–3:20 | 6–7 | "Na nossa simulação, o modelo previu 61% dos eventos críticos com quase 5 horas de antecedência. A mineração mostrou que uma falha de irrigação levava 45 horas para ser resolvida porque dependia de alguém ir a campo, e isso virou a próxima melhoria." |
| 3:20–3:50 | 8 | "É um produto pronto para operar: roda em containers, se monitora sozinho e só é publicado depois de passar por testes e verificações de segurança." |
| 3:50–4:30 | 9–10 | "Nosso cliente é o pequeno e médio produtor, alcançado por cooperativas. Cobramos por talhão por mês, vendemos o kit de sensores e, com o histórico, oferecemos score de risco para seguradoras e crédito rural." |
| 4:30–5:00 | 11 | "AgroSmart: do sensor à decisão em minutos, não em dias. Próximo passo: um piloto com uma cooperativa. Obrigado!" |

## 6.4 Roteiro do vídeo final (5 a 8 min)

**Preparação:** `AGRO_INTERVALO_S=30 docker compose up -d` alguns minutos antes; dashboard aberto em
http://localhost:8501; terminal na raiz; `docs/fase7/arquitetura_final.png` aberto.

| Tempo | Tela | Conteúdo |
|---|---|---|
| 0:00–0:30 | Capa / README | Apresentação: o que é o AgroSmart e o que a Fase 7 entrega (execução automatizada, DevSecOps, monitoramento, mineração de processos) |
| 0:30–1:30 | `arquitetura_final.png` | Arquitetura final da esquerda para a direita: entrada → processamento → automação/inteligência → saída; faixa de operação embaixo |
| 1:30–2:30 | Terminal | `docker compose ps` (2 serviços healthy) · `docker compose logs -f pipeline` mostrando um ciclo: coleta → processamento → automação → IA → mineração. Destacar "1706 recebidas → 1695 válidas", "55 episódios", "F1 0,949" |
| 2:30–3:45 | Dashboard | KPIs e cards (TAL-02 crítico: inspecionar bomba; TAL-03 em atenção só pelo ML) → Evolução no tempo (seca do TAL-02) → Alertas e ações → Risco ML → relatório da IA. **Fluxo entrada → processamento → saída** com o caso do TAL-02 |
| 3:45–4:30 | Aba 🩺 Monitoramento + terminal | Saúde, disponibilidade, duração por etapa; `docker exec agrosmart_pipeline python monitoramento/healthcheck.py`. Opcional: mostrar o teste de falha (corromper o serial → unhealthy → restaurar → healthy) |
| 4:30–5:15 | GitHub Actions ou `./devsecops/pipeline_local.sh` | As 9 etapas; mostrar que a 1ª execução barrou 38 CVEs e containers rodando como root, e a 2ª passou |
| 5:15–7:00 | Aba 🔀 Processo | Event log (case = ocorrência), mapa DFG, variantes. Análise: **gargalos** (escalado→normalizado 10h; manutenção 45h; infestação sem fechamento), **variações** (déficit hídrico 3h vs 47h; 61% previstos pelo ML sem ação preventiva; reincidência), **melhorias** M1–M7 e processo to-be |
| 7:00–7:30 | README | Encerramento: solução completa ponta a ponta, próximos passos, equipe |

**Dicas:** grave em 1080p; ensaie cronometrando; suba no YouTube como "não listado" ou no Drive com acesso por link
e cole os links em `docs/link_video_fase7.txt`.
