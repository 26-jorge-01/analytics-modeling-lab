@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM ============================
REM ANALYTICS MODELING LAB
REM Simple Task Runner (Windows)
REM ============================

IF "%1"=="" GOTO help

IF "%1"=="up" GOTO up
IF "%1"=="down" GOTO down
IF "%1"=="rebuild" GOTO rebuild
IF "%1"=="ps" GOTO ps
IF "%1"=="logs" GOTO logs

IF "%1"=="ingest" GOTO ingest
IF "%1"=="dbt-build" GOTO dbt_build
IF "%1"=="dbt-test" GOTO dbt_test
IF "%1"=="dbt-docs" GOTO dbt_docs
IF "%1"=="dq" GOTO dq

IF "%1"=="run-all" GOTO run_all
IF "%1"=="reset-db" GOTO reset_db

IF "%1"=="shell-dagster" GOTO shell_dagster
IF "%1"=="shell-postgres" GOTO shell_postgres

IF "%1"=="urls" GOTO urls

GOTO help

REM ============================
:up
echo Starting containers...
docker compose up -d --build
GOTO end

:down
echo Stopping containers...
docker compose down -v
GOTO end

:rebuild
echo Rebuilding everything...
docker compose down -v
docker compose build --no-cache
docker compose up -d
GOTO end

:ps
docker compose ps
GOTO end

:logs
docker compose logs -f --tail=200
GOTO end

REM ============================
:ingest
echo Running ingestion scripts...
docker compose exec dagster-web python /app/ingestion/extract_load.py
docker compose exec dagster-web python /app/ingestion/generate_synthetic.py
GOTO end

REM ============================
:dbt_build
echo Running dbt build...
docker compose exec dagster-web bash -lc "cd /app/transform/dbt && dbt build"
GOTO end

:dbt_test
echo Running dbt tests...
docker compose exec dagster-web bash -lc "cd /app/transform/dbt && dbt test"
GOTO end

:dbt_docs
echo Generating dbt docs...
docker compose exec dagster-web bash -lc "cd /app/transform/dbt && dbt docs generate"
GOTO end

REM ============================
:dq
echo Running data quality checks (Soda)...
docker compose exec dagster-web bash -lc "cd /app/quality/soda && soda scan -d postgres -c configuration.yml checks.yml"
GOTO end

REM ============================
:run_all
echo FULL PIPELINE RUN
call make.bat ingest
call make.bat dbt-build
call make.bat dbt-test
call make.bat dq
echo Pipeline finished.
GOTO end

REM ============================
:reset_db
echo Resetting database...
docker compose down -v
docker compose up -d postgres
echo Waiting 10 seconds for Postgres...
timeout /t 10
docker compose up -d dagster-web dagster-daemon metabase
GOTO end

REM ============================
:shell_dagster
docker compose exec dagster-web bash
GOTO end

:shell_postgres
docker compose exec postgres psql -U demo -d modeling_lab
GOTO end

REM ============================
:urls
echo Dagster UI:  http://localhost:3000
echo Metabase:   http://localhost:3001
GOTO end

REM ============================
:help
echo.
echo Usage: make.bat [command]
echo.
echo Core:
echo   up            Build and start all containers
echo   down          Stop and remove containers
echo   rebuild       Full rebuild from scratch
echo   ps            Show running containers
echo   logs          Tail logs
echo.
echo Data:
echo   ingest        Load raw + synthetic data
echo   dbt-build     Run dbt build
echo   dbt-test      Run dbt tests
echo   dbt-docs      Generate dbt docs
echo   dq            Run data quality checks
echo.
echo Pipelines:
echo   run-all       ingest + dbt-build + dbt-test + dq
echo.
echo Ops:
echo   reset-db      Drop volumes and restart db
echo.
echo Shells:
echo   shell-dagster Open shell inside dagster container
echo   shell-postgres Open psql shell
echo.
echo Utils:
echo   urls          Show local service URLs
echo.

:end
ENDLOCAL
