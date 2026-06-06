# ── Base ──────────────────────────────────────────────────────────────────────
# Usa esta imagen si decides migrar de Azure App Service (ZIP deploy) a
# Azure Container Apps o Azure App Service with Docker.
# Incluye tesseract-ocr para que el backend procese imágenes directamente.
#
# Build:  docker build -t neovate-api .
# Run:    docker run -p 4000:4000 --env-file .env neovate-api

FROM python:3.12-slim

# ── Tesseract OCR + idioma español ────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Directorio de trabajo ─────────────────────────────────────────────────────
WORKDIR /app

# ── Dependencias Python ───────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytesseract

# ── Código fuente ─────────────────────────────────────────────────────────────
COPY . .

# ── Variables de entorno por defecto (sobreescribir con --env-file .env) ──────
ENV PORT=4000 \
    DB_SSLMODE=require

EXPOSE 4000

# ── Arranque ──────────────────────────────────────────────────────────────────
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
