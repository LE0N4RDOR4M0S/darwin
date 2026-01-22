from datetime import datetime

def build_report(result: dict) -> dict:
    """
    Gera um relatório final padronizado e auditável.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "decision": result["decision"],
            "score": result["score"]
        },
        "details": {
            "delta_latency(%)": result["delta_latency(%)"],
            "delta_error(%)": result["delta_error(%)"],
            "delta_cpu(%)": result["delta_cpu(%)"]
        },
        "metadata": {
            "baseline": result["baseline"],
            "candidate": result["candidate"]
        }
    }
