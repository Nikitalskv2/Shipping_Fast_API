FROM python:alpine

WORKDIR /worker

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "worker.py", "--port", "7000"]
