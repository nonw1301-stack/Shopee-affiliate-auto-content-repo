#!/usr/bin/env bash
# Entrypoint that starts the OAuth callback server in background and then runs the runner
set -euo pipefail

# Start uvicorn in background
uvicorn src.tiktok_oauth_callback:app --host 0.0.0.0 --port 8080 &
UVICORN_PID=$!

# Wait briefly for uvicorn to be ready (healthcheck will confirm in compose)
sleep 1

# Run the runner (respecting flags passed to the container)
if [ "$#" -eq 0 ]; then
  exec python -m src.runner --dry-run
else
  exec python -m src.runner "$@"
fi

# On exit, ensure background process is terminated
trap "kill $UVICORN_PID 2>/dev/null || true" EXIT
