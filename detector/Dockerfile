FROM python:3.11-slim
WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

EXPOSE 5004

# Variáveis padrão
ENV PROMETHEUS_URL=http://prometheus:9090
ENV ORCHESTRATOR_URL=http://orchestrator:5003
ENV CHECK_INTERVAL=30

CMD ["uvicorn", "detector:app", "--host", "0.0.0.0", "--port", "5004"]
