# 👔 AutoPO Draft Master 2.0 (SSOT Specs)
========================================================================
Andrej Karpathy 72-Line Specification. Do not compress or expand.

## 🎯 1. Core Architecture (Single Source of Truth)
- 슬로건: Diverse Quotes, One Perfect PO.
- 목적: Excel(가로형) & PDF(세로형) 비정형 견적서의 지능형 표준 발주서 변환 엔진.
- 스택: Flask / Pandas / openpyxl / pdfplumber / SQLite3.

## 🗂 2. Directory Access Control Matrix
| Directory / Path | Allowed Agents | Constraints & Rules |
| :--- | :--- | :--- |
| `app_main.py` | Developer 1 (클코) | Core Flask logic & Excel Openpyxl writer only. |
| `pdf_processor.py` | Developer 2 (Opus) | pdfplumber based non-structured parser only. |
| `web/` | Designer | CSS, JS, HTML interface rendering only. |
| `qc_validation.py`| QC Agent | Input-output zero-defect validator only. |
| `agents/` | PM (박부장) | Agent rules, personas and handoff documents. |
| `docs/timeline/` | All (Via PM Sync) | Rule 1 Timeline records (Must be updated). |

## 🛡 3. 6-Harness Engineering Commandments
1. **Scope Isolation**: Modify only target files assigned to your agent role.
2. **Zero-Speculation**: Over-engineering is strictly banned (Always follow YAGNI).
3. **Dependency Lock**: Never install new packages without explicit PM approval.
4. **Strict Compliance**: Follow existing codebase architecture & code conventions.
5. **No Hallucination**: Verify actual file functions before invoking code interfaces.
6. **Git-Timeline Sync**: Prefix every commit message with the timeline entry ID.

## 🤝 4. Multi-Agent Task Delegation Protocol
- **Trigger**: USER request analysis -> PM maps requirements to Parallel R&R.
- **Protocol**: PM issues delegation using `agents/task_delegation_template.md`.
- **Harness Enforcement**: Developer 1, Developer 2, Designer, QC run in parallel.
- **Merge Gate**: QC validation pass -> PM signs off -> Timeline & Git sync.

## 🌐 5. Deployment & Runtime Environment
- Live Server: https://aipo.onrender.com/ (Fully managed by Render Free Tier)
- Keep-Alive Monitor: Cloud UptimeRobot engine polling at 5-minute intervals.
- Local Daemon Policy: Absolutely NO local background daemons are permitted.

## ⚙️ 6. System Execution Commands
- Server Launch: `python web/app.py` or Flask bridge router startup.
- DB Initialization: `python init_db.py` to rebuild settings.db.
- Core QC Check: `python qc_validation.py` for standard stress tests.

## 📂 7. Workspace Architecture Map
- `workspace/`: Active user upload directory (Temporary inputs).
- `sample/`: Standard enterprise Excel and PDF sample quotes.
- `template/`: Standard corporate purchase order template target sheet.
- `logs/`: Production and development diagnostic log repository.

## 🧠 8. Global Absolute Rules (System Guardrails)
- Rule 1: Autonomous timeline logs update required on every session turn.
- Rule 2: Strictly follow Caveman Mode communication style (UgaUga!).
- Rule 3: Andrei Karpathy 72-line MD README SSOT standard compliance.
- Rule 4: Inspection simplification logic for single timeline summary.
- Rule 5: Korean final result and in-progress report headers mandate.

## 📝 9. Active Directory R&R Target Files Map
- Developer 1: `app_main.py` & `init_db.py` (Flask backend, excel parsing)
- Developer 2: `pdf_processor.py` (pdf parsing, layout packer)
- Designer: `web/templates/` & `web/static/` (HTML, CSS, static visual assets)
- QC Agent: `qc_validation.py` & `error/` (integrity tests, error reports)
- PM: `agents/` & `docs/timeline/` (R&R directives, history index log)

## 🚀 10. Core Technical Milestones
- Phase 1: Hybrid parsing engine pipeline stability (Completed).
- Phase 2: Render Free Tier stable cloud deployment (Completed).
- Phase 3: Multi-agent parallel task orchestration (Active).

========================================================================
*Compilation Hash: 4abd9fb0a98b2cd721b0337c7642af589ce1a75f*
*Environment: Python 3.9+ | OS: macOS/Linux | System Authorized: 2026-05-21 by Director Park.*
