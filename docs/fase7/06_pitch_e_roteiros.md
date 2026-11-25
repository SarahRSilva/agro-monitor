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

Slides: [`AgroSmart_Video_Final.pptx`](AgroSmart_Video_Final.pptx) — 12 slides, com a fala de cada trecho nas notas do apresentador.

O vídeo **não é só a apresentação dos slides**: os slides 4 a 8 servem de apoio, e em cada um deles a tela muda para a
plataforma rodando de verdade (terminal, dashboard, GitHub Actions). É essa demonstração que a rubrica avalia
("análise de processo + demonstração", 25%). Duração-alvo: **~7 min**.

### 6.4.1 Preparação (10 min antes de gravar)

**Plataforma no 1º ciclo.** No modo contínuo cada ciclo usa uma semente diferente (`42`, `43`, `44`…); os números dos
slides (1.706 leituras, F1 0,949, 55 casos, TAL-02 crítico) só aparecem no **1º ciclo**. Por isso, logo antes de gravar:

```bash
docker compose down -v                       # zera dados e histórico de monitoramento
AGRO_INTERVALO_S=900 docker compose up -d    # 1 ciclo a cada 15 min: o ciclo 1 fica na tela durante a gravação
docker compose ps                            # aguarde os 2 serviços aparecerem como (healthy)
```

> A partir daí você tem **~15 min** até o 2º ciclo trocar os números. Se passar disso, repita os três comandos.

**Janelas abertas, nesta ordem** (alternar com Cmd+Tab):

1. **Slides** em tela cheia (Google Slides: *Apresentar*; PowerPoint/Keynote: modo apresentador para ler as notas).
2. **Terminal** na raiz do projeto, fonte grande (Cmd + `+` umas 3 vezes), tela limpa (`clear`).
3. **Navegador** com o dashboard em http://localhost:8501, já carregado, zoom 110–125%.
4. **Navegador** (outra aba) com o GitHub Actions do repositório → workflow **DevSecOps** → última execução verde.

**OBS / gravação:**

- [ ] *Configurações → Áudio*: microfone selecionado em "Mic/Áudio auxiliar"; a barra do Mixer chega perto de
      **−10 a −6 dB** quando você fala (se ficar em −24 dB, aumente o ganho ou aproxime o microfone).
- [ ] Gravar 10 s de teste e **ouvir** antes de começar.
- [ ] 1080p, 30 ou 60 fps.
- [ ] Fechar abas pessoais, notificações (Não Perturbe ligado) e esconder o Dock.
- [ ] Ocultar o cursor nos slides (mover para o canto); no dashboard, use o cursor para apontar o que está falando.
- [ ] **Não** clicar em "Rodar pipeline completo" na barra lateral do dashboard: isso gera outro cenário e muda os números.

### 6.4.2 Roteiro passo a passo

Cada bloco tem: **Tela** (o que aparece) · **Ação** (o que fazer) · **Fala** (sugestão, pode adaptar) · **Destacar**.

---

#### 0:00–0:20 · Abertura — Slide 1 (capa)

- **Tela:** slide 1 já em tela cheia (comece a gravar com ele aberto, sem aparecer o navegador).
- **Fala:** "Olá, somos o grupo do AgroSmart, uma plataforma de monitoramento agrícola que mede, decide e age. Na
  Fase 7, ela deixa de ser uma plataforma que funciona na nossa máquina e vira um produto: roda sozinha em
  containers, se monitora, passa por um pipeline DevSecOps antes de ser publicada e analisa o próprio processo com
  mineração de processos."

#### 0:20–0:35 · Agenda — Slide 2

- **Tela:** slide 2.
- **Fala:** "Vamos mostrar primeiro a arquitetura, depois a plataforma rodando de verdade, no terminal e no
  dashboard, a parte de operação, com monitoramento e DevSecOps, e por fim a análise do processo com mineração."

#### 0:35–1:30 · Arquitetura final — Slide 3

- **Tela:** slide 3 (diagrama). Use o cursor para acompanhar as caixas da esquerda para a direita.
- **Fala** (uma frase por camada):
  1. "Na **entrada** temos o Arduino simulado no TinkerCad e o simulador de campo, com 5 talhões por 7 dias, além da
     câmera e do pluviômetro."
  2. "No **processamento**, os dados brutos entram na camada raw; o `processar_dados.py` padroniza, remove
     duplicadas, valida e cria features. O que é inválido vai para `raw/rejeitados` com o motivo; o resto vai para
     a camada trusted."
  3. "Na **automação e inteligência**, o motor de regras, que vem da Fase 4, trabalha junto com um Random Forest que
     prevê o risco nas próximas 6 horas. A decisão combinada dispara ações automáticas e o relatório da IA
     Generativa, da Fase 5."
  4. "Na **saída** ficam a camada refined, o dashboard, os alertas e os relatórios para o produtor."
  5. "E embaixo, a **faixa de operação**: o orquestrador roda um ciclo a cada N segundos, o monitoramento registra
     tudo, o Docker Compose executa e o GitHub Actions só publica a imagem depois das verificações de segurança."

#### 1:30–2:30 · Plataforma em containers — Slide 4 → **Terminal**

