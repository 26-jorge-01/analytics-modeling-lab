## A) Roadmap por fases (semanas) + dependencias

|Fase|Objetivo|Dependencias|Deliverables visuales/tangibles|
|---|---|---|---|
|MVP|“De 0 a lab corriendo”: raw→stg→marts star mínimo + 1 dashboard|Docker/Compose|Dagster UI, dbt docs, Metabase 1 dashboard, screenshots, dbt tests|
|v1|Modelado completo: 3NF + Data Vault + Star + DQ suite + CI|MVP|ERD 3NF, DV diagram, lineage dbt, DQ report, CI green|
|v2|Snowflake + Galaxy + observabilidad/alertas + incrementales robustos + features churn opcional|v1|Fact constellation diagram, métricas pipeline, alertas simuladas, 3 dashboards finales|

## B) Checklist por fase + Definition of Done (DoD)

### MVP

**Meta:** cualquiera clona y ve “un modelo analítico funcionando” + orquestación básica.

### Checklist (MVP)

**Infra / repo**

- [] Crear repo + estructura base (ver sección H).

- [] Crear .env.example + Makefile + Compose.

- [] Levantar contenedores: Postgres, Dagster (web+daemon), Metabase.

**Datos**

- [] Descargar dataset público e-commerce (CSV) → data/raw/

- [] Script Python: generate_synthetic.py para suscripciones/devoluciones/envíos (si faltan).

- [] Script Python: extract_load.py para cargar a raw.* en Postgres.

**Transformaciones**

- [] dbt: stg_* + marts_star mínimo:

    - [] dim_date, dim_customer, dim_product

    - [] fct_order_item

- [] dbt tests básicos (unique/not_null/relationships).

**Orquestación**

- [] Dagster assets: raw_load → dbt_build → refresh_metrics.

**BI**

- [] Metabase: 1 dashboard “Star MVP” (ventas por día / top productos).

**Evidencias (screenshots)**

- [] docker compose ps

- [] Dagster UI assets graph + run logs

- [] dbt docs lineage (captura)

- [] dashboard en Metabase

### DoD (MVP)

- make up && make ingest && make dbt-build funciona sin errores.

- dbt test pasa.

- 1 dashboard visible con filtros (fecha/categoría).

## v1

**Meta:** demostrar “cuándo y por qué” 3NF + DV + Star con documentación y calidad seria.

**Checklist (v1)**

**3NF (core)**

- [] Modelos dbt en models/core_3nf/ (tablas normalizadas).

- [] ERD Mermaid en docs/diagrams/erd_3nf.mmd.

- [] dbt tests de integridad referencial + constraints.

**Data Vault**

- [] Hubs/Links/Sats en models/dv/.

- [] DV Mermaid en docs/diagrams/datavault.mmd.

- [] Ejemplo de historia: sat con effective_from.

**Star robusto**

- [] marts/star/ completo (facts: ventas, devoluciones, envíos, pagos).

- [] Definir grano y KPIs en docs.

**Calidad & gobernanza**

- [] Elegir Soda (simple y mostrable):

    - quality/soda/checks.yml con 10–15 checks

    - generar reporte a docs/reports/

- [] dbt contracts: schema.yml completo en staging/core/dv/marts.

- [] Linters: ruff + sqlfluff (opcional) + pytest.

**CI**

- [] GitHub Actions: lint + unit tests + dbt build (en contenedor).

**Evidencias (screenshots)**

- [] ERD 3NF

- [] DV diagram

- [] dbt docs lineage con 3 ramas (3NF/DV/marts)

- [] reporte de Soda

- [] GitHub Actions green

### DoD (v1)

- make test corre: lint + unit + dbt build + soda scan

- Documentación lista (diagramas + decisiones).

- Lineage visible y entendible.

## v2

**Meta:** Snowflake + Galaxy + observabilidad/alertas + incrementales + features churn opcional.

**Checklist (v2)**

**Snowflake**

- [] Normalizar dims: dim_product → dim_category (+ jerarquía).

- [] Documentar “por qué snowflake aquí”.

**Galaxy**

- [] Fact constellation:

    - fct_sales_item

    - fct_returns

    - fct_shipments

    - fct_subscription_revenue

- [] Dims conformadas compartidas (dim_customer, dim_product, dim_date).

**Incrementales**

- [] dbt incremental en facts grandes (watermark por fecha).

- [] Demostración: ejecutar 2 veces y comparar rows/duración.

**Observabilidad**

- [] Tabla ops.pipeline_run_metrics

- [] Dagster: asset que inserta métricas por corrida.

