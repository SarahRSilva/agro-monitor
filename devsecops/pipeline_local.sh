#!/usr/bin/env bash
# Pipeline DevSecOps local — mesmas etapas do .github/workflows/devsecops.yml.
# Grava todos os relatórios em docs/fase7/evidencias/devsecops/ (evidência da execução).
#
# Pré-requisitos: .venv com requirements-dev.txt instalado e Docker rodando.
# Uso:  ./devsecops/pipeline_local.sh
set -uo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-.venv/bin/python}
BIN=$(dirname "$PY")
OUT=docs/fase7/evidencias/devsecops
IMAGEM=agrosmart:7.0.0
TRIVY=aquasec/trivy:0.58.1
mkdir -p "$OUT"
RESUMO="$OUT/00_resumo_pipeline.txt"
: > "$RESUMO"
FALHAS=0

etapa() {  # etapa "<nome>" "<arquivo de saída>" comando...
  local nome=$1 saida=$2; shift 2
  local t0=$(date +%s)
  printf '\n=== %s ===\n' "$nome"
  if "$@" > "$OUT/$saida" 2>&1; then st="OK"; else st="FALHOU"; FALHAS=$((FALHAS+1)); fi
  local dt=$(( $(date +%s) - t0 ))
  tail -n 6 "$OUT/$saida"
  printf '%-48s %-7s %4ss  -> %s\n' "$nome" "$st" "$dt" "$saida" | tee -a "$RESUMO"
}

echo "Pipeline DevSecOps AgroSmart — $(date '+%Y-%m-%d %H:%M:%S') — commit $(git rev-parse --short HEAD 2>/dev/null)" | tee -a "$RESUMO"

# 1. Qualidade
etapa "1.1 Lint + complexidade (ruff)"                 01_ruff.txt          "$BIN/ruff" check . --statistics
etapa "1.2 Testes + cobertura (pytest)"                02_pytest.txt        "$BIN/pytest" --cov --cov-report=term --cov-fail-under=40 --junitxml="$OUT/junit.xml"
# 2. Segurança do código e dependências
etapa "2.1 SAST (bandit)"                              03_bandit.txt        "$BIN/bandit" -c pyproject.toml -r . --severity-level low
etapa "2.2 SCA dependências (pip-audit)"               04_pip_audit.txt     "$BIN/pip-audit" -r requirements.txt --strict
etapa "2.3 Segredos no repositório (trivy secret)"     05_segredos.txt      docker run --rm -v "$PWD:/src:ro" "$TRIVY" fs --scanners secret --skip-dirs /src/.venv --exit-code 1 /src
# 3. Build e container
etapa "3.1 Scan do Dockerfile/compose (trivy config)"  06_trivy_config.txt  docker run --rm -v "$PWD:/src:ro" "$TRIVY" config --severity HIGH,CRITICAL --exit-code 1 /src
etapa "3.2 Build da imagem (docker build)"             07_docker_build.txt  docker build -t "$IMAGEM" .
etapa "3.3 Vulnerabilidades da imagem (trivy image)"   08_trivy_image.txt   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock "$TRIVY" image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 "$IMAGEM"
etapa "3.4 Smoke test do container (ciclo + health)"   09_smoke_test.txt    bash -c "docker volume rm -f agro-smoke >/dev/null 2>&1; \
  docker run --rm --read-only --tmpfs /tmp -v agro-smoke:/app/dados $IMAGEM python run_plataforma.py && \
  docker run --rm -v agro-smoke:/app/dados $IMAGEM python monitoramento/healthcheck.py; rc=\$?; docker volume rm -f agro-smoke >/dev/null; exit \$rc"

echo "" | tee -a "$RESUMO"
if [ "$FALHAS" -eq 0 ]; then echo "RESULTADO: pipeline aprovado (todas as etapas OK)" | tee -a "$RESUMO"
else echo "RESULTADO: $FALHAS etapa(s) falharam — ver relatórios em $OUT" | tee -a "$RESUMO"; fi
exit "$FALHAS"
