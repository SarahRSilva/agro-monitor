FROM python:3.11-slim

WORKDIR /app

# Instala curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código original do repositório (estrutura idêntica ao agro_monitor original)
COPY main.py gerador.py regras.py ./

RUN mkdir -p /app/dados

EXPOSE 5000

CMD ["python", "main.py"]
