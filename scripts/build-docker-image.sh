#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."                      # run from the repo root, wherever you call it from
docker build -f docker/sandbox.Dockerfile -t rh-sandbox:1 docker/