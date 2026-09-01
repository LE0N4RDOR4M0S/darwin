"""
conftest.py — configura sys.path para que os testes unitários possam importar
módulos dos serviços (detector, generator, evaluator, orchestrator) diretamente,
replicando o ambiente de execução dos containers Docker.
"""
import sys
import os

# Adiciona cada pasta de serviço ao sys.path para permitir imports diretos
_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for svc in ["detector", "generator", "evaluator", "orchestrator"]:
    svc_path = os.path.join(_base, svc)
    if svc_path not in sys.path:
        sys.path.insert(0, svc_path)
