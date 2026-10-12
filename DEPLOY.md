# Deployment Guide — Vercel + Render + Neon

Quick-launch topology:

```
Browser ──▶ Vercel (Next.js)  ──/api/v1/* rewrite──▶  Render (FastAPI)  ──▶  Neon (Postgres + pgvector)
```

The browser talks **only to the Vercel domain**; Next.js proxies `/api/v1/*` to Render.
This keeps the auth cookie **first-party** (no third-party-cookie blocking, no CORS issues),
and server components call Render directly via `API_INTERNAL_URL`.

Never commit `.env` files or real secrets.

---

## 0. Prerequisites

- Accounts: [Neon](https://neon.tech), [Render](https://render.com), [Vercel](https://vercel.com)
- Repo pushed to GitHub (this repo).
- Provider keys ready: Groq, Serper, Resend (or leave search/email in mock/local mode).

---

## 1. Neon (database)

1. Create a project → create a database (e.g. `leadgen`).
2. Copy the **direct** connection string (the one *without* `-pooler`), e.g.
   `postgresql://USER:PASSWORD@ep-xxx.region.aws.neon.tech/leadgen?sslmode=require`.
3. Convert it for the async `asyncpg` driver:
   ```
   postgresql+asyncpg://USER:PASSWORD@ep-xxx.region.aws.neon.tech/leadgen?ssl=require
   ```
   Keep this as `DATABASE_URL`.
4. pgvector: no manual step — the first migration runs `CREATE EXTENSION IF NOT EXISTS vector`.

---

## 2. Render (backend)

1. **New → Blueprint**, connect this repo. Render reads `render.yaml` (service `leadgen-api`).
2. When prompted, fill the `sync: false` secrets:
   - `DATABASE_URL` = the Neon asyncpg URL from step 1.
   - `SECRET_KEY` = `python -c "import secrets; print(secrets.token_urlsafe(48))"`
   - `GROQ_API_KEY`, `SEARCH_API_KEY`, `EMAIL_API_KEY`, `EMAIL_FROM`
   - `HUNTER_API_KEY` (optional — enables contact email lookup; leave unset to disable)
   - `CORS_ORIGINS` = `["https://<your-app>.vercel.app"]` (update after Vercel deploy)
3. Deploy. The start command runs `alembic upgrade head` (creates all tables) then starts the API.
4. Verify: open `https://<render-service>.onrender.com/health` → `{"status":"ok",...}`.
5. Copy the service URL — you need it for Vercel (`API_PROXY_TARGET`, `API_INTERNAL_URL`).

> Free tier sleeps after inactivity and wakes on request. Background agent runs execute
> in-process; keep runs short. No persistent disk is needed (Postgres is external).

---

## 3. Vercel (frontend)

1. **Add New → Project**, import this repo.
2. **Root Directory = `frontend`** (important — this is a monorepo).
3. Environment Variables (Production):
   | Key | Value |
   | --- | --- |
   | `NEXT_PUBLIC_API_URL` | *(empty)* |
   | `API_PROXY_TARGET` | `https://<render-service>.onrender.com` |
   | `API_INTERNAL_URL` | `https://<render-service>.onrender.com` |
4. Deploy. Note your URL, e.g. `https://your-app.vercel.app`.
5. Go back to Render → set `CORS_ORIGINS` = `["https://your-app.vercel.app"]` → redeploy backend.

---

## 4. Verify end-to-end

1. Visit the Vercel URL → **Register** a user → you should land on the dashboard (login persists).
2. Create a lead (or run the **Discovery** agent) → **Export CSV** downloads.
3. Queue an agent run → check the **Agents** page for status.
4. Send a test outreach (email) — see step 6 for the sender domain.

If login does not persist: confirm `NEXT_PUBLIC_API_URL` is empty and `API_PROXY_TARGET` is set,
and that the browser is hitting `https://<vercel-domain>/api/v1/...` (not the Render URL directly).

---

## 5. Custom domain (recommended for client handover)

Attach the client's domain to **both** services on the *same* registrable domain:

- `app.clientdomain.com` → Vercel (Project → Domains)
- `api.clientdomain.com` → Render (Service → Settings → Custom Domain)

Then update:
- Vercel: `API_PROXY_TARGET` / `API_INTERNAL_URL` = `https://api.clientdomain.com`
- Render: `CORS_ORIGINS` = `["https://app.clientdomain.com"]`

(With the proxy in place, cookies stay first-party even across the two subdomains.)

---

## 6. Email sending

Two live providers are supported; set `EMAIL_PROVIDER` to pick one.

**Resend** (`EMAIL_PROVIDER=resend`)
- Test sender `onboarding@resend.dev` only delivers to the Resend account owner.
- For real outreach: verify the client's domain in Resend, then set on Render:
  `EMAIL_FROM=leads@clientdomain.com` and keep `EMAIL_PROVIDER=resend`.

**SMTP — free, no domain needed** (`EMAIL_PROVIDER=smtp`)
- Works with any SMTP relay; needs no domain for a Gmail App Password.
- Gmail: `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USE_TLS=true`,
  `SMTP_USERNAME=<gmail>`, `SMTP_PASSWORD=<app password>`, `EMAIL_FROM=<gmail>`.
- Brevo: `SMTP_HOST=smtp-relay.brevo.com`, `SMTP_PORT=587` (login email + SMTP key).
- SMTP2GO: `SMTP_HOST=mail.smtp2go.com`, `SMTP_PORT=2525`.
- Zoho: `SMTP_HOST=smtp.zoho.com`, `SMTP_PORT=465`, `SMTP_USE_SSL=true`.
- If the SMTP vars are missing the app falls back to `local` (records only).

---

## 6b. Contact email lookup (Hunter.io / Enrich.so)

- During enrichment, leads that have a **website but no email** are looked up.
  Pick a provider with `EMAIL_FINDER_PROVIDER=hunter|enrich`.
- **Hunter.io** (`HUNTER_API_KEY`): domain search, or email finder when a contact
  name exists. Free plan ~50 credits/month.
- **Enrich.so** (`ENRICH_API_KEY`): email finder only — needs a first + last name.
  Costs 10 credits per found email (100 free credits ≈ 10 lookups).
- Without the matching key, email finding is skipped — the app never invents an
  address. Emails found are stored with confidence `verified` or `unverified`.

## 6c. Free contact discovery (website scrape + Serper search)

- Runs **before** the email finder during enrichment, and needs **no paid API**.
- **Website scrape** (`CONTACT_FINDER_ENABLED=true`, default): reads the
  company's own homepage + `/contact` + `/about` + `/team` pages and extracts
  only emails published there (mailto links = `verified`, plain text =
  `unverified`). Set `CONTACT_FINDER_MAX_PAGES` / `CONTACT_FINDER_TIMEOUT_SECONDS`.
- **Serper search**: when `SEARCH_API_KEY` is set, runs a targeted Google query
  (`"<domain> email"`) and reads emails from the snippets (`unverified`).
- Only emails on the target domain are kept; nothing is ever invented. If the
  scrape finds nothing, the configured email finder (Hunter/Enrich) runs next.

---

## 6d. One-click pipeline & auto outreach drafts

- On the Agents page, choose **Full pipeline** and enable
  **"Auto-create outreach drafts for qualified leads"** (on by default). The
  run request sets `prepare_outreach: true`.
- At the end of the pipeline the backend creates an outreach draft
  (`PENDING_APPROVAL`) for every qualified lead that has an email, skipping
  `DO_NOT_CONTACT` / opted-out leads and leads that already have an active or
  sent outreach. The count is returned as `output_summary.outreach_drafts`.
- Drafts are **never auto-sent**: a human must still approve and send each one
  (see constitution §36, Outreach Safety).

---

## 7. Security checklist

- [ ] Rotate any keys that were ever shared in plaintext; put new ones only in Render/Vercel.
- [ ] `SECRET_KEY` is a fresh 48-byte value (never the default).
- [ ] `.env` / `.env.local` are gitignored and not committed.
- [ ] `AUTO_CREATE_TABLES=false` in production (migrations own the schema).
- [ ] `COOKIE_SECURE=true`.

---

## 8. Redeploys & migrations

- Render redeploys run `alembic upgrade head` automatically before start.
- New migration: locally `alembic revision --autogenerate -m "..."`, commit, push, redeploy.
- Rollback: `alembic downgrade -1` (run via a Render shell).

---

## Local equivalent

```powershell
# backend
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
# frontend (proxies /api/v1 -> API_PROXY_TARGET, default http://localhost:8001)
cd frontend
npm run dev
```