- **Tela:** slide 4 por ~5 s, depois **Cmd+Tab para o terminal**.
- **Ação 1:** `docker compose ps`
  - **Destacar:** "São dois serviços, o pipeline e o dashboard, usando a mesma imagem, e os dois estão
    **healthy**."
- **Ação 2:** mostrar só as linhas que importam do ciclo 1:

  ```bash
  docker compose logs --no-log-prefix pipeline | grep -E "Ciclo 1 |Etapa .* ok|recebidas|duplicadas|rejeitadas|válidas|episódios|F1=|event log" | head -15
  ```

  (ou `docker compose logs -f pipeline` e rolar até o início do ciclo 1; Ctrl+C para sair).
  - **Destacar,** apontando cada linha: "Aqui vemos um ciclo completo, sem ninguém mexer: coleta, processamento,
    automação, IA e mineração, cada etapa cronometrada. Recebemos **1.706 leituras** e **1.695 ficaram válidas**:
    6 duplicadas removidas e 5 rejeitadas com o motivo. A automação encontrou **55 episódios** de alerta, e o
    modelo de ML teve **F1 de 0,949**, contra 0,887 da regra reativa."
- **Fala de transição:** "Agora vamos ver o resultado disso no dashboard."

#### 2:30–3:45 · Dashboard: entrada → processamento → saída no TAL-02 — Slide 5 → **Dashboard**

