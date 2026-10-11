# LabDoctor: Autonomous Google Cloud Lab Verification & Healing Agent

[![Google Cloud](https://img.shields.io/badge/Google_Cloud-Gemini_%7C_Vertex_AI-4285F4?logo=google-cloud)](https://cloud.google.com)
[![Protocol](https://img.shields.io/badge/Tools-Model_Context_Protocol_(MCP)-0052CC)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

**LabDoctor** is an agentic AI solution engineered for **Google Cloud Learning Services**. It autonomously audits, tests, diagnoses, and self-heals broken hands-on labs and codelabs caused by API deprecations, SDK flag changes, and IAM drift.

---

## 🎯 Target Role & Value Proposition
Designed specifically for the **Senior AI Solution Builder (Cloud Learning Services)** role at Google:
* **Workflow Automation**: Replaces manual lab regression testing across thousands of Cloud Skills Boost & Codelab modules.
* **Tool Augmentation via MCP**: Uses Model Context Protocol tool calling to interact with sandboxed GCP environments (`gcloud`, `terraform`, audit logs).
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
    MCP Sandbox Tool ──► Command Execution (gcloud, terraform, bash)
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

### 1. Run the Verification Pipeline
```bash
python3 labdoctor/main.py
```

### 2. Output Highlights
1. **Parses the sample broken lab** (`sample_labs/broken_cloud_run_lab.md`).
2. **Executes steps via MCP sandbox harness**.
3. **Catches real-world deprecations**:
   - `gcloud secrets create --replication-policy=automatic` (deprecated flag).
   - `gcloud run deploy --platform=managed` (obsolete flag).
4. **Auto-heals the commands** and re-runs them in the sandbox.
5. **Generates a ready-to-merge PR description** and writes `healed_cloud_run_lab.md`.
6. **Emits BigQuery telemetry** tracking reliability and ~3.2 engineering hours saved.

---

## 📂 Project Structure
- [`main.py`](file:///Users/jayungerland/gs-os/labdoctor/main.py): Pipeline execution and CLI demo.
- [`src/parser/lab_parser.py`](file:///Users/jayungerland/gs-os/labdoctor/src/parser/lab_parser.py): Markdown AST step and command extractor.
- [`src/mcp_tools/gcp_sandbox_server.py`](file:///Users/jayungerland/gs-os/labdoctor/src/mcp_tools/gcp_sandbox_server.py): MCP tool interfaces for shell execution and GCP doc lookup.
- [`src/agent/orchestrator.py`](file:///Users/jayungerland/gs-os/labdoctor/src/agent/orchestrator.py): Verification and self-healing loop.
- [`src/reporter/pr_generator.py`](file:///Users/jayungerland/gs-os/labdoctor/src/reporter/pr_generator.py): Human-in-the-loop PR description & markdown patch generator.
- [`src/reporter/metrics.py`](file:///Users/jayungerland/gs-os/labdoctor/src/reporter/metrics.py): BigQuery operational telemetry exporter.
