FROM python:3.11-slim

# Fase 7 (DevSecOps): pacotes do SO atualizados e execução sem root (achado AVD-DS-0002 do Trivy)
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 10001 --no-create-home agro

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consumer.py .

USER agro
CMD ["python", "consumer.py"]
