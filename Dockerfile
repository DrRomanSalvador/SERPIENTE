FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERPIENTE_HOST=0.0.0.0 \
    SERPIENTE_PORT=8001

WORKDIR /app
COPY pyproject.toml README.md ./
COPY backend ./backend
COPY config ./config

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 serpiente \
    && mkdir -p /data \
    && chown -R serpiente:serpiente /app /data

USER serpiente
VOLUME ["/data"]
EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=3)"

CMD ["serpiente"]
