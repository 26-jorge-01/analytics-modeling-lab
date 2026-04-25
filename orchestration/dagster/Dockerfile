FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DAGSTER_HOME=/opt/dagster/dagster_home

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# upgrade pip
RUN pip install --no-cache-dir -U pip

# dagster home + config (tu carpeta real)
RUN mkdir -p ${DAGSTER_HOME}
COPY orchestration/dagster/dagster_home/ ${DAGSTER_HOME}/

# tu código (ajusta si quieres copiar solo subcarpetas)
# Install the main project
COPY . /app
RUN pip install -e /app

# entrypoint (ruta real)
COPY orchestration/dagster/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000
ENTRYPOINT ["/entrypoint.sh"]