- [] Alertas simuladas:

    - si return_rate > 0.15 → crear alerts/alert_<run_id>.md

**BI**

- [] 3 dashboards finales (ver sección F) con screenshots.

**Features churn (opcional)**

- [] features_customer_churn (tabla) + notebook demo.

### DoD (v2)

- make run (job completo) genera métricas + posible alerta.

- Galaxy diagram + lineage dbt con múltiples facts.

- 3 dashboards con preguntas “tipo de análisis”, no “negocio”.

## C) Arquitectura final + cómo se ve en Docker Compose

**Componentes**

* **Postgres:** almacén local con schemas: raw, staging, core_3nf, dv, marts, ops

* **dbt:** transformaciones + docs + tests (contracts)

* **Dagster:** orquestación (assets + schedules)

* **Soda:** DQ suite (YAML)

* **Metabase:** dashboards

Qué screenshot

* docker compose ps

* Dagster UI (assets graph)

* Metabase conectado a Postgres

## D) Diseño de modelos (qué construir y propósito)

### 1) 3NF (core_3nf)

**Propósito:** integridad + mínima redundancia (modelo “referencia”).

**Tablas (alto nivel + keys)**

* customers(customer_id PK)

* products(product_id PK)

* categories(category_id PK, parent_category_id FK)

* orders(order_id PK, customer_id FK)

* order_items(order_item_id PK, order_id FK, product_id FK)

* payments(payment_id PK, order_id FK)

* shipments(shipment_id PK, order_id FK)

* returns(return_id PK, order_id FK, product_id FK)

* plans(plan_id PK)

* subscriptions(subscription_id PK, customer_id FK, plan_id FK)

* subscription_events(event_id PK, subscription_id FK)

**Qué mostrar**

* ERD Mermaid + tests de FKs

### 2) Data Vault (dv)

**Propósito:** historia y auditoría (cambios en el tiempo).

**Hubs**

* h_customer(hk_customer, customer_bk)

* h_product(hk_product, product_bk)

* h_order(hk_order, order_bk)

* h_subscription(hk_subscription, subscription_bk)

**Links**

* l_order_customer(hk_order, hk_customer)

* l_order_product(hk_order, hk_product)

* l_subscription_customer(hk_subscription, hk_customer)

**Satellites**

* s_customer_profile(hk_customer, effective_from, email, country, …)

* s_order_status(hk_order, effective_from, status, channel, …)

* s_product_attrs(hk_product, effective_from, category, price, …)

* s_subscription_status(hk_subscription, effective_from, plan, status, …)

**Qué mostrar**

* DV diagram + query “estado actual vs histórico”

### 3) Star (marts_star)

**Propósito:** consumo BI simple y rápido.

**Dims**

* dim_date(date_key)

* dim_customer(customer_key)

* dim_product(product_key)

* dim_channel(channel_key)

**Fact + grano**

* fct_order_item grano = 1 fila por (order_id, product_id)

**KPIs ejemplo**

* net_revenue, gross_revenue, discount_amount, qty

**Qué mostrar**

* dbt lineage + dashboard de agregados

### 4) Snowflake (marts_snowflake)

**Propósito:** dimensiones jerárquicas / gobernanza.

* dim_product → dim_category (y subcategoría si aplica)

**Qué mostrar**

* diagrama y query jerárquica

### 5) Galaxy / Fact Constellation (marts_galaxy)

**Propósito:** múltiples procesos compartiendo dims conformadas.

**Facts**

* fct_sales_item

* fct_returns

* fct_shipments

* fct_subscription_revenue

**Shared dims**

* dim_customer, dim_product, dim_date

**Qué mostrar**

* diagrama constelación + dashboard cruzado (ventas vs devoluciones vs retrasos)

## E) Plan de datos y pipelines (exacto)

### Ingestión (raw → staging)

**Construir**

* ingestion/sql/raw_tables.sql (DDL)

* ingestion/extract_load.py (carga CSV a raw.*)

* ingestion/generate_synthetic.py (suscripciones/envíos/devoluciones)

**Comandos**

* make ingest

**Evidencias**

* screenshot: conteo de filas en raw.*

### Validaciones

* dbt tests (rápido)

* unique, not_null, relationships

**Soda (suite visible)**

**Archivos**

* quality/soda/configuration.yml

* quality/soda/checks.yml

**Ejemplos de checks**

* missing_count, duplicates, min/max, freshness, valid_values

**Comandos**

* make dq

**Evidencia**

* screenshot del reporte

### Transformaciones (staging → core → dv → marts)

**dbt modelos**

