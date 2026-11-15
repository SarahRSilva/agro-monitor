# 3. Pipeline DevSecOps (20%)

O pipeline automatiza **build, execução via container, análise de qualidade e análise de vulnerabilidades**.
A segurança não é uma etapa final: cada camada (código, dependências, segredos, Dockerfile e imagem) tem
uma verificação que **bloqueia** a entrega se encontrar problema.

## 3.1 Arquivos de configuração

| Arquivo | Papel |
|---|---|
| `.github/workflows/devsecops.yml` | Pipeline no GitHub Actions (push, pull request, manual e semanal) |
| `devsecops/pipeline_local.sh` | Mesmas etapas rodando localmente; grava os relatórios em `docs/fase7/evidencias/devsecops/` |
| `Dockerfile` | Imagem multi-stage, endurecida, com `HEALTHCHECK` |
| `docker-compose.yml` | Execução da plataforma: `pipeline` (contínuo) + `dashboard`, com restrições de segurança |
| `.dockerignore` | Só código e dados de entrada entram na imagem (sem `.git`, `.venv`, testes, docs) |
| `pyproject.toml` | Regras do ruff (lint, complexidade, segurança), pytest, cobertura e bandit |
| `requirements.txt` / `requirements-dev.txt` | Dependências com **versão fixa** (auditáveis e reproduzíveis) |
| `.github/dependabot.yml` | Atualização semanal controlada de dependências pip, imagem base e actions |
| `tests/` | 19 testes: unitários (processamento, regras, ML, mineração, monitoramento) + 1 integração ponta a ponta |

## 3.2 Etapas do pipeline

```
 push / PR / semanal
        │
        ├──► [qualidade]  ruff (lint + complexidade ciclomática ≤ 15) ─► pytest (19 testes, cobertura ≥ 40%)
        │
        ├──► [segurança]  bandit (SAST) ─► pip-audit (SCA, CVEs em dependências) ─► gitleaks (segredos no histórico)
        │
        └──► [build] (só se os dois anteriores passarem)
                 Trivy config (Dockerfile/compose) ─► docker build ─► Trivy image (CVEs HIGH/CRITICAL)
                 ─► SARIF na aba Security ─► smoke test (ciclo real dentro do container + healthcheck)
                 ─► publica no GHCR (somente na main)
```

| Etapa | Ferramenta | Tipo | Critério de bloqueio |
|---|---|---|---|
| Lint + complexidade | **ruff** (regras E, W, F, I, B, C90, S, UP) | Qualidade | qualquer violação |
| Testes + cobertura | **pytest + pytest-cov** | Qualidade | teste falhando ou cobertura < 40% |
| Análise estática de segurança | **bandit** | SAST | achado de severidade média ou maior |
| Vulnerabilidades em dependências | **pip-audit** (base OSV/PyPI) | SCA | qualquer CVE conhecida |
| Segredos | **gitleaks** (CI) / **trivy secret** (local) | Secret scanning | qualquer segredo encontrado |
| Configuração de container | **Trivy config** | IaC / misconfiguration | achado HIGH ou CRITICAL |
| Build | **docker build** | Build | erro de build |
| Vulnerabilidades da imagem | **Trivy image** | Container scanning | CVE HIGH/CRITICAL com correção disponível |
| Execução via container | **docker run** + `healthcheck.py` | Smoke test | ciclo com erro ou plataforma não saudável |

O agendamento semanal (`cron`) re-escaneia a imagem mesmo sem commits: CVEs novas aparecem todos os dias.

## 3.3 Endurecimento do container

