# process.md — Running Processes & Recovery State

> Purpose: capture live process/terminal state so that if a terminal (or this session) is terminated,
> everything needed to resume is saved here.
>
> Last updated: 2026-10-08 (during dashboard UI redesign verification)

---

## 1. Live processes right now

| Service            | Port | PID   | Process | Started              | Notes |
|--------------------|------|-------|---------|----------------------|-------|
| Frontend (Next.js) | 3000 | 17528 | node    | 2026-10-08 11:34:55  | `npm run start` (production build of `.next`) |
| Backend (FastAPI)  | 8001 | 10380 | python  | 2026-10-07 19:49:51  | `uvicorn app.main:app --port 8001` |
| **NOT OURS**       | 8000 | 4828  | python  | 2026-10-07 14:02:29  | "Customer Support Agent API" — unrelated, **do not kill** |

Other node/python helpers:
- node 16708 — npm wrapper for the frontend process
- python 17288 — uvicorn reloader/worker child of the backend

⚠️ PIDs change on restart. Always re-detect by **port**, not by stored PID.

---

## 2. Log files (persisted outside the terminal)

| Log | Path |
|-----|------|
| Backend stdout | `C:\Users\missa\AppData\Local\Temp\opencode\be.log` |
| Backend stderr | `C:\Users\missa\AppData\Local\Temp\opencode\be.err.log` |
| Frontend stdout | `C:\Users\missa\AppData\Local\Temp\opencode\fe.log` |
| Frontend stderr | `C:\Users\missa\AppData\Local\Temp\opencode\fe.err.log` |

Tail a log:
```powershell
Get-Content "C:\Users\missa\AppData\Local\Temp\opencode\fe.log" -Tail 20
```

---

## 3. Detect / start / stop / restart

Detect by port:
```powershell
Get-NetTCPConnection -LocalPort 3000 -State Listen | Select-Object OwningProcess
Get-NetTCPConnection -LocalPort 8001 -State Listen | Select-Object OwningProcess
```

Start backend (FastAPI, port 8001):
```powershell
Start-Process -FilePath "E:\Lead-genertion\Lead-generation-agent\backend\.venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","app.main:app","--port","8001" `
  -WorkingDirectory "E:\Lead-genertion\Lead-generation-agent\backend" `
  -RedirectStandardOutput "C:\Users\missa\AppData\Local\Temp\opencode\be.log" `
  -RedirectStandardError  "C:\Users\missa\AppData\Local\Temp\opencode\be.err.log" `
  -WindowStyle Hidden
```

Start frontend (Next.js, port 3000):
```powershell
Start-Process -FilePath "npm.cmd" -ArgumentList "run","start" `
  -WorkingDirectory "E:\Lead-genertion\Lead-generation-agent\frontend" `
  -RedirectStandardOutput "C:\Users\missa\AppData\Local\Temp\opencode\fe.log" `
  -RedirectStandardError  "C:\Users\missa\AppData\Local\Temp\opencode\fe.err.log" `
  -WindowStyle Hidden
```

Stop by port (safe — targets only the listener):
```powershell
$p = (Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess
Stop-Process -Id $p -Force
$p = (Get-NetTCPConnection -LocalPort 8001 -State Listen).OwningProcess
Stop-Process -Id $p -Force
```

After changing frontend code, you must **rebuild + restart** (production server serves `.next`):
```powershell
cd "E:\Lead-genertion\Lead-generation-agent\frontend"
npm run lint
npm run build     # then restart `npm run start`
```

---

## 4. Verification / smoke test

Script: `C:\Users\missa\AppData\Local\Temp\opencode\smoke_frontend.py`
(run with the backend venv python; needs both servers up)

```powershell
& "E:\Lead-genertion\Lead-generation-agent\backend\.venv\Scripts\python.exe" `
  "C:\Users\missa\AppData\Local\Temp\opencode\smoke_frontend.py"
```

- Expected: **19/19 pass** on a clean DB.
- The `register 409` result on re-runs is expected (test user `smoke2@test.dev` already exists) — not a real failure.
- Test credentials: `smoke2@test.dev` / `password123`

Quick authenticated dashboard marker check:
```powershell
& "E:\Lead-genertion\Lead-generation-agent\backend\.venv\Scripts\python.exe" `
  "C:\Users\missa\AppData\Local\Temp\opencode\check_search.py"
```

---

## 5. Environment notes

- Frontend env: `frontend\.env.local` → `NEXT_PUBLIC_API_URL=http://localhost:8001`
- Port 8000 is occupied by an unrelated app → our backend intentionally uses **8001**.
- Backend uses Neon Postgres in prod / sqlite dev fallback; `GROQ_API_KEY` optional (deterministic fallback).
- `next.config.ts` must keep `cacheComponents: false` (do not re-enable).

---

## 6. Current work state (UI redesign)

Task: restyle the frontend to match `Lead-generation-agent/docs/UI design.png`
(decoded programmatically via OCR + pixel sampling, since the model cannot view images).

Status:
- [x] Design decoded (layout, palette: bg `#f6fafd`, primary `#1e67fd`, CTA gradient `#7d93fb→#6194fd`, status colors)
- [x] Tokens updated in `app/globals.css` (+ `--violet`, `--cyan`)
- [x] Sidebar / Header redesigned; topbar search → `/dashboard/leads?q=`
- [x] Badge tones + `statusMeta` remapped
- [x] Dashboard rebuilt: greeting + UTC clock pill, 4 KPI cards, performance line chart, status donut, agent status, recent activity, recent leads, CTA card
- [x] `lib/dashboardData.ts` server data layer (KPI totals, status distribution, activity feed)
- [x] `npm run lint` clean, `npm run build` passes
- [x] Smoke: 18/19 (only expected register 409), new dashboard markers all render
- [x] Final re-verify after latest rebuild: `/dashboard/leads?q=Sarah` → 200, search prefilled, "AI Agents" nav present

Key new files:
- `frontend/lib/dashboardData.ts`
- `frontend/components/dashboard/{DashboardOverview,StatCard,CtaCard,PerformanceChart,StatusDonut,AgentStatus,Activity,RecentLeads,DateTimePill}.tsx`
- `frontend/app/dashboard/page.tsx` (rewritten)