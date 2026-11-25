# Narração do vídeo final: texto para gravar

Só a fala de cada bloco, sem instruções de tela, para ler direto (o roteiro completo está em `06_pitch_e_roteiros.md` §6.4.2).

**Como gravar**

- Um arquivo por bloco, com o número na frente do nome: `01_abertura.m4a`, `02_agenda.m4a`… Errou? Regrave só aquele bloco.
- Deixe **1 segundo de silêncio** no começo e no fim de cada arquivo.
- Mesmo lugar, mesma distância do microfone em todos os blocos, sem ventilador ou ar-condicionado ligado.
- Ritmo calmo. O tempo indicado em cada bloco é uma referência, não uma meta: eu ajusto a tela à sua voz.

---

## 01 · Abertura (~20 s)

Olá, somos o grupo do AgroSmart, uma plataforma de monitoramento agrícola que mede, decide e age. Na Fase 7, ela deixa de ser uma plataforma que funciona na nossa máquina e vira um produto: roda sozinha em containers, se monitora, passa por um pipeline DevSecOps antes de ser publicada e analisa o próprio processo com mineração de processos.

## 02 · Agenda (~15 s)

Vamos mostrar primeiro a arquitetura, depois a plataforma rodando de verdade, no terminal e no dashboard, a parte de operação, com monitoramento e DevSecOps, e por fim a análise do processo com mineração.

## 03 · Arquitetura final (~55 s)

Na entrada, temos o Arduino simulado no TinkerCad e o simulador de campo, com 5 talhões por 7 dias, além da câmera e do pluviômetro.

No processamento, os dados brutos entram na camada raw. O script de processamento padroniza, remove duplicadas, valida e cria features. O que é inválido vai para a pasta de rejeitados, com o motivo; o resto vai para a camada trusted.

Na automação e inteligência, o motor de regras, que vem da Fase 4, trabalha junto com um Random Forest que prevê o risco nas próximas 6 horas. A decisão combinada dispara ações automáticas e o relatório da IA Generativa, da Fase 5.

Na saída, ficam a camada refined, o dashboard, os alertas e os relatórios para o produtor.

E embaixo, a faixa de operação: o orquestrador roda um ciclo a cada N segundos, o monitoramento registra tudo, o Docker Compose executa e o GitHub Actions só publica a imagem depois das verificações de segurança.

## 04 · Plataforma em containers (~60 s)

São dois serviços, o pipeline e o dashboard, usando a mesma imagem, e os dois estão healthy.

Aqui vemos um ciclo completo, sem ninguém mexer: coleta, processamento, automação, IA e mineração, cada etapa cronometrada. Recebemos 1.706 leituras, e 1.695 ficaram válidas: 6 duplicadas removidas e 5 rejeitadas com o motivo. A automação encontrou 55 episódios de alerta, e o modelo de Machine Learning teve F1 de 0,949, contra 0,887 da regra reativa.

Agora vamos ver o resultado disso no dashboard.

## 05 · Dashboard: o caso do TAL-02 (~75 s)

No topo, os indicadores principais: temperatura, umidade, luminosidade, alertas críticos e talhões em risco alto.

O TAL-02 está crítico: falha de irrigação com déficit hídrico, e a recomendação é inspecionar a bomba. Já o TAL-03 está em atenção só pelo risco previsto pelo modelo, antes de qualquer regra disparar. A IA explica a situação em linguagem simples para o produtor.

Essa é a entrada: o sensor mostra o solo do TAL-02 secando, com a irrigação desligada e praticamente sem chuva.

O processamento calculou a tendência da umidade em 6 horas e a chuva acumulada em 24 horas, e a saída foi automática: ordem de manutenção aberta, gestor avisado e o card de inspecionar a bomba.

O modelo prevê o evento crítico com 6 horas de antecedência e supera a regra reativa em todas as métricas.

## 06 · Monitoramento (~45 s)

