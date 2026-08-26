FROM python:3.10-slim

ARG APP_VERSION=dev

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_VERSION=${APP_VERSION}

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-mysql-client netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN sed -i 's/\r$//' /app/docker/entrypoint.sh \
    && chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready/', timeout=3)" || exit 1

CMD ["sh", "/app/docker/entrypoint.sh"]
