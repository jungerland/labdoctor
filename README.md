# LabDoctor: Autonomous Google Cloud Lab Verification & Healing Agent

[![Google Cloud](https://img.shields.io/badge/Google_Cloud-Gemini_%7C_Vertex_AI-4285F4?logo=google-cloud)](https://cloud.google.com)
[![Protocol](https://img.shields.io/badge/Tools-Model_Context_Protocol_(MCP)-0052CC)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

**LabDoctor** is an agentic AI solution engineered for **Google Cloud Learning Services**. It autonomously audits, tests, diagnoses, and self-heals broken hands-on labs and codelabs caused by API deprecations, SDK flag changes, and IAM drift.

**Status: prototype.** The MCP sandbox runs in simulated mode; live GCP project execution is next.

---

## 🎯 Target Role & Value Proposition
Designed specifically for the **Senior AI Solution Builder (Cloud Learning Services)** role at Google:
* **Workflow Automation**: Replaces manual lab regression testing across thousands of Cloud Skills Boost & Codelab modules.
* **Tool Augmentation via MCP**: Uses Model Context Protocol tool calling to interact with sandboxed GCP environments (`gcloud`, bash, audit logs; Terraform planned).
* **Self-Healing & HITL Governance**: Diagnoses root causes, checks updated GCP documentation, verifies fixes in an isolated sandbox, and submits clean GitHub PRs for human curriculum designers.
* **Operational Telemetry & ROI**: Emits BigQuery-ready telemetry modeling engineering hours saved and API drift trends.

---

## 🏗️ Architecture

```
Codelab Markdown / Jupyter Notebook
               │
               ▼
   [1. Markdown AST Lab Parser] ── Extracts commands, expected outputs, and steps
               │
               ▼
   [2. LabDoctor Agent Orchestrator]
         │                     ▲
         ▼                     │
    MCP Sandbox Tool ──► Command Execution (gcloud, bash; terraform planned)
         │                     │
         ▼ (Exit Code != 0)    │
   [3. Diagnostic & Auto-Healer]
         │ (Consults Documentation / Deprecation Knowledge)
         ▼
     Sandbox Retest & Self-Verification
               │
               ▼
   [4. Human-in-the-Loop PR & BigQuery Telemetry]
         ├── GitHub Pull Request with before/after diff
         └── BigQuery telemetry row (reliability score, hours saved)
```

---

## 🚀 Quickstart

### 1. Installation & Setup
```bash
# Clone the repository
git clone https://github.com/jungerland/labdoctor.git
cd labdoctor

# Install dependencies
pip install -e .
```

### 2. Run the Verification Pipeline
```bash
# Run verification on complex sample lab
python3 main.py

# Or run verification on Cloud Run sample lab
python3 main.py cloud_run
```

### 3. Manage Issue Queue & Self-Healing Playbook
```bash
# Inspect unresolved escalation queue
python3 -m src.queue.cli

# View or manage self-healing playbook rules
python3 -m src.playbook.cli
```

### 4. Run Quantitative Agent Evaluation Suite (Rubric & Metrics)
```bash
# Execute the agentic verification benchmark suite & scorecard
python3 -m src.evals.cli

# Run automated tests
pytest tests/ -v
```

### 5. Output Highlights
1. **Parses the sample broken lab** (`sample_labs/broken_cloud_run_lab.md` or `sample_labs/complex_broken_lab.md`).
2. **Executes steps via MCP sandbox harness**.
3. **Catches real-world deprecations**:
   - `gcloud secrets create --replication-policy=automatic` (deprecated flag).
   - `gcloud run deploy --platform=managed` (obsolete flag).
4. **Auto-heals the commands** and re-runs them in the sandbox.
5. **Generates a ready-to-merge PR description** and writes `healed_cloud_run_lab.md`.
6. **Emits BigQuery telemetry** tracking reliability and an estimated ~3.2 engineering hours saved (assumed weights: 0.1 hr per passing step, 1.5 per healed step, 0.5 per queued step; see `src/agent/orchestrator.py`).
7. **Evaluates against ground truth benchmarks**: Measures Fix Pass Rate (FPR), Negative Control Integrity (0% false positives), and Escalation Precision.

---

## 📂 Project Structure
- [`main.py`](main.py): Pipeline execution and CLI demo.
- [`src/evals/`](src/evals/): Quantitative evaluation runner (`evaluator.py`, `cli.py`, `schema.py`).
- [`evals/benchmarks/`](evals/benchmarks/): Golden benchmark lab suite (CLI flags, negative controls, missing assets, arch forks).
- [`src/parser/lab_parser.py`](src/parser/lab_parser.py): Markdown AST step and command extractor.
- [`src/mcp_tools/gcp_sandbox_server.py`](src/mcp_tools/gcp_sandbox_server.py): MCP tool interfaces for shell execution and GCP doc lookup.
- [`src/agent/orchestrator.py`](src/agent/orchestrator.py): Verification and self-healing loop.
- [`src/playbook/engine.py`](src/playbook/engine.py): Rule evaluation and self-healing playbook engine.
- [`src/queue/issue_queue.py`](src/queue/issue_queue.py): Human-in-the-loop issue queue store.
- [`src/reporter/pr_generator.py`](src/reporter/pr_generator.py): Human-in-the-loop PR description & markdown patch generator.
- [`src/reporter/metrics.py`](src/reporter/metrics.py): BigQuery operational telemetry exporter.
- [`tests/`](tests/): Pytest unit and integration test suite.

