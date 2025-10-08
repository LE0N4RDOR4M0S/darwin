FROM python:3.11
WORKDIR /app
COPY evaluator.py .
RUN pip install fastapi uvicorn python-multipart
CMD ["uvicorn", "evaluator:app", "--host", "0.0.0.0", "--port", "5001"]
