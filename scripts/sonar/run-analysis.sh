#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="$ROOT_DIR/reports/coverage"
FRONTEND_DIR="$ROOT_DIR/interface-web"

mkdir -p "$REPORTS_DIR/frontend"

echo "Gerando cobertura do backend..."
(
  cd "$ROOT_DIR"
  pytest \
    --cov=backend/app \
    --cov=backend/pipeline_busca/src \
    --cov=backend/pipeline_indexador/src \
    --cov-report=xml:"$REPORTS_DIR/backend-coverage.xml"
)

echo "Gerando cobertura do frontend..."
(
  cd "$FRONTEND_DIR"
  npm run test:coverage
)

echo "Executando scanner..."
(
  cd "$ROOT_DIR"
  sonar-scanner
)
