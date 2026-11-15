FROM python:3.11-slim

WORKDIR /app

# Instala curl para healthcheck
# Fase 7 (DevSecOps): pacotes do SO atualizados e execução sem root (achado AVD-DS-0002 do Trivy)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 10001 --no-create-home agro

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código original do repositório (estrutura idêntica ao agro_monitor original)
COPY main.py gerador.py regras.py ./

RUN mkdir -p /app/dados && chown agro /app/dados

USER agro

EXPOSE 5000

CMD ["python", "main.py"]
