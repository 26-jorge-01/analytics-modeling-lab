FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DAGSTER_HOME=/opt/dagster/dagster_home

# System deps (psycopg2 build + basic tooling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python deps
COPY orchestration/dagster/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy Dagster home config + project code
RUN mkdir -p ${DAGSTER_HOME}
COPY orchestration/dagster/dagster_home/ ${DAGSTER_HOME}/
COPY orchestration/dagster/dagster_project/ /app/orchestration/dagster/dagster_project/

# Entry point
COPY orchestration/dagster/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000
ENTRYPOINT ["/entrypoint.sh"]
