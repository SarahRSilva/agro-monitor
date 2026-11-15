# AgroSmart — imagem da plataforma (Fase 7)
# Um único artefato roda os dois papéis: "pipeline" (execução contínua) e "dashboard" (Streamlit).
#
# Boas práticas de segurança aplicadas (verificadas pelo Trivy no pipeline DevSecOps):
#   - imagem base slim com versão fixa       - usuário sem privilégios (UID 10001)
#   - dependências com versão fixa (pip-audit) - sem cache do pip / sem ferramentas de build
#   - multi-stage: wheels compilados no estágio "build", runtime só com o necessário
#   - pacotes do SO atualizados no build    - HEALTHCHECK baseado no status real do pipeline

# ── estágio 1: build das dependências ────────────────────────────────────────
FROM python:3.15.0-slim-bookworm AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# ── estágio 2: runtime ───────────────────────────────────────────────────────
FROM python:3.15.0-slim-bookworm AS runtime
# aplica as correções de segurança do Debian publicadas depois da imagem base
# (1ª execução do pipeline: o Trivy barrou 38 CVEs HIGH/CRITICAL em openssl, gnutls, perl...)
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/*
LABEL org.opencontainers.image.title="agrosmart" \
      org.opencontainers.image.description="AgroSmart — plataforma de monitoramento agrícola inteligente" \
      org.opencontainers.image.version="7.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MPLCONFIGDIR=/app/.cache/matplotlib \
    AGRO_INTERVALO_S=300 \
    AGRO_MAX_IDADE_MIN=15

COPY --from=build /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels \
    && pip uninstall -y pip setuptools wheel 2>/dev/null || true

RUN groupadd --system --gid 10001 agro \
    && useradd --system --uid 10001 --gid agro --home-dir /app --shell /usr/sbin/nologin agro
WORKDIR /app
COPY --chown=agro:agro . .
RUN mkdir -p dados logs .cache/matplotlib && chown -R agro:agro dados logs .cache

USER agro
# pré-aquece o cache de fontes do matplotlib (evita o "cold start" de ~8s no 1º ciclo de mineração)
RUN python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot"

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ["python", "monitoramento/healthcheck.py"]

# padrão: execução contínua do pipeline (o compose sobrescreve para o dashboard)
CMD ["python", "run_plataforma.py", "--loop"]
