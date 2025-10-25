# --- Stage 1: Base image ---
FROM python:3.11-slim AS base

WORKDIR /app

# Giảm layer cache bằng cách copy requirements trước
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY app .

EXPOSE 8000

CMD ["python", "main.py"]
