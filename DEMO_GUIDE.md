# QFD Permit to Light Fire — Agentic AI Prototype
## Demonstration and Evaluation Guide

**Context:** UNSW Online — AI Fluency, *Assessment 2: Applied AI Analysis — Agent Report*  
**Live prototype:** https://qfd-permit-agentic-demo.streamlit.app/  
**Source code:** https://github.com/raulmendezpat/qfd-permit-agentic-demo

> **Educational simulation only.** This is not an official Queensland Fire Department (QFD) application. All people, locations, permit records and restriction responses shown in the demo are synthetic. Do not use it to make real permit or fire-safety decisions.

## 1. Purpose

This prototype demonstrates selected capabilities from the proposed agentic Permit to Light Fire solution: digital application intake, simulated retrieval of GIS/OMS information, restriction checks, AI-assisted draft assessments, workflow coordination, human approval gates and traceable actions.

It uses **Python, Streamlit and OpenAI Agents SDK**. There are **no connections to operational QFD systems**.

## 2. Architecture at a glance

| Component | Demonstrated responsibility |
|---|---|
| Orchestrator | Coordinates the case workflow; the optional LLM orchestrator calls specialist review tools. |
| Intake & Guidance | Checks application completeness and identifies missing information. |
| Property & Compliance | Consults simulated GIS, OMS and restriction records and identifies evidence gaps or conflicts. |
| Communications & Integration | Creates an optional, unsent LLM message after simulated approval and performs a separate mock downstream update. |
| Fire Warden / Chief Fire Warden (simulated) | Performs the explicit approve/reject action; no LLM can authorise the permit. |

The deterministic workflow is always available. The **optional live LLM assessment** invokes `intake_review` and `property_review` tools and produces an **advisory draft only**. The displayed SDK execution events are evidence of orchestration/tool calls, not evidence of production system integration.

## 3. Recommended assessment walkthrough

**Before starting:** Open the live prototype in a browser. Choose **Clear current case** between test scenarios. Live LLM calls may be unavailable when disabled by the owner or when the demo quota has been reached; all deterministic tests can still be completed.

### Test A — Standard application

1. In **Demonstration controls**, select **Standard application**.
2. In **1 · Application & agent run**, leave the synthetic application fields as loaded.
3. Click **Run orchestrator and specialist agents**.
4. Review the completeness check, synthetic GIS/OMS results, mock restriction response and the case status awaiting Fire Warden review.
5. If live AI is enabled, click **Run real LLM agents (read-only)**. Review the **LLM draft recommendation** and, in **3 · Evidence & audit trail**, the **Real LLM agent/tool events**.
6. In **2 · Human review & integration**, select a simulated authorised role and click **Approve (human action)**.
7. Click **Run mock downstream integration** (with failure simulation off) and inspect the audit log.

**Expected:** The automated workflow prepares a case for review. No permit is approved or downstream update simulated until the explicit human action. LLM outputs remain advisory.

### Test B — Missing information

1. Clear the case and select **Missing information**.
2. Run the deterministic workflow.
3. Review the missing fields and blocked progression.

**Expected:** The case requires clarification; it must not silently proceed to approval. The LLM assessment is optional and is not required to demonstrate this control.

### Test C — Restriction / conflict

1. Clear the case and select **Restriction / conflict**.
2. Run the deterministic workflow.
3. Inspect the simulated conflicting restriction information and escalation result.

**Expected:** The workflow identifies unresolved or conflicting synthetic evidence and escalates rather than automatically approving. **Unavailable official evidence is a limitation, not itself proof of a data conflict.**

### Test D — Integration failure and auditability

1. Clear the case; run **Standard application** and record a simulated human approval.
2. Select **Simulate ESCAD/OMS integration failure**.
3. Click **Run mock downstream integration**.
4. Open **3 · Evidence & audit trail** and click **Download case and audit JSON**.

**Expected:** The failure is logged without claiming a successful update. The export includes case state and audit events from the current browser session.

### Optional Test E — Communications drafting

After a simulated human approval, click **Draft stakeholder message with LLM** if live AI is enabled and quota remains. **Expected:** An unsent message draft; it does not notify recipients or update ESCAD/OMS.

## 4. What to look for

- **Agent coordination/tool use:** `AGENT_START`, `TOOL_START`, `TOOL_END` and `AGENT_END` in the SDK lifecycle table (where live LLM execution succeeds).
- **Human oversight:** `REQUEST_APPROVAL` before `HUMAN_DECISION` in the case audit trail.
- **Separation of concerns:** `LLM_ADVISORY_ONLY` and `LLM_DRAFT_ONLY` cannot update authoritative permit state.
- **Safety under uncertainty:** Missing or conflicting synthetic data blocks or escalates a case; the assessment does not invent official clearances.
- **Traceability:** Events identify actor, action, details and timestamp; the case can be exported to JSON.

## 5. Scope, limitations and evaluation integrity

This prototype demonstrates **technical workflow feasibility**, not operational fitness. GIS, OMS, ESCAD, officer identities and restrictions are simulated; no authoritative QFD policies or live restrictions are retrieved. The selected Fire Warden role is a demo control, **not real user authentication or role-based authorisation**. Session state and logs are not a durable production case-management record. LLM outputs may be imperfect and require verification. There is no validated fire-risk model, production IAM, cross-system transaction handling or completed security assessment.

The live AI capability may be switched off to protect API costs. Session and instance quotas are **best-effort**, not absolute spending caps. If disabled, deterministic scenarios still demonstrate case handling, escalation, approval gating and audit events.

## 6. Suggested evidence for an assessment submission

Capture (a) a completed standard application and its draft assessment; (b) the LLM SDK agent/tool event table; (c) a simulated human approval followed by downstream processing; and (d) an incomplete or conflicting case with its audit history. Do not include API keys or real personal/operational information in screenshots or exports.

**Key principle:** AI supports retrieval, coordination and drafting; authorised humans remain accountable for consequential permit decisions.
