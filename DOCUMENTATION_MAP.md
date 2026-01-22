# 🗺️ Mapa de Documentação — Código Vivo

Bem-vindo! Use este mapa para navegar pela documentação do projeto.

---

## 🎯 Começar Aqui

```
┌─────────────────────────────────────────────┐
│  NOVO NO PROJETO?                           │
│  ↓                                           │
│  Leia: README.md (5 min)                    │
│  ↓                                           │
│  Quero começar rápido?                      │
│  ├─ SIM → QUICKSTART.md                    │
│  └─ NÃO → Leia completo abaixo             │
└─────────────────────────────────────────────┘
```

---

## 📚 Documentação Estruturada

### 🟦 Nível 1: Visão Geral (20 minutos)

| Documento | Propósito | Público |
|-----------|-----------|---------|
| [README.md](README.md) | Visão geral do projeto | Todos |
| [QUICKSTART.md](QUICKSTART.md) | Executar em 30 segundos | Todos |
| [docs/arquitetura.md](docs/arquitetura.md) | Arquitetura e componentes | Engenheiros |

**Pronto para começar?** → `docker-compose up -d`

---

### 🟩 Nível 2: Entender Melhor (1 hora)

| Documento | Propósito | Público |
|-----------|-----------|---------|
| [docs/design_decisions.md](docs/design_decisions.md) | Decisões de design (12 ADRs) | Arquitetos, Leads |
| [docs/fluxo_dados.md](docs/fluxo_dados.md) | Fluxo de dados completo | Engenheiros |
| [ROADMAP.md](ROADMAP.md) | Plano futuro (Fase 2-3) | Gestores, Engenheiros |

**Quer contribuir?** → Leia seção abaixo

---

### 🟨 Nível 3: Desenvolvimento (2+ horas)

| Documento | Propósito | Público |
|-----------|-----------|---------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Setup dev local | Engenheiros |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como contribuir | Contribuidores |
| [detector/README.md](detector/README.md) | Módulo Detector | Engenheiros Python |
| [generator/README.md](generator/README.md) | Módulo Generator | Engenheiros Python |
| [evaluator/README.md](evaluator/README.md) | Módulo Evaluator | Engenheiros Python |
| [orchestrator/README.md](orchestrator/README.md) | Módulo Orchestrator | Engenheiros Python |
| [telemetry-agent/README.md](telemetry-agent/README.md) | Telemetry Agent | Engenheiros Python |

**Pronto para desenvolvimento?** → `source venv/bin/activate && pytest tests/`

---

### 🟥 Nível 4: Implementação Completa (3+ horas)

| Documento | Propósito | Público |
|-----------|-----------|---------|
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumo de tudo | Técnicos, PMs |
| [COMPLETION_REPORT.md](COMPLETION_REPORT.md) | Status e estatísticas | Gestores, Leads |

---

## 🎯 Navegação por Interesse

### 👨‍💼 Sou Product Manager

1. Leia [README.md](README.md) — Entenda a proposta
2. Veja [ROADMAP.md](ROADMAP.md) — Plano futuro
3. Abra [docs/arquitetura.md](docs/arquitetura.md) — Entenda escopo
4. Confira [COMPLETION_REPORT.md](COMPLETION_REPORT.md) — Status atual

**Tempo**: 30 minutos

---

### 👨‍💻 Sou Engenheiro Backend/Frontend

1. Leia [README.md](README.md) — Contexto
2. Siga [QUICKSTART.md](QUICKSTART.md) — Setup
3. Abra [DEVELOPMENT.md](DEVELOPMENT.md) — Desenvolvimento local
4. Escolha um módulo e leia seu README
5. Vire [CONTRIBUTING.md](CONTRIBUTING.md) — Comece contribuindo

**Tempo**: 2 horas

---

### 👨‍🔧 Sou DevOps/SRE

1. Leia [docs/arquitetura.md](docs/arquitetura.md) — Componentes
2. Veja `docker-compose.yml` — Serviços
3. Verifique `infra/k8s/` — Kubernetes
4. Revise `.gitlab-ci.yml` — CI/CD
5. Configure `.env.example` — Variáveis

