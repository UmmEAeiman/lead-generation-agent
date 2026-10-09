# API Specification — AI Lead Generation Agent

Source of truth: [`../constitution-leads.md`](../constitution-leads.md) (§7, 34, 42). All endpoints are versioned under `/api/v1`. Contracts are defined here before frontend integration; frontend types in `frontend/types/` must match and be updated whenever this spec changes.

## Conventions

- Auth: HTTP-only cookie session; protected routes validate the authenticated user.
- Errors: `{ "error": { "code": "...", "message": "..." } }` with appropriate HTTP status codes.
- Pagination: `?page=&page_size=` (response includes `total`, `page`, `page_size`).
- Filtering: `?status=&score_min=&score_max=&industry=&location=&q=` on list endpoints.
- Long-running operations return `202` with `{ "run_id": "run_123", "status": "queued" }`.

## Leads

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/leads` | List leads (search/filter/sort/paginate) |
| GET | `/api/v1/leads/{lead_id}` | Lead detail (company, contact, score, research, activity, outreach) |
| POST | `/api/v1/leads` | Create lead (duplicate check on normalized domain/email) |
| PATCH | `/api/v1/leads/{lead_id}` | Update lead / change status |
| DELETE | `/api/v1/leads/{lead_id}` | Delete lead |

Lead statuses: `NEW, ENRICHING, QUALIFIED, UNQUALIFIED, CONTACTED, REPLIED, INTERESTED, MEETING_BOOKED, CONVERTED, REJECTED, DO_NOT_CONTACT`.

## Campaigns

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/campaigns` | List campaigns |
| POST | `/api/v1/campaigns` | Create campaign |
| PATCH | `/api/v1/campaigns/{campaign_id}` | Update campaign |

## Agents

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/agents/discovery/run` | Queue discovery run |
| POST | `/api/v1/agents/qualification/run` | Queue qualification run |
| POST | `/api/v1/agents/personalization/run` | Queue personalization run |
| GET | `/api/v1/agents/runs` | List agent runs (status, progress, summaries) |
| GET | `/api/v1/agents/runs/{run_id}` | Run status/result |

Example — qualification:

```
POST /api/v1/agents/qualification/run

Request:  { "lead_ids": ["1", "2", "3"] }
Response: { "run_id": "run_123", "status": "queued" }
```

Run object: `run_id, agent_type, campaign_id, started_at, completed_at, status (queued|running|completed|failed|cancelled), input_summary, output_summary, error, tokens_used, duration`.

## Outreach

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/outreach` | List outreach records |
| POST | `/api/v1/outreach/prepare` | Prepare outreach (human approval required before send) |
| POST | `/api/v1/outreach/{id}/approve` | Approve prepared outreach |
| POST | `/api/v1/outreach/{id}/send` | Send approved outreach (409 if not approved) |
| POST | `/api/v1/leads/{lead_id}/opt-out` | Record opt-out; stops future outreach (`DO_NOT_CONTACT`) |

## Analytics

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/analytics/overview` | Totals, rates, campaign performance, agent success/failure |

Metrics: total leads, qualified leads, qualification rate, contacted, reply rate, positive reply rate, meetings, conversion rate — computed from persisted data.

## Auth & users

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Establish session (HTTP-only cookie) |
| POST | `/api/v1/auth/logout` | Clear session |
| GET | `/api/v1/users/me` | Current authenticated user |

## Example error responses

| Code | Status | Meaning |
|---|---|---|
| `LEAD_NOT_FOUND` | 404 | Lead does not exist |
| `DUPLICATE_LEAD` | 409 | Same normalized domain/email already exists |
| `UNAUTHORIZED` | 401 | Missing/invalid session |
| `VALIDATION_ERROR` | 422 | Request body failed schema validation |
