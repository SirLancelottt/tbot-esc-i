FROM python:3.10-slim

WORKDIR /app

# Cache'i kırmak için zaman ekleyelim
ARG CACHEBUST=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