**Tempo**: 1 hora

---

### 🎓 Sou Estudante/Aprendiz

1. Comece [README.md](README.md) — Entenda o problema
2. Execute [QUICKSTART.md](QUICKSTART.md) — Veja funcionando
3. Leia [docs/fluxo_dados.md](docs/fluxo_dados.md) — Entenda o fluxo
4. Estude [docs/design_decisions.md](docs/design_decisions.md) — Aprenda decisões
5. Faça [DEVELOPMENT.md](DEVELOPMENT.md) — Desenvolva localmente

**Tempo**: 3-4 horas

---

### 🤝 Quero Contribuir

1. Leia [CONTRIBUTING.md](CONTRIBUTING.md) — Guidelines
2. Revise [ROADMAP.md](ROADMAP.md) — Escolha uma issue
3. Setup local com [DEVELOPMENT.md](DEVELOPMENT.md)
4. Estude o módulo relevante
5. Abra um Pull Request!

**Tempo**: 1-2 horas de setup + desenvolvimento

---

### 🚀 Quero Fazer Deploy

**Para Desenvolvimento (Local)**:
1. [QUICKSTART.md](QUICKSTART.md) — Docker Compose
2. `.env.example` — Configure variáveis
3. `docker-compose up -d` — Start

**Para Produção (Kubernetes)**:
1. [QUICKSTART.md](QUICKSTART.md) — Seção Kubernetes
2. `infra/k8s/all-in-one.yaml` — Manifests
3. `kubectl apply -f` — Deploy

**Para CI/CD (GitLab)**:
1. `.gitlab-ci.yml` — Review pipeline
2. Configure secrets em GitLab
3. Push para trigger

---

## 📊 Mapa de Leitura Recomendado

```
START
  │
  ├─→ README.md (5 min)
  │     │
  │     ├─→ Quero iniciar rápido?
  │     │   └─→ QUICKSTART.md → docker-compose up
  │     │
  │     └─→ Quero entender mais?
  │         └─→ docs/arquitetura.md → docs/design_decisions.md
  │
  ├─→ Sou Engenheiro?
  │   └─→ DEVELOPMENT.md → Escolha um módulo → Teste
  │
  ├─→ Sou DevOps?
  │   └─→ docker-compose.yml → infra/k8s/ → .gitlab-ci.yml
  │
  ├─→ Quero Contribuir?
  │   └─→ CONTRIBUTING.md → ROADMAP.md → Escolha issue
  │
  └─→ Quero Saber Status?
      └─→ COMPLETION_REPORT.md → IMPLEMENTATION_SUMMARY.md
```

---

## 🔍 Busca Rápida

### Por Tecnologia

