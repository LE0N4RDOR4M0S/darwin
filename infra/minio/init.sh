#!/bin/sh
set -e

echo "🚀 Iniciando MinIO com configuração personalizada..."

export MINIO_ROOT_USER=${MINIO_ROOT_USER:-admin}
export MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-changeme123}

minio server /data --console-address ":9001" &

sleep 5

mc alias set local http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb -p local/artifacts || true
mc mb -p local/telemetry || true
mc mb -p local/patches || true

echo "✅ Buckets criados: artifacts, telemetry, patches"
wait
