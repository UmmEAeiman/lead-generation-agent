# Requirements Specification — AI Lead Generation Agent

Source of truth: [`../constitution-leads.md`](../constitution-leads.md). This spec elaborates constitution §2 (Core Product Goal).

## 1. Purpose

The system helps users discover, qualify, research, and manage potential business leads.

## 2. Workflow

```
User defines ICP → Lead Discovery → Lead Collection → Data Cleaning →
Lead Enrichment → AI Research → AI Qualification/Scoring →
AI Personalization → Outreach Preparation → Human Approval →
Outreach → Response Tracking → AI Follow-up → CRM/Lead Pipeline → Analytics
```

Discovery, enrichment, scoring, outreach, and CRM responsibilities MUST stay separated.

## 3. Functional requirements

### FR-1 ICP definition
- User defines target industry, location, company size, and keywords.

### FR-2 Lead discovery
- Discovery Agent finds leads matching the ICP.
- Long-running discovery runs in a background job; API returns `{ "run_id", "status" }`.

### FR-3 Enrichment
- Enrichment Agent adds: company, website, industry, location, contact, role, email, social profiles, company size, business description.
- Every value is labeled `verified` / `unverified` / `unknown`. Never fabricate.

### FR-4 Research
- Research Agent analyzes website quality, business model, services, technology, pain points, current tools, buying signals.

### FR-5 Qualification
- Explicit, configurable scoring criteria totaling 100 points:
  - ICP fit 25 · Company size 15 · Industry fit 20 · Buying signal 20 · Pain point 10 · Contact quality 10
- Bands: 0–39 Low · 40–69 Medium · 70–100 High.

### FR-6 Personalization
- Personalized outreach based only on verified research; omit unknowns; never invent achievements, facts, titles, events, revenue, or technology usage.

### FR-7 Outreach safety
- Human approval required before outreach.
- `DO_NOT_CONTACT` and valid opt-outs permanently stop automated outreach.
- Duplicate prevention (normalized domain, email, provider ID), rate limits, provider policies, applicable laws.

### FR-8 Follow-up
- Follow-up states: `NO_RESPONSE`, `INTERESTED`, `NOT_INTERESTED`, `NEEDS_INFO`, `MEETING_REQUESTED`, `MEETING_BOOKED`, `DO_NOT_CONTACT`.

### FR-9 Lead management UI
- Listing: search, filtering (status, score, industry, location), sorting, pagination, bulk selection.
- Detail: company/contact info, score, qualification reasons, AI research, pain points, activity history, outreach, follow-ups.

### FR-10 Dashboard
- Metrics: total leads, qualified, hot, contacted, replies, meetings, conversions, conversion rate.
- Sections: Overview, Lead Pipeline, Recent Leads, Agent Activity, Campaign Performance.

### FR-11 Analytics
- Qualification rate, reply rate, positive reply rate, conversion rate, campaign performance, agent success/failure rate — computed from persisted data.

### FR-12 Observability
- Agent runs tracked: `run_id, agent_type, campaign_id, started_at, completed_at, status, input_summary, output_summary, error, tokens_used, duration`.
- Statuses: Queued, Running, Completed, Failed, Cancelled. Progress percentages must be real, never faked.

## 4. Non-functional requirements

| Area | Requirement |
|---|---|
| Security | No secrets in browser, source, or logs; HTTP-only cookie auth; validated protected routes |
| Data quality | Distinguish Known / Verified / Inferred / Unknown; never upgrade an inference to a fact |
| Performance | Paginated queries and lists, async I/O, background jobs for long-running work |
| Accessibility | Keyboard navigation, focus states, semantic HTML, contrast, labels |
| Responsive | Mobile, tablet, desktop, large desktop |
| Testing | Unit + integration tests for services, repos, endpoints, scoring, auth, duplicates, agent output validation |

## 5. Definition of done

See constitution §56: requirement, backend, API contract, frontend, types, loading/error/empty states, validation, security review, tests, lint, type checks, production build, no secrets, docs.
