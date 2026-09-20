# Maestro Agentic: Testing Strategy

This document outlines the automated testing framework for Maestro. We use a multi-tiered approach to ensure reliability, from low-level tool logic to high-level agent orchestration.

---

## 🏗 Testing Tiers

### 1. Unit Tests (Tools)

- **Goal:** Verify that individual tool functions (CSV parsing, math, data processing) work correctly.
- **Location:** `tests/test_finance_tools.py`, `tests/test_workout_tools.py`
- **Mocking:** External APIs (Wikipedia, Finance APIs) are mocked to ensure tests run fast and offline.

### 2. Integration Tests (Agent Flows)

- **Goal:** Verify that the `Agent` and `Runner` logic correctly handles events and tool calls.
- **Location:** `tests/test_agent_flow.py`
- **Mocking:** The LLM backend is mocked to verify the surrounding infrastructure without burning tokens.

### 3. Model Evals (Evaluation)

- **Goal:** Use LLMs to judge the quality of other LLMs. Measure accuracy, tone, and adherence to instructions.
- **Running Evals:**
  - Create a "Golden Dataset" (Input vs. Expected Output).
  - Use the `google-adk` built-in evaluation capabilities or a script to run queries and compare results.

---

## 🚀 How to Run Tests

### Prerequisite: Install dependencies

```bash
uv pip install pytest pytest-mock pytest-asyncio
```

### Run all tests

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
./.venv/bin/python -m pytest tests/
```

### Run specific test files

```bash
./.venv/bin/python -m pytest tests/test_finance_tools.py
```

---

## 📈 Future Roadmap for Testing

1. **End-to-End (E2E) Browser Tests:** Use Playwright to test the `web_ui` interaction with the backend.
2. **Deterministic Routing Tests:** Ensure the Orchestrator always routes "workout" queries to the Workout Agent.
3. **CI/CD Integration:** Automatically run `pytest` in the Jenkins pipeline before every deployment.
4. **Safety Evals:** Test the system against adversarial prompts to ensure safety guardrails are working.

---

_Created on: January 6, 2026_
