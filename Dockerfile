FROM python:3.10-slim

RUN apt-get update && apt-get install -y pkg-config libcairo2-dev gcc

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
