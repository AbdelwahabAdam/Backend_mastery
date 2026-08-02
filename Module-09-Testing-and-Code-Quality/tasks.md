# Tasks

Complete each task with evidence. Functional code alone is not complete without tests, operational signals, documentation, and a recovery plan.

## 1. Test a REST API

**Level:** Beginner

**Objective**  
Write pytest unit/API tests for FastAPI validation and errors.

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
A public endpoint must reject invalid input safely.

## 2. Integration testing

**Level:** Intermediate

**Objective**  
Run PostgreSQL/Redis in Docker and test transactions, cache behavior, and failure cleanup.

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
A release changed persistence behavior.

## 3. Quality gate

**Level:** Advanced

**Objective**  
Add GitHub Actions tests, linting, coverage/mutation risk, artifacts, and flaky-test policy.

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
A team needs trusted PR automation.

## 4. Quality capstone

**Level:** Production

**Objective**  
Improve a service using test pyramid, contracts, load checks, review standards, refactoring, CI gates, metrics, and a regression runbook.

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
A payment API has recurring production regressions.