- **Tela:** slide 5 por ~5 s ("o caso do TAL-02"), depois **Cmd+Tab para o navegador** (http://localhost:8501).
- **Ação 1 — topo da página:** apontar os 5 KPIs (temperatura, umidade, luminosidade, alertas críticos, talhões em
  risco alto).
- **Ação 2 — "Situação atual por talhão":** apontar o card do **TAL-02** em crítico.
  - **Fala:** "O TAL-02 está crítico: falha de irrigação com déficit hídrico, e a recomendação é inspecionar a
    bomba. Já o TAL-03 está em atenção só pelo risco previsto pelo modelo, antes de qualquer regra disparar."
  - Abrir o expander **📝 Relatório da IA Generativa** do TAL-02 e ler 1 linha: "A IA explica a situação em linguagem
    simples para o produtor."
- **Ação 3 — aba 📈 Evolução no tempo:** apontar a linha do TAL-02 no gráfico de umidade do solo caindo abaixo de
  30% e 20%.
  - **Fala:** "Essa é a **entrada**: o sensor mostra o solo do TAL-02 secando, com a irrigação desligada e
    praticamente sem chuva."
- **Ação 4 — aba 🚨 Alertas e ações:** apontar a linha FALHA_IRRIGACAO / CRITICO do TAL-02; abrir **Log de ações
  automáticas executadas**.
  - **Fala:** "O **processamento** calculou a tendência da umidade em 6 horas e a chuva acumulada em 24 horas, e a
    **saída** foi automática: ordem de manutenção aberta, gestor avisado e o card de inspecionar a bomba."
- **Ação 5 — aba 🤖 Risco previsto (ML):** apontar F1 e o "vs regra".
  - **Fala:** "O modelo prevê o evento crítico com 6 horas de antecedência e supera a regra reativa em todas as
    métricas."

#### 3:45–4:30 · Monitoramento — Slide 6 → **Dashboard + Terminal**

- **Tela:** slide 6 por ~5 s, depois **aba 🩺 Monitoramento** no dashboard.
- **Ação 1:** apontar *Saúde da plataforma* (🟢 Saudável), *Último ciclo* (OK), *Ciclos ok / erro*, *Disponibilidade* e o
  gráfico de duração por etapa.
  - **Fala:** "A plataforma sabe quando não está saudável. Cada ciclo é registrado com a duração de cada etapa, e
    temos disponibilidade, indicadores de qualidade e o log estruturado."
- **Ação 2 — terminal:** `docker exec agrosmart_pipeline python monitoramento/healthcheck.py`
  - **Destacar:** `"saudavel": true` e as 4 verificações (`status_existe`, `ultimo_ciclo_ok`, `dados_recentes`,
    `saidas_refined`).
- **Fala sobre o teste de falha (volte ao slide 6):** "Também testamos uma falha controlada: corrompemos o arquivo
  serial do TinkerCad, o ciclo falhou, o container ficou unhealthy e o erro apareceu nessa aba. Restauramos o arquivo
  e o ciclo seguinte voltou a healthy. Naquele teste, a disponibilidade registrada foi de **85,7%**, 6 de 7 ciclos,
  e o incidente fica no histórico."
  > Não fazer o teste de falha ao vivo: ele altera os números do dashboard. Os 85,7% vêm das evidências em
  > `docs/fase7/evidencias/monitoramento/` — o dashboard ao vivo mostra 100% (1 de 1 ciclo).

#### 4:30–5:15 · Pipeline DevSecOps — Slide 7 → **GitHub Actions**

- **Tela:** slide 7 por ~10 s (apontar a tabela "1ª execução reprovada → 2ª aprovada"), depois a aba do
  **GitHub Actions → DevSecOps → última execução verde**.
- **Ação:** abrir a execução e passar o cursor pelos jobs/etapas.
- **Fala:** "São 9 verificações em três blocos: **qualidade**, com ruff e 19 testes no pytest; **segurança**, com
  bandit, pip-audit e gitleaks; e **build**, com Trivy na configuração, build da imagem, Trivy na imagem e smoke
  test. A primeira execução foi **reprovada de verdade**: o Trivy achou 38 vulnerabilidades HIGH e CRITICAL na
  imagem base e containers da Fase 4 rodando como root. Corrigimos com atualização dos pacotes no build e usuário
  sem privilégio, e a segunda passou. A imagem só é publicada no GHCR depois de tudo aprovado."
- **Alternativa** (sem internet): no terminal, `./devsecops/pipeline_local.sh` e mostrar o final
  "pipeline aprovado (todas as etapas OK)".

#### 5:15–6:00 · Mineração de processos — Slide 8 → **Aba 🔀 Processo**

- **Tela:** slide 8 por ~5 s, depois **aba 🔀 Processo (mineração)** no dashboard.
- **Ação 1:** apontar os indicadores do topo (Casos, Variantes, Em aberto, Críticos antecipados pelo ML, Gargalo).
  - **Fala:** "Cada ocorrência no campo vira um caso no event log: o caso é o talhão, a regra e o início, e as
    atividades vêm das saídas reais da plataforma — risco previsto, alerta, ação automática, gestor notificado,
    ordem de manutenção, escalado e normalizada. São **55 casos, 246 eventos e 16 variantes**. O mesmo log sai em XES
    para ProM, Disco ou pm4py."
- **Ação 2:** rolar até o **Mapa do processo (DFG)**.
  - **Fala:** "No mapa, a espessura é o número de casos e o vermelho marca esperas de 12 horas ou mais."
- **Ação 3:** rolar até **Variantes do processo**.
  - **Fala:** "As três variantes principais cobrem 70,9% dos casos; os problemas estão nas outras 13."

#### 6:00–6:20 · Gargalos — Slide 9

- **Tela:** slide 9 (voltar aos slides).
- **Fala:** "Achamos três gargalos. Primeiro, a **manutenção sem retorno**: a ordem é aberta, mas não tem SLA nem
  evento de manutenção concluída, e leva **45 horas**. Segundo, o **crítico esperando o clima**: na temperatura
  extrema a ação só aumenta a leitura e avisa, e o caso espera **10 horas**. Terceiro, a **infestação nunca fecha**,
  porque não existe a atividade 'tratamento aplicado'. No processo técnico, a mineração ocupa a maior parte do
  ciclo e o modelo é re-treinado toda vez, mesmo sem dados novos."

#### 6:20–6:40 · Variações — Slide 10

- **Tela:** slide 10.
- **Fala:** "E três variações. O **déficit hídrico** resolve em 3 horas com a bomba funcionando, mas arrasta 47 horas
  com a bomba quebrada, porque o processo não verifica se a ação funcionou. O modelo **antecipa 61%** das
  ocorrências críticas com 4,7 horas de antecedência, mas a previsão não dispara nenhuma ação. E há **reincidência**:
  temperatura extrema e movimento noturno se repetem quase toda noite."

#### 6:40–7:05 · Melhorias e processo ideal — Slide 11

- **Tela:** slide 11 — **não pule este slide**, ele fecha a análise.
- **Fala:** "Cada achado virou uma melhoria: ação preventiva disparada pelo ML; verificar o efeito da ação em 1 hora;
  SLA de manutenção, de 45 para menos de 8 horas; a atividade 'tratamento aplicado' com foto da câmera; agrupar
  alertas repetidos; proteção programada para padrões recorrentes, como a geada no TAL-05; e um pipeline mais
  rápido, que já aplicamos em parte no Dockerfile." Apontar o quadro **Processo ideal (to-be)**: "Esse é o processo
  ideal: o risco alto já gera a ação preventiva e o alerta nem chega a acontecer."

#### 7:05–7:30 · Encerramento — Slide 12

- **Tela:** slide 12.
- **Fala:** "O AgroSmart é uma solução completa, ponta a ponta: coleta, processa, decide e age sozinho; roda em
  containers, se monitora e só é publicado depois de passar pelas verificações de segurança; e usa a mineração de
  processos para descobrir a próxima melhoria. Os próximos passos são sensores físicos via MQTT ou LoRaWAN, a ação
  preventiva disparada pelo ML e um piloto com uma cooperativa. Obrigado!"
- **Ação:** ficar ~2 s no slide e **parar a gravação ainda em tela cheia** (não sair da apresentação antes de parar).

### 6.4.3 Depois de gravar

- [ ] Assistir inteiro: o áudio está audível do início ao fim? A duração ficou entre 5 e 8 min?
- [ ] Aparar o início e o fim (QuickTime: *Editar → Aparar*) para não aparecer o navegador, o aviso "press Esc" ou o
      editor de slides.
- [ ] Subir no YouTube como "não listado" ou no Drive com acesso "qualquer pessoa com o link".
- [ ] Colar o link em `docs/link_video_fase7.txt`.
