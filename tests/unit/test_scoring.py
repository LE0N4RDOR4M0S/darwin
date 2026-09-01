import pytest
from metrics.scoring import evaluate_metrics


def test_evaluate_metrics_auto_approve():
    baseline = {"latency_p95": 2.0, "error_rate": 0.10, "cpu_usage": 0.80}
    candidate = {"latency_p95": 1.0, "error_rate": 0.02, "cpu_usage": 0.50}

    res = evaluate_metrics(baseline, candidate)
    assert res["decision"] == "approve_auto"
    assert res["score"] > 10.0
    assert res["delta_latency_pct"] == 50.0
    assert res["confidence"] > 0.0


def test_evaluate_metrics_reject():
    baseline = {"latency_p95": 1.0, "error_rate": 0.02, "cpu_usage": 0.50}
    candidate = {"latency_p95": 2.5, "error_rate": 0.10, "cpu_usage": 0.90}

    res = evaluate_metrics(baseline, candidate)
    assert res["decision"] == "reject"
    assert res["score"] < 0.0


def test_evaluate_metrics_zero_baseline_guard():
    baseline = {"latency_p95": 0.0, "error_rate": 0.0, "cpu_usage": 0.0}
    candidate = {"latency_p95": 1.0, "error_rate": 0.05, "cpu_usage": 0.50}

    res = evaluate_metrics(baseline, candidate)
    assert res["decision"] == "reject"
    assert res["score"] == 0.0
    assert res["confidence"] == 0.0
