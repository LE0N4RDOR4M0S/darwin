from fastapi import FastAPI, BackgroundTasks
import requests
import os
import time
import json

app = FastAPI(title="Código Vivo - Hotspot Detector", version="1.0.0")

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:5003")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))

def read_query(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "queries", filename)
    with open(path, "r") as f:
        return f.read().strip()

def run_promql(query: str):
    try:
        resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        data = resp.json()
        return data.get("data", {}).get("result", [])
    except Exception as e:
        print(f"❌ Erro ao consultar Prometheus: {e}")
        return []

def detect_hotspots():
    print("🔍 Iniciando varredura de métricas no Prometheus...")

    latency_query = read_query("latency_query.promql")
    error_query = read_query("error_query.promql")
    cpu_query = read_query("cpu_usage.promql")

    latency_results = run_promql(latency_query)
    error_results = run_promql(error_query)
    cpu_results = run_promql(cpu_query)

    hotspots = []

    for res in latency_results:
        try:
            endpoint = res["metric"].get("uri", "unknown")
            value = float(res["value"][1])
            if value > 2.0:
                hotspots.append({
                    "type": "latency",
                    "endpoint": endpoint,
                    "p95": value
                })
        except Exception:
            continue

    for res in error_results:
        try:
            endpoint = res["metric"].get("uri", "unknown")
            value = float(res["value"][1])
            if value > 0.05:
                hotspots.append({
                    "type": "error_rate",
                    "endpoint": endpoint,
                    "error_rate": value
                })
        except Exception:
            continue

    for res in cpu_results:
        try:
            instance = res["metric"].get("instance", "unknown")
            value = float(res["value"][1])
            if value > 0.8:
                hotspots.append({
                    "type": "cpu_usage",
                    "instance": instance,
                    "usage": value
                })
        except Exception:
            continue

    if hotspots:
        try:
            print(f"🚨 Hotspots detectados: {len(hotspots)}")
            payload = {"hotspots": hotspots, "timestamp": time.time()}
            requests.post(f"{ORCHESTRATOR_URL}/hotspot", json=payload)
        except Exception as e:
            print(f"❌ Falha ao notificar Orchestrator: {e}")
    else:
        print("✅ Nenhum hotspot detectado nesta varredura.")


def schedule_detection():
    while True:
        detect_hotspots()
        time.sleep(CHECK_INTERVAL)


@app.on_event("startup")
def on_startup():
    print("🚀 Detector iniciado, monitorando métricas...")
    import threading
    t = threading.Thread(target=schedule_detection, daemon=True)
    t.start()


@app.get("/health")
def health():
    return {"status": "ok", "interval": CHECK_INTERVAL, "prometheus": PROMETHEUS_URL}
