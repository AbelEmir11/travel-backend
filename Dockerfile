FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes si aplica
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5000

ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