* models/staging/*.sql

* models/core_3nf/*.sql

* models/dv/*.sql

* models/marts/star/*.sql

* models/marts/snowflake/*.sql

* models/marts/galaxy/*.sql

**Comandos**

* make dbt-build

* dbt docs generate (incluido en Make opcional)

**Evidencia**

* screenshot de dbt docs lineage

### Incrementales

Aplicar a fct_sales_item, fct_shipments (tablas grandes).

* materialized incremental + watermark por order_ts.

**Evidencia**

* 2 runs: screenshot rows y duración.

## F) Dashboards / reportes (mínimo 3) “no negocio”

Son dashboards para comparar modelos y tipos de preguntas, no para “empresa”.

**Dashboard 1 — “Star: Aggregation Playground”**

* time series net_revenue

* top products

* AOV

**Dashboard 2 — “Data Vault: History & Change”**

* cambios de estado de orden por tiempo

* cambios de plan/estado suscripción

**Dashboard 3 — “Galaxy: Multi-Fact Lens”**

* ventas vs devoluciones vs retrasos (join de facts con dims conformadas)

**Screenshots**

* 1 por dashboard + 1 de filtros

## G) Extras para lucirte + evidencia exacta
|Extra|Qué haces|Archivo(s)|Evidencia|
|---|---|---|---|
|CI|GitHub Actions: lint + tests + dbt|.github/workflows/ci.yml|badge + screenshot pipeline verde|
|Lint|ruff + black (o solo ruff format)|pyproject.toml|make lint output|
|Contracts|dbt schema.yml completo|models/**/schema.yml|screenshot dbt test|
|DQ suite|Soda checks|10–15	quality/soda/checks.yml|reporte + screenshot|
|Observabilidad|métricas por run + alerta|ops/metrics/*.sql, dagster asset|tabla ops.pipeline_run_metrics + alert md|
|Docs|dbt docs + Mermaid diagrams|docs/diagrams/*|screenshots de diagramas + lineage|

## H) Estructura del repo (recomendada)
analytics-modeling-lab/
  README.md
  Makefile
  docker-compose.yml
  .env.example

  ingestion/
    extract_load.py
    generate_synthetic.py
    sql/raw_tables.sql

  transform/dbt/
    dbt_project.yml
    profiles.yml.example
    models/
      staging/
      core_3nf/
      dv/
      marts/
        star/
        snowflake/
        galaxy/
    macros/
    tests/

  orchestration/dagster/
    Dockerfile
    dagster_project/
      assets.py
      jobs.py
      schedules.py
      resources.py

  quality/soda/
    configuration.yml
    checks.yml

  ops/metrics/
    create_ops_tables.sql

  docs/
    diagrams/
      erd_3nf.mmd
      datavault.mmd
      star.mmd
      snowflake.mmd
      galaxy.mmd
    screenshots/
    reports/
    alerts/

## I) README outline + qué screenshots poner

1. What this lab is (and isn’t)

2. Dataset & Generation

    - screenshot: raw tables row counts

3. Architecture (Docker + Dagster + dbt + Soda + Metabase)

    - screenshot: docker compose ps

    - screenshot: Dagster graph

4. Modeling Layers

    - 3NF ERD screenshot

    - Data Vault diagram screenshot

    - Star/Snowflake/Galaxy diagrams screenshots

5. How to run

    - quickstart commands

6. Data Quality & Contracts

    - screenshot: Soda report

    - screenshot: dbt test

7. Dashboards

    - 3 dashboard screenshots

8. Observability

    - screenshot: ops.pipeline_run_metrics

    - screenshot: alerta generada (archivo)

9. CI

    - badge + screenshot actions

10. Roadmap (MVP → v1 → v2)

## J) Comandos Quickstart (para cualquiera)

**Makefile (mínimo)**
```
up:
	docker compose up -d --build

down:
	docker compose down -v

ingest:
	docker compose exec dagster-web python /app/ingestion/extract_load.py
	docker compose exec dagster-web python /app/ingestion/generate_synthetic.py

dbt-build:
	docker compose exec dagster-web bash -lc "cd /app/transform/dbt && dbt build"

dq:
	docker compose exec dagster-web bash -lc "cd /app/quality/soda && soda scan -d postgres -c configuration.yml checks.yml"

docs:
	docker compose exec dagster-web bash -lc "cd /app/transform/dbt && dbt docs generate"

test:
	docker compose exec dagster-web bash -lc "cd /app/transform/dbt && dbt test"
	$(MAKE) dq
```

**Quickstart en README**

1. cp .env.example .env

2. make up

3. make ingest

4. make dbt-build

5. make dq

6. abrir:

    - Dagster: http://localhost:3000

    - Metabase: http://localhost:3001