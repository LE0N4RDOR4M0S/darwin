import json
from fastapi.testclient import TestClient
from evaluator import app


client = TestClient(app)


def test_approve_auto():
    baseline = {"p95": 500, "error_rate": 0.01}
    candidate = {"p95": 400, "error_rate": 0.009}
    files = {
        'baseline': ('baseline.json', json.dumps(baseline), 'application/json'),
        'candidate': ('candidate.json', json.dumps(candidate), 'application/json')
    }
    resp = client.post('/evaluate', files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert body['decision'] == 'approve_auto'


def test_reject():
    baseline = {"p95": 500, "error_rate": 0.01}
    candidate = {"p95": 520, "error_rate": 0.015}
    files = {
        'baseline': ('baseline.json', json.dumps(baseline), 'application/json'),
        'candidate': ('candidate.json', json.dumps(candidate), 'application/json')
    }
    resp = client.post('/evaluate', files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert body['decision'] == 'reject'
