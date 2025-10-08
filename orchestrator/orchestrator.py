from fastapi import FastAPI
import requests, os, json

app = FastAPI(title="Código Vivo - Orchestrator")

GENERATOR_URL = os.getenv("GENERATOR_URL", "http://generator:5000/generate")
EVALUATOR_URL = os.getenv("EVALUATOR_URL", "http://evaluator:5001/evaluate")


@app.post("/hotspot")
def handle_hotspot(hotspot: dict):
    # Retry logic for contacting generator (DNS / startup races)
    max_retries = 5
    backoff = 0.5
    gen_res = None
    last_exc = None
    for attempt in range(max_retries):
        try:
            gen_res = requests.post(GENERATOR_URL, json=hotspot, timeout=10)
            break
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries} failed contacting generator: {e}")
            last_exc = e
            time_to_sleep = backoff * (2 ** attempt)
            import time
            time.sleep(time_to_sleep)

    if gen_res is None:
        return {"error": "generator_unreachable", "detail": str(last_exc)}
    if gen_res.status_code != 200:
        return {"error": "generator_failed", "status_code": gen_res.status_code, "body": gen_res.text}

    gen_json = gen_res.json()
    branch = gen_json.get("branch")
    candidate = gen_json.get("candidate")

    print(f"Pipeline iniciado para branch: {branch}")

    if candidate is not None:
        # prepare multipart with baseline file and candidate json
        baseline_fp = open('../tests/baseline.json', 'rb')
        candidate_bytes = (None, os.path.basename('candidate.json'), json.dumps(candidate).encode('utf-8'))

        # requests accepts (filename, fileobj) or tuple (filename, content, content_type)
        files = {
            'baseline': ('baseline.json', baseline_fp),
            'candidate': ('candidate.json', json.dumps(candidate), 'application/json')
        }

        decision_resp = requests.post(EVALUATOR_URL, files=files)
        baseline_fp.close()
        if decision_resp.status_code != 200:
            return {"error": "evaluator_failed", "status_code": decision_resp.status_code, "body": decision_resp.text}

        decision = decision_resp.json()
    else:
        decision = {"decision": "no_candidate_metrics", "note": "Generator did not return candidate metrics"}

    print("Decisão:", decision)
    return {"branch": branch, "evaluation": decision}
