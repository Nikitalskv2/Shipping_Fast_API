FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app, config.py .


CMD ["uvicorn", "app.main:app", "--workers 4", "--host", "0.0.0.0", "--port", "3000"]