| Medida | Onde |
|---|---|
| Imagem base `slim` com versão fixa + `apt-get upgrade` no build | `Dockerfile` |
| Multi-stage: wheels compilados no estágio `build`; runtime sem ferramentas de compilação e sem `pip` | `Dockerfile` |
| Usuário sem privilégios (UID 10001, shell `nologin`) | `Dockerfile` (`USER agro`) |
| Sistema de arquivos somente leitura; só `dados/`, `logs/` e `/tmp` graváveis | `docker-compose.yml` (`read_only`, `tmpfs`) |
| Sem capabilities do kernel e sem escalonamento de privilégio | `cap_drop: [ALL]`, `no-new-privileges` |
| Limite de CPU e memória; rotação dos logs do Docker | `deploy.resources`, `logging` |
| Segredos (chave da Anthropic) só por variável de ambiente, nunca na imagem | `docker-compose.yml` |
| API da Fase 4 escuta só em `127.0.0.1` por padrão (`API_HOST` no compose) | `docker/api/main.py` — achado B104 do bandit |
| Dockerfiles da Fase 4 passaram a rodar sem root | `docker/*/Dockerfile` — achado AVD-DS-0002 do Trivy |

## 3.4 Evidência da execução — o pipeline barrou problemas reais

A **primeira execução foi reprovada** (`evidencias/devsecops_execucao1_reprovada/`). Corrigimos cada achado e a
**segunda execução foi aprovada** (`evidencias/devsecops/`):

| Etapa | Execução 1 | Achado | Correção | Execução 2 |
|---|---|---|---|---|
| ruff | ❌ | import fora de ordem em arquivo novo | `ruff --fix` | ✅ |
| pytest | ✅ (19) | o teste ponta a ponta já tinha achado antes um bug da Fase 6: com < 6 dias de dados o ML quebrava | divisão temporal 70/30 para janelas curtas | ✅ 19 testes, 46% |
| bandit | ✅ | (B104 e B406 corrigidos antes, durante o desenvolvimento) | — | ✅ 0 achados em 3.114 linhas |
| pip-audit | ✅ | — | — | ✅ nenhuma vulnerabilidade |
| segredos | ✅ | — | — | ✅ |
| Trivy config | ❌ | 3 Dockerfiles da Fase 4 rodando como **root** (AVD-DS-0002, HIGH) | `USER` sem privilégio | ✅ |
| docker build | ✅ | — | — | ✅ |
| Trivy image | ❌ | **38 CVEs** (31 HIGH, 7 CRITICAL) na base Debian: openssl, gnutls, perl, apt… | `apt-get upgrade` no build | ✅ **0** HIGH/CRITICAL |
| smoke test | ❌ | com `--read-only` e sem volume de logs, o logger quebrava a plataforma | log em arquivo vira opcional (cai para o console) | ✅ ciclo ok + healthy |

Resumo da execução aprovada (`evidencias/devsecops/00_resumo_pipeline.txt`):

```
1.1 Lint + complexidade (ruff)                   OK         0s  -> 01_ruff.txt
1.2 Testes + cobertura (pytest)                  OK         5s  -> 02_pytest.txt
2.1 SAST (bandit)                                OK         0s  -> 03_bandit.txt
2.2 SCA dependências (pip-audit)                 OK         3s  -> 04_pip_audit.txt
2.3 Segredos no repositório (trivy secret)       OK         0s  -> 05_segredos.txt
3.1 Scan do Dockerfile/compose (trivy config)    OK         7s  -> 06_trivy_config.txt
3.2 Build da imagem (docker build)               OK        33s  -> 07_docker_build.txt
3.3 Vulnerabilidades da imagem (trivy image)     OK        26s  -> 08_trivy_image.txt
3.4 Smoke test do container (ciclo + health)     OK         4s  -> 09_smoke_test.txt
RESULTADO: pipeline aprovado (todas as etapas OK)
```

Outro achado que motivou o pipeline: ao preparar a Fase 7, `pip install -r requirements.txt` instalou o
**pandas 3.0** e a plataforma da Fase 6 parou de funcionar (`TypeError: unary '-' not supported for dtype 'str'`).
Por isso as dependências agora têm versão fixa e só mudam via Dependabot, passando pelo pipeline.

## 3.5 Como rodar

```bash
pip install -r requirements-dev.txt
./devsecops/pipeline_local.sh            # local (precisa do Docker para as etapas 2.3 a 3.4)
```

No GitHub: qualquer `push`/PR dispara o workflow **DevSecOps**; os relatórios ficam em *Artifacts* da execução e
as vulnerabilidades da imagem aparecem em *Security → Code scanning*.
