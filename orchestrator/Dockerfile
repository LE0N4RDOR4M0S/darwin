FROM python:3.11
WORKDIR /app
COPY orchestrator.py .
RUN pip install fastapi uvicorn requests
CMD ["uvicorn", "orchestrator:app", "--host", "0.0.0.0", "--port", "5002"]