**Docker**
- [QUICKSTART.md#Docker](QUICKSTART.md) — Como rodar
- [docker-compose.yml](docker-compose.yml) — Config completa

**Kubernetes**
- [QUICKSTART.md#Kubernetes](QUICKSTART.md) — Como rodar
- [infra/k8s/all-in-one.yaml](infra/k8s/all-in-one.yaml) — Manifests

**Python (FastAPI)**
- [DEVELOPMENT.md#Python](DEVELOPMENT.md) — Setup
- [detector/README.md](detector/README.md) — Exemplo
- [CONTRIBUTING.md#Python](CONTRIBUTING.md) — Padrões

**Java (Spring Boot)**
- [DEVELOPMENT.md#Spring-Boot](DEVELOPMENT.md) — Setup
- [app/README.md](app/README.md) — Aplicação

**GitLab CI/CD**
- [.gitlab-ci.yml](.gitlab-ci.yml) — Pipeline
- [DEVELOPMENT.md#GitLab](DEVELOPMENT.md) — Como funciona

**Observabilidade (Prometheus, Grafana, Jaeger, Loki)**
- [docs/arquitetura.md#Observabilidade](docs/arquitetura.md) — Overview
- [DEVELOPMENT.md#Debugging](DEVELOPMENT.md) — Como debugar

### Por Problema

**"Docker não inicia"**
- [DEVELOPMENT.md#Docker-Issues](DEVELOPMENT.md) → Troubleshooting

**"Porta em uso"**
- [DEVELOPMENT.md#Porta-em-Uso](DEVELOPMENT.md) → Solução

**"Como contribuir?"**
- [CONTRIBUTING.md](CONTRIBUTING.md) → Processo completo

**"Qual é o roadmap?"**
- [ROADMAP.md](ROADMAP.md) → Plano futuro

**"Qual é o status?"**
- [COMPLETION_REPORT.md](COMPLETION_REPORT.md) → Status atual

**"Como fazer deploy?"**
- [QUICKSTART.md#Deploy](QUICKSTART.md) → Instruções

**"Como testar?"**
- [DEVELOPMENT.md#Testes](DEVELOPMENT.md) → Testing guide

---

## 📋 Checklist de Onboarding

Use este checklist para acompanhar seu progresso:

### Fase 1: Entendimento (30 min)
- [ ] Li [README.md](README.md)
- [ ] Vi o sistema rodando com `docker-compose up`
- [ ] Acessei Grafana em localhost:3000
- [ ] Entendi arquitetura básica

### Fase 2: Exploração (1 hora)
- [ ] Explorei todos os endpoints via Swagger
- [ ] Li [docs/arquitetura.md](docs/arquitetura.md)
- [ ] Entendi ciclo de evolução
- [ ] Vi logs em Loki

### Fase 3: Desenvolvimento (2 horas)
- [ ] Setup ambiente local (venv)
- [ ] Rodei testes unitários
- [ ] Li [DEVELOPMENT.md](DEVELOPMENT.md)
- [ ] Entendi estrutura de código

### Fase 4: Contribuição (Ongoing)
- [ ] Li [CONTRIBUTING.md](CONTRIBUTING.md)
- [ ] Escolhi uma issue do [ROADMAP.md](ROADMAP.md)
- [ ] Abri um Pull Request
- [ ] Recebi code review

---

## 🎓 Materiais de Estudo

### Pré-requisitos
- Docker & Docker Compose
- Python 3.10+
- Java 17+
- Git

### Conceitos
- Microserviços
- REST APIs
- Observabilidade (OTEL, Prometheus, Grafana)
- CI/CD Pipelines
- Kubernetes (opcional)

### Tecnologias
- FastAPI (Python)
- Spring Boot (Java)
- GitLab CI/CD
- Docker/Kubernetes
- OpenTelemetry

---

## 💬 Perguntas Frequentes

**P: Por onde começo?**  
R: Leia [README.md](README.md) e depois execute [QUICKSTART.md](QUICKSTART.md)

**P: Qual é o roadmap?**  
R: Veja [ROADMAP.md](ROADMAP.md) para plano futuro

**P: Como contribuo?**  
R: Leia [CONTRIBUTING.md](CONTRIBUTING.md) passo a passo

**P: Qual é o status?**  
R: Veja [COMPLETION_REPORT.md](COMPLETION_REPORT.md)

**P: Como faço deploy?**  
R: Siga [QUICKSTART.md](QUICKSTART.md) seção Deploy

**P: Preciso de ajuda?**  
R: Abra uma Issue ou veja [DEVELOPMENT.md#Troubleshooting](DEVELOPMENT.md)

---

## 🔗 Links Úteis

### Documentação Externa
- [Docker Compose](https://docs.docker.com/compose/)
- [Kubernetes](https://kubernetes.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Spring Boot](https://spring.io/projects/spring-boot)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

### APIs Locais (quando rodando)
- Generator: http://localhost:5002/docs
- Evaluator: http://localhost:5001/docs
- Orchestrator: http://localhost:5003/docs
- Detector: http://localhost:5004/docs
- Spring Boot: http://localhost:8080/actuator

---

**🎉 Bem-vindo ao Código Vivo!**

Escolha sua jornada acima e comece a explorar! 🚀
