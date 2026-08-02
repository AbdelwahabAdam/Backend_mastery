# Tasks

Complete each task with evidence. Functional code alone is not complete without tests, operational signals, documentation, and a recovery plan.

## 1. Dockerize FastAPI

**Level:** Beginner

**Objective**  
Create a small, non-root image with health checks and Compose dependencies.

**Requirements**  
- Define requirements, invariants, APIs/data boundaries, and acceptance checks.
- Provide code/configuration, tests, logs/metrics/traces, diagrams, and an operational note.

**Constraints**  
- Bound resources/timeouts and protect secrets/customer data.
- State assumptions, failure behavior, security, cost, rollback, and ownership.

**Expected Output**  
Repository changes, README, test/CI evidence, diagrams, dashboard/runbook, and a concise trade-off record.

**Hints**  
Start with one thin vertical slice and a deterministic baseline; introduce complexity only after measuring the risk it addresses.

**Stretch Goals**  
Add load/fault testing, canary rollout, restore drill, security review, cost forecast, and a recorded mock explanation.

**Evaluation Checklist**  
- [ ] Correctness and failure handling are demonstrated.
- [ ] Automation and telemetry are actionable.
- [ ] Security, cost, and rollback are explicit.
- [ ] Documentation supports an independent reviewer.

**Real-world Context**  
Developers need reproducible local startup.

## 2. CI/CD pipeline

**Level:** Intermediate

**Objective**  
Build/test/scan/publish a traceable container in GitHub Actions.

**Requirements**  
- Define requirements, invariants, APIs/data boundaries, and acceptance checks.
- Provide code/configuration, tests, logs/metrics/traces, diagrams, and an operational note.

**Constraints**  
- Bound resources/timeouts and protect secrets/customer data.
- State assumptions, failure behavior, security, cost, rollback, and ownership.

**Expected Output**  
Repository changes, README, test/CI evidence, diagrams, dashboard/runbook, and a concise trade-off record.

**Hints**  
Start with one thin vertical slice and a deterministic baseline; introduce complexity only after measuring the risk it addresses.

**Stretch Goals**  
Add load/fault testing, canary rollout, restore drill, security review, cost forecast, and a recorded mock explanation.

**Evaluation Checklist**  
- [ ] Correctness and failure handling are demonstrated.
- [ ] Automation and telemetry are actionable.
- [ ] Security, cost, and rollback are explicit.
- [ ] Documentation supports an independent reviewer.

**Real-world Context**  
Every merge must be validated consistently.

## 3. AWS service deployment

**Level:** Advanced

**Objective**  
Design EC2/ECS, ALB, RDS, Redis, S3, IAM, VPC, CloudWatch, and rollback path.

**Requirements**  
- Define requirements, invariants, APIs/data boundaries, and acceptance checks.
- Provide code/configuration, tests, logs/metrics/traces, diagrams, and an operational note.

**Constraints**  
- Bound resources/timeouts and protect secrets/customer data.
- State assumptions, failure behavior, security, cost, rollback, and ownership.

**Expected Output**  
Repository changes, README, test/CI evidence, diagrams, dashboard/runbook, and a concise trade-off record.

**Hints**  
Start with one thin vertical slice and a deterministic baseline; introduce complexity only after measuring the risk it addresses.

**Stretch Goals**  
Add load/fault testing, canary rollout, restore drill, security review, cost forecast, and a recorded mock explanation.

**Evaluation Checklist**  
- [ ] Correctness and failure handling are demonstrated.
- [ ] Automation and telemetry are actionable.
- [ ] Security, cost, and rollback are explicit.
- [ ] Documentation supports an independent reviewer.

**Real-world Context**  
A backend team is moving from one VM to managed AWS services.

## 4. DevOps capstone

**Level:** Production

**Objective**  
Deliver a Dockerized FastAPI service with CI/CD, AWS deployment plan, private RDS/Redis, S3 uploads, ECR/ECS/ALB, CloudWatch, benchmark, budgets, Multi-AZ/DR, and progressive rollback.

**Requirements**  
- Define requirements, invariants, APIs/data boundaries, and acceptance checks.
- Provide code/configuration, tests, logs/metrics/traces, diagrams, and an operational note.

**Constraints**  
- Bound resources/timeouts and protect secrets/customer data.
- State assumptions, failure behavior, security, cost, rollback, and ownership.

**Expected Output**  
Repository changes, README, test/CI evidence, diagrams, dashboard/runbook, and a concise trade-off record.

**Hints**  
Start with one thin vertical slice and a deterministic baseline; introduce complexity only after measuring the risk it addresses.

**Stretch Goals**  
Add load/fault testing, canary rollout, restore drill, security review, cost forecast, and a recorded mock explanation.

**Evaluation Checklist**  
- [ ] Correctness and failure handling are demonstrated.
- [ ] Automation and telemetry are actionable.
- [ ] Security, cost, and rollback are explicit.
- [ ] Documentation supports an independent reviewer.

**Real-world Context**  
This is reviewed by backend, platform, security, and SRE teams.
