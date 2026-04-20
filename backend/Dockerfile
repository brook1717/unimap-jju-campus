# ═══════════════════════════════════════════════════════════════════════════
# Stage 1 — Builder: install Python dependencies into a virtual-env
# ═══════════════════════════════════════════════════════════════════════════
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build deps for psycopg2 and GDAL Python bindings
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

# ═══════════════════════════════════════════════════════════════════════════
# Stage 2 — Runtime: lean image with only what's needed to run
# ═══════════════════════════════════════════════════════════════════════════
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# GeoDjango runtime dependencies (GDAL, GEOS, PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal34 \
    libgeos-c1v5 \
    libpq5 \
    && ldconfig \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built virtual-env from builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Create non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app
USER app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
