# Architecture Specification — AI Lead Generation Agent

Source of truth: [`../constitution-leads.md`](../constitution-leads.md) (§3–6, 45, 51–54, 58). This spec describes the target architecture.

## 1. System overview

```
Next.js 16 Frontend ── REST/JSON ──▶ FastAPI API Layer
                                        │
                                     Services (business logic)
                              ┌─────────┼──────────────┐
                          AI Agents  Integrations  Repositories
                          (discovery,  (llm/email/    (leads, campaigns,
                           research,    search/crm)    users, agent runs)
                           qualify,...)      │
                              │              ▼
                              ▼         Database
                         AI Providers
```

## 2. Backend layering (mandatory)

```
Router → Pydantic schema validation → Service → Agent/Integration → Repository → Database
```

| Layer | Location | Responsibility | Must NOT contain |
|---|---|---|---|
| Router | `backend/app/api/v1/` | HTTP methods, auth deps, validation, status codes | Business logic, prompts, raw SQL |
| Schema | `backend/app/schemas/` | Explicit request/response contracts | ORM logic |
| Service | `backend/app/services/` | Business logic (create, qualify, status changes) | HTTP details, prompts |
| Agent | `backend/app/agents/` | AI tasks coordinated by `orchestrator.py` | DB access, HTTP logic |
| Integration | `backend/app/integrations/` | Vendor adapters (llm, email, search, crm) | Business logic |
| Repository | `backend/app/repositories/` | Database access only | AI prompts, HTTP logic |

`backend/app/main.py`: startup and global configuration only.

## 3. AI agent architecture

- One specialized agent per responsibility: `discovery_agent`, `enrichment_agent`, `research_agent`, `qualification_agent`, `personalization_agent`, `followup_agent`.
- `agents/orchestrator.py` coordinates only: Discovery → Enrichment → Research → Qualification → Personalization → Human Approval → Outreach. It must not hold agent implementations; every agent stays independently testable.
- Prompts in `backend/app/prompts/`, each defining role, context, output schema, fabrication prohibition, failure and uncertainty behavior.
- Vendor-agnostic AI chain: `Agent → LLM service interface → provider adapter → provider`.
- Providers are selected by config, never by importing a vendor SDK directly: `LLM_PROVIDER=groq`, `SEARCH_PROVIDER=mock|serper`, `EMAIL_PROVIDER=local|resend`. Defaults are offline (`mock`, `local`), so live calls only happen when a provider and its API key are set.
- Structured output preferred; AI output validated before persistence.

## 4. Frontend architecture

```
Page → Feature component → Reusable UI → Hook / API function → FastAPI
```

- App Router under `frontend/app/`; Server Components by default, `"use client"` only for state/effects/browser APIs.
- All HTTP through `frontend/lib/api/client.ts` + feature API modules — no scattered `fetch`.
- Types in `frontend/types/` mirror backend contracts.
- Base primitives in `frontend/components/ui/`; feature components compose them.
- Simplest state (`useState`/`useReducer`/server-state); no global store for local state.
- No business decisions hard-coded in UI.

## 5. Background jobs

Long-running work (discovery, bulk enrichment, research, campaigns, follow-up scheduling, analytics aggregation) never blocks HTTP. API returns `{ "run_id", "status": "queued" }`; runs persisted and observable.

## 6. Security & data boundaries

- Env vars: backend `DATABASE_URL`, `SECRET_KEY`, `GROQ_API_KEY`, `EMAIL_PROVIDER`, `EMAIL_API_KEY`, `EMAIL_FROM`, `SEARCH_PROVIDER`, `SEARCH_API_KEY`, `CRM_API_KEY`; frontend only `NEXT_PUBLIC_API_URL`. Never commit `.env`.
- Auth server-side (HTTP-only cookies); protected routes validate the user.
- Persistence concerns stay inside repositories; business logic stays ORM-independent.

## 7. Error contract

```json
{ "error": { "code": "LEAD_NOT_FOUND", "message": "The requested lead does not exist." } }
```

No stack traces or internal details exposed to users; frontend maps errors to friendly messages.

## 8. Principles

Modular, Typed, Secure, Testable, Observable, Reusable, Scalable, Maintainable — when architecture and quick implementation conflict, prefer the architecture.
