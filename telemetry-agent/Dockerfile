FROM python:3.11-slim
WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Expõe porta de métricas
EXPOSE 8000

# Executa collector
CMD ["python", "src/telemetry_collector.py"]
