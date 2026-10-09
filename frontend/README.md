# AI Lead Generation Agent — Frontend

Next.js 16 (App Router) + TypeScript + Tailwind CSS 4 client for the FastAPI backend.

## Setup

```bash
cd Lead-generation-agent/frontend
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL to your backend
npm install
npm run dev                        # http://localhost:3000
```

The backend must allow `http://localhost:3000` in `cors_origins` (default) and
sessions are shared through the HTTP-only `access_token` cookie.

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Development server |
| `npm run lint` | ESLint (next/core-web-vitals + TypeScript rules) |
| `npm run build` | Production build (runs type checking) |
| `npm start` | Serve the production build |

## Architecture

```
Page (app/) → Feature component (components/<feature>/)
  → Reusable UI (components/ui/) → Hook (hooks/) / API function (lib/api/) → FastAPI
```

- `types/` — API contract types; must match `spec/api.md` and the backend schemas.
- `lib/api/client.ts` — single `apiRequest<T>` (credentials included, error envelope
  `{"error": {code, message}}` → `ApiRequestError`); feature modules: `auth`, `leads`,
  `campaigns`, `agents`, `outreach`, `analytics`.
- `lib/api/server.ts` — cookie-forwarding fetch for server components (auth guard).
- `components/ui/` — Button, Input, Select, Textarea, Checkbox, Modal, Card, Badge,
  Table, Pagination, Dropdown, Tabs, Skeleton, Spinner, EmptyState, ErrorState,
  ConfirmDialog. Design tokens live in `app/globals.css` as CSS variables.
- Every async view handles loading (Skeleton), error (ErrorState + retry), and
  empty (EmptyState) states.

## Pages

| Route | Purpose |
|---|---|
| `/login`, `/register` | Cookie-based auth |
| `/dashboard` | Overview: stats, pipeline, agent activity, recent leads, campaign performance |
| `/dashboard/leads` | Search/filter/sort/paginate, bulk selection + bulk agent runs, create |
| `/dashboard/leads/[id]` | Full lead detail, status changes, prepare outreach, opt-out, delete |
| `/dashboard/campaigns` | ICP campaigns, discovery runs, status management |
| `/dashboard/agents` | Queue discovery/pipeline runs, live run progress (3s polling) |
| `/dashboard/outreach` | Prepare → approve → send flow, human approval enforced |
| `/dashboard/analytics` | Conversion metrics from persisted data |
