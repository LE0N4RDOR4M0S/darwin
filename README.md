# 🧬 Código Vivo — Sistema Auto-otimizador de Software

> “Um sistema que observa, aprende e se reescreve para evoluir.”

---

## 🧠 Contexto e Motivação

O **Código Vivo** é uma proposta de arquitetura experimental que une engenharia de software, sistemas distribuídos e aprendizado automatizado.  
A ideia central: permitir que um software **monitore seu próprio desempenho, gere alterações de código e avalie essas alterações de forma autônoma**, aplicando somente mudanças que comprovadamente melhorem a performance.

O projeto parte do princípio de que **a evolução de sistemas pode ser automatizada**, semelhante à evolução biológica, por meio de pequenas mutações e seleção das versões mais eficientes.

Ciclo contínuo:
1. Observação (telemetria) → coleta de métricas.
2. Geração (mutação) → criação de variações de código.
3. Avaliação (seleção) → comparação e decisão.
4. Evolução (deploy) → adoção da versão melhorada.

---

## 🏗️ Arquitetura Geral

Arquitetura composta por módulos desacoplados, conectados via Docker e APIs REST.

```text
Runtime App (Spring Boot)
    ↓ Telemetria
Prometheus → Detector → Generator
              ↓
          Sandbox Runner (GitLab CI)
              ↓
           Evaluator → Orchestrator → Canary Deployer
              ↑
              Auditor / MinIO
```

Cada componente desempenha um papel autônomo dentro do ciclo de evolução.

### ⚙️ Componentes e Justificativas Técnicas

| Componente     | Tecnologia                                | Justificativa |
|----------------|-------------------------------------------|---------------|
| Runtime App    | Spring Boot (Java)                        | Simula um sistema real de produção com endpoints instrumentados via Micrometer |
| Telemetria     | Micrometer + Prometheus + Grafana         | Observabilidade padronizada e escalável |
| Detector       | Python (FastAPI + Prometheus API)         | Detecta hotspots com consultas PromQL |
| Generator      | Python + JavaParser + GitPython           | Gera variações de código (patches) via AST/heurísticas |
| Sandbox Runner | GitLab CI/CD + Docker                     | Testa variações em ambiente isolado e reproduzível |
| Evaluator      | FastAPI + Pandas/Numpy                    | Avalia desempenho e calcula score |
| Orchestrator   | FastAPI + Celery                          | Coordena o ciclo completo e decisões de aprovação |
| Storage        | MinIO                                     | Guarda logs, relatórios e snapshots de builds/testes |
| Observabilidade| Grafana + Jaeger + Loki                   | Dashboards, tracing e logs centralizados |

Todos os serviços são containerizados e conectados pela rede `codigo-vivo-net`, garantindo isolamento e escalabilidade modular.

---

## 🧩 Estrutura de Diretórios

A estrutura do repositório e a função de cada parte:

```text
codigo-vivo/
│
├── .env.example
├── docker-compose.yml
├── README.md
│
├── docs/
│   ├── arquitetura.md
│   ├── fluxo_dados.png
│   ├── design_decisions.md
│   └── roadmap.md
│
├── infra/
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   ├── jaeger/
│   │   └── config.yaml
│   ├── minio/
│   │   ├── Dockerfile
│   │   └── init.sh
│   └── k8s/
│
├── secrets/                    # NÃO versionado (.gitignore)
│   ├── id_rsa
│   ├── gitlab_token.txt
│   └── config.json
│
├── runtime-app/
│   ├── src/main/java/com/example/codigovivo/
│   │   ├── CodigoVivoApplication.java
│   │   ├── controller/SampleController.java
│   │   └── config/HttpClientConfig.java
│   ├── pom.xml
│   ├── Dockerfile
│   └── README.md
│
├── telemetry-agent/
│   ├── src/telemetry_collector.py
│   ├── exporters/
│   │   ├── prometheus_exporter.py
│   │   ├── jaeger_exporter.py
│   │   └── loki_exporter.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── detector/
│   ├── detector.py
│   ├── queries/
│   │   ├── latency_query.promql
│   │   ├── error_query.promql
│   │   └── cpu_usage.promql
│   ├── Dockerfile
│   └── requirements.txt
│
├── generator/
│   ├── generator.py
│   ├── heuristics/
│   │   ├── timeout_rule.py
│   │   ├── pool_size_rule.py
│   │   └── caching_rule.py
│   ├── models/tinyllama_adapter.py
│   ├── utils/
│   │   ├── git_helper.py
│   │   ├── ast_parser.py
│   │   └── patch_writer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── evaluator/
│   ├── evaluator.py
│   ├── metrics/
│   │   ├── baseline.json
│   │   ├── candidate.json
│   │   └── scoring.py
│   ├── utils/report_builder.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── orchestrator/
│   ├── orchestrator.py
│   ├── utils/
│   │   ├── api_client.py
│   │   ├── job_scheduler.py
│   │   └── logger.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── tests/
    ├── integration/
    ├── unit/
    ├── load/
    ├── sandbox/
    │   ├── Dockerfile
    │   └── sandbox_runner.py
    └── data/
     ├── baseline.json
     └── candidate.json
```

---

## 🔐 Segurança e Segredos

Nenhum segredo deve ser commitado. O arquivo `.env` local contém apenas variáveis genéricas. Tokens, chaves e credenciais são montados via Docker secrets (`/run/secrets/...`) ou GitLab CI/CD Variables.

---

## 🧠 Princípios de Design

- Desacoplamento total — módulos independentes comunicando-se via APIs.
- Auditabilidade total — todo patch, decisão e rollback são registrados.
- Evolução incremental — mudanças pequenas, reversíveis e testáveis.
- Paridade com produção — sandbox reflete o ambiente real.
- Segurança por padrão — sem alteração de módulos críticos sem revisão humana.

---

## 🚀 Como executar o projeto

1. Crie o arquivo `.env` a partir do exemplo:
```bash
cp .env.example .env
```

2. Suba os serviços:
```bash
docker compose --env-file .env up -d --build
```

3. Acesse os módulos:
- App (Spring Boot): http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Generator API: http://localhost:5000/docs
- Evaluator API: http://localhost:5001/docs
- Orchestrator API: http://localhost:5002/docs

---

## 🧬 Fluxo de Vida do Código Vivo

Runtime → expõe métricas via Micrometer → Prometheus/Detector identifica hotspot → Generator cria patch candidato → Sandbox Runner (CI) executa testes e coleta métricas → Evaluator calcula score → Orchestrator decide aplicar ou reverter → MinIO + Auditor registra histórico.

---

## 🧾 Licença

Projeto experimental e acadêmico sob licença MIT. Uso em produção exige práticas de segurança e ética em automação de software.

---
