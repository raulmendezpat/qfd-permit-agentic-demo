# QFD Permit to Light Fire — Agentic Prototype (synthetic educational demo)

**Live public demo:** https://qfd-permit-agentic-demo.streamlit.app/  
**Evaluator walkthrough:** [DEMO_GUIDE.md](DEMO_GUIDE.md)  
**Source repository:** https://github.com/raulmendezpat/qfd-permit-agentic-demo

This is **not an official Queensland Fire Department application**. All people, land records, districts, restrictions and decisions are fictional. Do not use this app for actual fire permits.

## What it demonstrates

- Applicant form and three preloaded cases: standard, incomplete, and restriction conflict
- Deterministic intake, GIS/OMS mock lookups and mock restriction checks
- Human approval/rejection gate before synthetic downstream updates
- Synthetic integration failure and audit trail (JSON export)
- Optional OpenAI Agents SDK LLM orchestrator with intake and property/compliance specialists; SDK lifecycle event list in the UI
- Optional **unsent** communications draft only after simulated human approval
- Clear distinction between synthetic evidence, actual conflict, unavailable authoritative data and LLM recommendations

**Important limitation:** The LLM recommendations do not own authoritative case state. SDK lifecycle events show agent/tool invocations; they are not evidence of real QFD connectivity or production-grade security. The demo role dropdown is a simulation, not identity authentication. Case/audit is Streamlit session state and disappears when the browser session expires; it is not a production case database.

## Local setup

Recommended: Python 3.12. From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENAI_API_KEY="YOUR_NEW_KEY" # optional; avoid committing or sharing it
python -m streamlit run app.py
```

For better key hygiene use Streamlit secrets. Create a local, **untracked** `.streamlit/secrets.toml` with `OPENAI_API_KEY = "your-secret"`. Never upload that file. No key = deterministic demo continues to work.

## Deploy to Streamlit Community Cloud

1. Create a **new public GitHub repository** such as `qfd-permit-agentic-demo`.
2. Upload `app.py`, `llm_agents.py`, `usage_guard.py`, `requirements.txt`, `.gitignore` and `README.md` at repository root. **Never upload credentials, `.venv`, `.venv-llm` or `secrets.toml`.**
3. Go to https://share.streamlit.io/ → **Create app** → **Yup, I have an app**. Select your GitHub repository, branch `main`, entrypoint `app.py`.
4. In **Advanced settings**, choose **Python 3.12** and enter secrets, for example:

```toml
OPENAI_API_KEY = "YOUR_FRESH_API_KEY"
QFD_LLM_ENABLED = "true"
QFD_GLOBAL_DAILY_LIMIT = "12"
```

5. Deploy. The generated `*.streamlit.app` URL can be opened without login when the app is public. Confirm using a private browsing window.
6. Try all three deterministic scenarios and one live LLM call, then inspect the local SDK lifecycle table. The public demo must be tested after deployment; static compilation alone does not prove runtime success.

## Cost controls and operational cautions

- The UI limits each Streamlit browser session to **one LLM assessment** and **one communications draft**. These counters can be bypassed with a new browser session.
- `usage_guard.py` additionally reserves **12 API calls/day per running Streamlit instance** by default (`QFD_GLOBAL_DAILY_LIMIT`). It counts failed requests. The SQLite state is **ephemeral**, resets on app restart/redeploy, and does not coordinate multiple server instances. **This is not a hard spend limit**.
- Use a **dedicated API project and key** for the demo, configure the lowest suitable project spending alerts/limits in https://platform.openai.com/ and regularly monitor https://platform.openai.com/usage. Platform budgets may be alert-only; don't assume a spending limit is a hard stop.
- For a safer public demonstration, set `QFD_LLM_ENABLED = "false"` in Community Cloud secrets. The deterministic demo still works and no model calls are made. Enable it shortly before your teacher evaluates the demo, then turn it off afterwards.
- There is no login. Other users can access live AI calls while enabled; do not enter real personal/operational data.
- SDK trace export excludes sensitive model/tool inputs and outputs (`trace_include_sensitive_data=False`), but ordinary API model requests still transmit synthetic application data to the model. Keep inputs fictional.
- Revoke any API key accidentally exposed in screenshots/chat/terminal logs and rotate to a fresh dedicated key before public deployment.

## Demonstration guide for evaluators

For a step-by-step English walkthrough with expected results, evidence to inspect and limitations, see **[DEMO_GUIDE.md](DEMO_GUIDE.md)**. Live LLM calls may be temporarily disabled or quota-limited on the public app; the deterministic scenarios remain available.

## Suggested assessment walkthrough

1. Standard application → run deterministic agents → (optional) run LLM assessment → show events / evidence.
2. Human review → simulated Fire Warden approval → create optional unsent draft → simulate downstream update.
3. Missing information → STOP; no human approval available.
4. Restriction/conflict → escalation; show detected conflict vs mere absence of actual official policies.
5. Simulate integration failure → show audit logs and no false success claim.

## Deliberate limitations

No real GIS/OMS/ESCAD integration; no live fire restrictions; no official policies; no production IAM/RBAC, persistence, multi-user quotas, durable queue, or guarantees of model correctness. Decisions require simulated manual Fire Warden actions.
