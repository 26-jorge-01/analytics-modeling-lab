#!/usr/bin/env bash
set -euo pipefail

# Ensure DAGSTER_HOME exists
mkdir -p "${DAGSTER_HOME}"

# Default command if none provided
if [ $# -eq 0 ]; then
  exec dagster-webserver -h 0.0.0.0 -p 3000
else
  exec "$@"
fi