A plataforma sabe quando não está saudável. Cada ciclo é registrado com a duração de cada etapa, e temos disponibilidade, indicadores de qualidade e o log estruturado.

No terminal, o healthcheck confirma: a plataforma está saudável, e as quatro verificações passaram.

Também testamos uma falha controlada: corrompemos o arquivo serial do TinkerCad, o ciclo falhou, o container ficou unhealthy e o erro apareceu nessa aba. Restauramos o arquivo, e o ciclo seguinte voltou a healthy. Naquele teste, a disponibilidade registrada foi de 85,7%, 6 de 7 ciclos, e o incidente fica no histórico.

## 07 · Pipeline DevSecOps (~45 s)

São 9 verificações em três blocos: qualidade, com ruff e 19 testes no pytest; segurança, com bandit, pip-audit e gitleaks; e build, com Trivy na configuração, build da imagem, Trivy na imagem e smoke test.

A primeira execução foi reprovada de verdade: o Trivy achou 38 vulnerabilidades HIGH e CRITICAL na imagem base, e containers da Fase 4 rodavam como root. Corrigimos com a atualização dos pacotes no build e um usuário sem privilégio, e a segunda execução passou. A imagem só é publicada no GHCR depois de tudo aprovado.

## 08 · Mineração de processos (~45 s)

Cada ocorrência no campo vira um caso no event log: o caso é o talhão, a regra e o início, e as atividades vêm das saídas reais da plataforma: risco previsto, alerta, ação automática, gestor notificado, ordem de manutenção, escalado e normalizada. São 55 casos, 246 eventos e 16 variantes. O mesmo log sai em XES, para ProM, Disco ou pm4py.

No mapa, a espessura é o número de casos, e o vermelho marca esperas de 12 horas ou mais.

As três variantes principais cobrem 70,9% dos casos; os problemas estão nas outras 13.

## 09 · Gargalos (~20 s)

Achamos três gargalos. Primeiro, a manutenção sem retorno: a ordem é aberta, mas não tem SLA nem evento de manutenção concluída, e leva 45 horas. Segundo, o crítico esperando o clima: na temperatura extrema, a ação só aumenta a leitura e avisa, e o caso espera 10 horas. Terceiro, a infestação nunca fecha, porque não existe a atividade "tratamento aplicado". No processo técnico, a mineração ocupa a maior parte do ciclo, e o modelo é retreinado toda vez, mesmo sem dados novos.

## 10 · Variações (~20 s)

E três variações. O déficit hídrico resolve em 3 horas com a bomba funcionando, mas se arrasta por 47 horas com a bomba quebrada, porque o processo não verifica se a ação funcionou. O modelo antecipa 61% das ocorrências críticas, com 4,7 horas de antecedência, mas a previsão não dispara nenhuma ação. E há reincidência: temperatura extrema e movimento noturno se repetem quase toda noite.

## 11 · Melhorias e processo ideal (~25 s)

Cada achado virou uma melhoria: ação preventiva disparada pelo Machine Learning; verificar o efeito da ação em 1 hora; SLA de manutenção, de 45 para menos de 8 horas; a atividade "tratamento aplicado", com foto da câmera; agrupar alertas repetidos; proteção programada para padrões recorrentes, como a geada no TAL-05; e um pipeline mais rápido, que já aplicamos em parte no Dockerfile.

Esse é o processo ideal: o risco alto já gera a ação preventiva, e o alerta nem chega a acontecer.

## 12 · Encerramento (~25 s)

O AgroSmart é uma solução completa, ponta a ponta: coleta, processa, decide e age sozinho; roda em containers, se monitora e só é publicado depois de passar pelas verificações de segurança; e usa a mineração de processos para descobrir a próxima melhoria. Os próximos passos são sensores físicos via MQTT ou LoRaWAN, a ação preventiva disparada pelo Machine Learning e um piloto com uma cooperativa. Obrigado!
