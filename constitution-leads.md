# AI Lead Generation Agent --- Project Constitution

## 1. Purpose

This document is the single source of truth for the AI Lead Generation
Agent application.

All generated code, manual code, refactors, UI work, API work, database
work, and AI-agent behavior MUST follow the rules in this document.

The application is a full-stack lead-generation platform with:

-   Backend: FastAPI + Python
-   Frontend: Next.js 16 + TypeScript
-   Styling: Tailwind CSS + `global.css`
-   UI: Reusable, composable components
-   AI: Agent-based lead discovery, enrichment, qualification,
    personalization, and follow-up
-   Database: Relational database accessed through a dedicated
    data-access layer
-   API: RESTful JSON API
-   Authentication: Secure server-side authentication
-   Background work: Asynchronous/background job architecture where
    appropriate

------------------------------------------------------------------------

# 2. Core Product Goal

The system helps users discover, qualify, research, and manage potential
business leads.

The high-level workflow is:

``` text
User defines ICP
      ↓
Lead Discovery
      ↓
Lead Collection
      ↓
Data Cleaning
      ↓
Lead Enrichment
      ↓
AI Research
      ↓
AI Qualification / Scoring
      ↓
AI Personalization
      ↓
Outreach Preparation
      ↓
Human Approval
      ↓
Outreach
      ↓
Response Tracking
      ↓
AI Follow-up
      ↓
CRM / Lead Pipeline
      ↓
Analytics
```

The application MUST keep discovery, enrichment, scoring, outreach, and
CRM responsibilities separated.

------------------------------------------------------------------------

# 3. Non-Negotiable Engineering Principles

## 3.1 Separation of Concerns

Never put unrelated responsibilities into one file.

Bad:

``` text
api route
+ database query
+ AI prompt
+ business logic
+ email sending
```

Good:

``` text
API Route
   ↓
Service
   ↓
Agent
   ↓
Repository
   ↓
Database
```

The frontend follows the same principle:

``` text
Page
   ↓
Feature Component
   ↓
Reusable UI Component
   ↓
API Client
```

------------------------------------------------------------------------

## 3.2 Reusability

Do not duplicate:

-   Buttons
-   Inputs
-   Modals
-   Tables
-   Cards
-   Badges
-   Loading states
-   Empty states
-   Error states
-   API request logic
-   Validation logic
-   AI prompt construction

Reusable behavior belongs in reusable modules.

------------------------------------------------------------------------

## 3.3 Type Safety

TypeScript MUST be used strictly.

Avoid:

``` ts
any
```

unless there is a documented technical reason.

Prefer:

``` ts
type LeadStatus =
  | "new"
  | "qualified"
  | "contacted"
  | "replied"
  | "meeting"
  | "converted"
  | "rejected";
```

Backend request/response schemas MUST be explicitly defined with
Pydantic.

------------------------------------------------------------------------

## 3.4 Security First

Never expose:

-   API keys
-   AI provider secrets
-   Database credentials
-   SMTP credentials
-   JWT secrets
-   Private environment variables

to the browser.

Frontend-accessible environment variables MUST only contain values
intentionally safe for public exposure.

------------------------------------------------------------------------

# 4. Recommended Monorepo Structure

``` text
lead-generation-agent/
│
├── constitution.md
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── leads.py
│   │   │       ├── campaigns.py
│   │   │       ├── agents.py
│   │   │       ├── outreach.py
│   │   │       ├── analytics.py
│   │   │       └── users.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── lead.py
│   │   │   ├── campaign.py
│   │   │   ├── outreach.py
│   │   │   └── agent_run.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── lead.py
│   │   │   ├── campaign.py
│   │   │   ├── outreach.py
│   │   │   └── agent.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── lead_repository.py
│   │   │   ├── campaign_repository.py
│   │   │   ├── user_repository.py
│   │   │   └── agent_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── lead_service.py
│   │   │   ├── campaign_service.py
│   │   │   ├── outreach_service.py
│   │   │   ├── auth_service.py
│   │   │   └── analytics_service.py
│   │   │
│   │   ├── agents/
│   │   │   ├── orchestrator.py
│   │   │   ├── discovery_agent.py
│   │   │   ├── enrichment_agent.py
│   │   │   ├── qualification_agent.py
│   │   │   ├── research_agent.py
│   │   │   ├── personalization_agent.py
│   │   │   └── followup_agent.py
│   │   │
│   │   ├── integrations/
│   │   │   ├── llm/
│   │   │   ├── email/
│   │   │   ├── search/
│   │   │   └── crm/
│   │   │
│   │   ├── prompts/
│   │   │   ├── qualification.py
│   │   │   ├── research.py
│   │   │   ├── personalization.py
│   │   │   └── followup.py
│   │   │
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── migrations/
│   │   │
│   │   └── utils/
│   │       ├── validators.py
│   │       ├── normalization.py
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   │
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   │
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   │
│   │   └── dashboard/
│   │       ├── page.tsx
│   │       ├── leads/
│   │       │   ├── page.tsx
│   │       │   └── [id]/
│   │       │       └── page.tsx
│   │       ├── campaigns/
│   │       ├── agents/
│   │       ├── outreach/
│   │       └── analytics/
│   │
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── ErrorState.tsx
│   │   │
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── DashboardLayout.tsx
│   │   │
│   │   ├── leads/
│   │   ├── campaigns/
│   │   ├── agents/
│   │   └── analytics/
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── leads.ts
│   │   │   ├── campaigns.ts
│   │   │   ├── agents.ts
│   │   │   └── analytics.ts
│   │   ├── constants.ts
│   │   ├── utils.ts
│   │   └── validators.ts
│   │
│   ├── hooks/
│   │   ├── useLeads.ts
│   │   ├── useCampaigns.ts
│   │   └── useAgentRun.ts
│   │
│   ├── types/
│   │   ├── lead.ts
│   │   ├── campaign.ts
│   │   ├── agent.ts
│   │   └── api.ts
│   │
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.ts
│
└── docs/
    ├── architecture.md
    ├── api.md
    ├── agents.md
    └── deployment.md
```

------------------------------------------------------------------------

# 5. Backend Constitution --- FastAPI

## 5.1 FastAPI Application

`backend/app/main.py` is responsible only for application startup and
global configuration.

It SHOULD NOT contain business logic.

Example responsibility:

``` python
from fastapi import FastAPI

app = FastAPI(
    title="AI Lead Generation API",
    version="1.0.0",
)
```

Routers are registered through the API router.

------------------------------------------------------------------------

# 6. Backend Layer Architecture

The backend MUST follow:

``` text
Router
  ↓
Schema validation
  ↓
Service
  ↓
Agent / Integration
  ↓
Repository
  ↓
Database
```

## Router

Routers handle:

-   HTTP methods
-   Authentication dependencies
-   Request validation
-   Response schemas
-   HTTP status codes

Routers MUST NOT contain complex business logic.

------------------------------------------------------------------------

## Service

Services contain application/business logic.

Example:

``` text
lead_service.py
```

Responsibilities:

-   Create lead
-   Update lead
-   Qualify lead
-   Trigger enrichment
-   Change lead status

------------------------------------------------------------------------

## Repository

Repositories contain database access.

Example:

``` python
lead_repository.py
```

Repositories MUST NOT contain AI prompts or HTTP-specific logic.

------------------------------------------------------------------------

# 7. API Naming Convention

Use REST-style endpoints.

``` text
GET    /api/v1/leads
GET    /api/v1/leads/{lead_id}
POST   /api/v1/leads
PATCH  /api/v1/leads/{lead_id}
DELETE /api/v1/leads/{lead_id}

GET    /api/v1/campaigns
POST   /api/v1/campaigns

POST   /api/v1/agents/discovery/run
POST   /api/v1/agents/qualification/run
POST   /api/v1/agents/personalization/run

GET    /api/v1/analytics/overview
```

All API routes MUST be versioned.

------------------------------------------------------------------------

# 8. Pydantic Schemas

Separate database models from API schemas.

Example:

``` python
class LeadCreate(BaseModel):
    company_name: str
    website: str | None = None
    email: EmailStr | None = None
```

Do not return database ORM objects blindly.

Use explicit response schemas.

------------------------------------------------------------------------

# 9. AI Agent Architecture

The application uses specialized agents rather than one giant AI prompt.

## Agent Roles

### Discovery Agent

Purpose:

Find potential leads according to the user's ICP.

Input:

``` json
{
  "industry": "Dental",
  "location": "United States",
  "company_size": "5-50",
  "keywords": ["dental clinic", "dentist"]
}
```

Output:

``` json
{
  "leads": []
}
```

------------------------------------------------------------------------

### Enrichment Agent

Adds missing information:

``` text
Company
Website
Industry
Location
Contact
Role
Email
Social profiles
Company size
Business description
```

The agent MUST distinguish:

``` text
verified
unverified
unknown
```

Never fabricate lead information.

------------------------------------------------------------------------

### Research Agent

Analyzes the business.

Possible analysis:

``` text
Website quality
Business model
Services
Technology
Potential pain points
Current tools
Buying signals
```

------------------------------------------------------------------------

### Qualification Agent

Assigns a score.

Example:

``` text
0–39   = Low
40–69  = Medium
70–100 = High
```

The scoring criteria MUST be explicit and configurable.

Example:

``` text
ICP fit              25 points
Company size         15 points
Industry fit         20 points
Buying signal        20 points
Pain point           10 points
Contact quality      10 points
--------------------------------
Total                100 points
```

------------------------------------------------------------------------

### Personalization Agent

Creates personalized outreach using verified research.

It MUST NOT invent:

-   Personal achievements
-   Company facts
-   Job titles
-   Customer relationships
-   Events
-   Revenue
-   Technology usage

If information is unknown, the agent must omit it.

------------------------------------------------------------------------

### Follow-up Agent

Controls follow-up messaging based on lead status.

Possible states:

``` text
NO_RESPONSE
INTERESTED
NOT_INTERESTED
NEEDS_INFO
MEETING_REQUESTED
MEETING_BOOKED
DO_NOT_CONTACT
```

`DO_NOT_CONTACT` MUST stop automated outreach.

------------------------------------------------------------------------

# 10. Agent Orchestrator

`agents/orchestrator.py` coordinates agent execution.

Example:

``` text
Campaign
   ↓
Discovery Agent
   ↓
Enrichment Agent
   ↓
Research Agent
   ↓
Qualification Agent
   ↓
Personalization Agent
   ↓
Human Approval
   ↓
Outreach
```

The orchestrator MUST NOT become a giant file containing every agent's
implementation.

Each agent remains independently testable.

------------------------------------------------------------------------

# 11. AI Output Rules

AI responses MUST use structured output whenever possible.

Prefer:

``` json
{
  "score": 82,
  "category": "high",
  "reasons": [
    "Strong ICP match",
    "Relevant business size"
  ]
}
```

over free-form text.

AI-generated data MUST be validated before persistence.

------------------------------------------------------------------------

# 12. Prompt Constitution

Prompts MUST be stored outside API routes.

Use:

``` text
backend/app/prompts/
```

Prompts should:

-   Define the agent role
-   Define available context
-   Define output schema
-   Explicitly prohibit fabrication
-   Define failure behavior
-   Define uncertainty behavior

Do not construct huge prompt strings directly inside routers.

------------------------------------------------------------------------

# 13. Lead Data Model

A lead SHOULD contain at least:

``` text
id
company_name
website
industry
location
company_size
contact_name
contact_role
email
phone
linkedin_url
source
source_url
description
lead_score
qualification
status
research_summary
pain_points
personalized_message
created_at
updated_at
```

Potential statuses:

``` text
NEW
ENRICHING
QUALIFIED
UNQUALIFIED
CONTACTED
REPLIED
INTERESTED
MEETING_BOOKED
CONVERTED
REJECTED
DO_NOT_CONTACT
```

------------------------------------------------------------------------

# 14. Frontend Constitution --- Next.js 16

Use the App Router.

Prefer:

``` text
app/
```

Do not introduce unnecessary routing systems.

------------------------------------------------------------------------

# 15. Server vs Client Components

Default to Server Components.

Use `"use client"` only when the component needs:

-   Browser interaction
-   React state
-   Event handlers
-   Client-side effects
-   Browser APIs

Avoid making entire pages client components unnecessarily.

------------------------------------------------------------------------

# 16. Frontend Architecture

Frontend flow:

``` text
Page
 ↓
Feature Component
 ↓
Reusable UI
 ↓
Hook / API function
 ↓
FastAPI
```

API communication MUST be centralized.

Do not scatter:

``` ts
fetch("http://localhost:8000/...")
```

throughout components.

Use:

``` text
lib/api/client.ts
```

and feature-specific API modules.

------------------------------------------------------------------------

# 17. API Client

Example:

``` ts
export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(endpoint, options);

  if (!response.ok) {
    throw new Error("API request failed");
  }

  return response.json();
}
```

Feature APIs then build on this abstraction.

------------------------------------------------------------------------

# 18. TypeScript Types

Keep API types in:

``` text
frontend/types/
```

Example:

``` ts
export interface Lead {
  id: string;
  companyName: string;
  website?: string;
  email?: string;
  leadScore: number;
  status: LeadStatus;
}
```

Types MUST match backend contracts.

------------------------------------------------------------------------

# 19. Reusable Components

Every repeated UI pattern SHOULD become a component.

Required base components:

``` text
Button
Input
Select
Textarea
Checkbox
Modal
Card
Badge
Table
Pagination
Dropdown
Tabs
Skeleton
Spinner
EmptyState
ErrorState
ConfirmDialog
```

Feature components should compose these primitives.

Example:

``` text
LeadTable
  ├── Table
  ├── Badge
  ├── Dropdown
  └── Button
```

------------------------------------------------------------------------

# 20. Component Rules

Components should have one clear responsibility.

Bad:

``` text
Dashboard.tsx
```

containing:

-   Sidebar
-   Header
-   Lead table
-   AI agent controls
-   Analytics
-   Modals
-   API requests

Good:

``` text
DashboardPage
 ├── DashboardHeader
 ├── StatsCards
 ├── LeadOverview
 ├── AgentStatus
 └── RecentActivity
```

------------------------------------------------------------------------

# 21. Tailwind CSS Constitution

Use Tailwind utility classes for component styling.

Keep global styles in:

``` text
app/globals.css
```

Global CSS SHOULD contain only:

-   CSS variables
-   Base typography
-   Global resets
-   Application-wide utilities
-   Theme definitions

Do not put component-specific CSS in `globals.css`.

------------------------------------------------------------------------

# 22. Design Tokens

Use CSS variables for the design system.

Example:

``` css
:root {
  --background: #ffffff;
  --foreground: #111827;
  --muted: #6b7280;
  --border: #e5e7eb;
  --primary: #2563eb;
  --primary-foreground: #ffffff;
  --success: #16a34a;
  --warning: #d97706;
  --danger: #dc2626;
}
```

Components should consume design tokens instead of inventing random
colors.

------------------------------------------------------------------------

# 23. UI Consistency

All screens MUST maintain:

-   Consistent spacing
-   Consistent border radius
-   Consistent typography
-   Consistent button sizes
-   Consistent status colors
-   Consistent loading behavior
-   Consistent error handling

Do not create a different button style for every page.

------------------------------------------------------------------------

# 24. Dashboard Requirements

The dashboard SHOULD provide:

``` text
Total Leads
Qualified Leads
Hot Leads
Contacted Leads
Replies
Meetings
Conversions
Conversion Rate
```

Main sections:

``` text
Overview
Lead Pipeline
Recent Leads
Agent Activity
Campaign Performance
```

------------------------------------------------------------------------

# 25. Lead Management UI

Lead listing should support:

-   Search
-   Filtering
-   Sorting
-   Pagination
-   Status filtering
-   Score filtering
-   Industry filtering
-   Location filtering
-   Bulk selection where appropriate

Lead detail should show:

``` text
Company Information
Contact Information
Lead Score
Qualification Reasons
AI Research
Pain Points
Activity History
Outreach
Follow-ups
```

------------------------------------------------------------------------

# 26. Loading, Error, and Empty States

Every asynchronous UI MUST account for:

``` text
Loading
Success
Error
Empty
```

Never leave the user staring at a blank page while data loads.

Use reusable components:

``` text
Skeleton
EmptyState
ErrorState
```

------------------------------------------------------------------------

# 27. Forms

Forms MUST:

-   Validate input
-   Show useful errors
-   Disable submission while processing
-   Show success/failure feedback
-   Prevent accidental duplicate submissions

Validation rules should be shared where practical.

------------------------------------------------------------------------

# 28. Authentication

Authentication MUST be handled securely.

Never store sensitive authentication secrets in:

``` text
localStorage
```

unless there is a deliberate, reviewed security architecture requiring
it.

Prefer secure, HTTP-only cookies for session/token handling where
appropriate.

Protected API routes MUST validate the authenticated user.

------------------------------------------------------------------------

# 29. Environment Variables

Backend:

``` text
DATABASE_URL=
SECRET_KEY=
LLM_API_KEY=
EMAIL_API_KEY=
SEARCH_API_KEY=
```

Frontend:

``` text
NEXT_PUBLIC_API_URL=
```

Never commit `.env`.

Provide:

``` text
.env.example
```

with variable names but no real secrets.

------------------------------------------------------------------------

# 30. Database Rules

Database operations MUST be handled through repositories.

Never perform raw database operations directly inside FastAPI route
functions.

Use migrations for schema changes.

Never modify production schema manually without a migration.

------------------------------------------------------------------------

# 31. Background Jobs

Long-running work MUST NOT block normal HTTP requests.

Examples:

``` text
Large lead discovery
Bulk enrichment
AI research
Email campaigns
Follow-up scheduling
Analytics aggregation
```

These should use a background-job/queue architecture when required.

The API should return a job/run identifier when appropriate:

``` json
{
  "run_id": "abc123",
  "status": "queued"
}
```

------------------------------------------------------------------------

# 32. Agent Run Tracking

Every agent execution SHOULD be observable.

Store:

``` text
run_id
agent_type
campaign_id
started_at
completed_at
status
input_summary
output_summary
error
tokens_used
duration
```

Do not store sensitive secrets in logs.

------------------------------------------------------------------------

# 33. Logging

Use structured logging.

Logs should help answer:

``` text
Which agent ran?
For which campaign?
For which lead?
What happened?
How long did it take?
Did it fail?
```

Avoid:

``` python
print("something happened")
```

in production code.

------------------------------------------------------------------------

# 34. Error Handling

Backend errors should return predictable API responses.

Example:

``` json
{
  "error": {
    "code": "LEAD_NOT_FOUND",
    "message": "The requested lead does not exist."
  }
}
```

Frontend should translate errors into user-friendly messages.

Never expose internal stack traces to users.

------------------------------------------------------------------------

# 35. Data Quality

The system MUST distinguish:

``` text
Known
Verified
Inferred
Unknown
```

AI MUST NOT turn an inference into a fact.

Example:

Bad:

``` text
The company uses Salesforce.
```

when no evidence exists.

Good:

``` text
CRM: Unknown
```

------------------------------------------------------------------------

# 36. Outreach Safety

Automated outreach MUST respect:

-   User approval requirements
-   Opt-out requests
-   `DO_NOT_CONTACT` status
-   Duplicate prevention
-   Rate limits
-   Provider policies
-   Applicable email/privacy laws

The system MUST stop future outreach after a valid opt-out.

------------------------------------------------------------------------

# 37. Duplicate Prevention

The system SHOULD prevent duplicate leads using suitable identifiers
such as:

``` text
normalized company domain
normalized email
provider/source ID
```

Do not rely only on company name.

------------------------------------------------------------------------

# 38. Testing

Backend tests:

``` text
tests/
├── unit/
└── integration/
```

Test:

-   Services
-   Repositories
-   API endpoints
-   Agent output validation
-   Authentication
-   Lead scoring
-   Duplicate detection

Frontend tests SHOULD cover critical:

-   Forms
-   Tables
-   Filters
-   API states
-   User interactions

------------------------------------------------------------------------

# 39. Code Quality

Before considering a feature complete:

``` text
Type checking
Linting
Formatting
Unit tests
Integration tests where required
Build verification
```

Remove:

-   Dead code
-   Unused imports
-   Debug logs
-   Temporary comments
-   Duplicate components
-   Hard-coded secrets

------------------------------------------------------------------------

# 40. Git Rules

Use meaningful commits.

Examples:

``` text
feat: add lead qualification agent
feat: add campaign dashboard
fix: resolve lead filtering issue
refactor: extract reusable lead table
chore: update dependencies
docs: document agent architecture
```

Do not commit:

``` text
.env
API keys
passwords
tokens
private credentials
large generated files
```

------------------------------------------------------------------------

# 41. Feature Development Workflow

Every new feature SHOULD follow:

``` text
1. Understand requirement
2. Define data model if needed
3. Define API contract
4. Implement backend schema
5. Implement repository
6. Implement service
7. Implement agent/integration if needed
8. Add API route
9. Add frontend types
10. Add API client function
11. Build reusable components
12. Build page/feature
13. Add loading/error/empty states
14. Test
15. Run lint/type checks
16. Verify production build
```

------------------------------------------------------------------------

# 42. API Contract First

Before connecting frontend and backend, define:

``` text
Request
Response
Errors
Authentication
Loading state
Pagination
Filtering
```

Example:

``` text
POST /api/v1/agents/qualification/run

Request:
{
  "lead_ids": ["1", "2", "3"]
}

Response:
{
  "run_id": "run_123",
  "status": "queued"
}
```

------------------------------------------------------------------------

# 43. Frontend State Rules

Use the simplest appropriate state solution.

Do not introduce a global state library for local component state.

Prefer:

``` text
useState
useReducer
server state/data-fetching solution
```

Use global state only when multiple distant parts of the application
genuinely need shared client state.

------------------------------------------------------------------------

# 44. File Naming

React components:

``` text
PascalCase.tsx
```

Examples:

``` text
LeadTable.tsx
LeadCard.tsx
AgentStatus.tsx
```

Hooks:

``` text
useSomething.ts
```

Examples:

``` text
useLeads.ts
useCampaigns.ts
```

Python modules:

``` text
snake_case.py
```

Examples:

``` text
lead_service.py
qualification_agent.py
```

------------------------------------------------------------------------

# 45. No Giant Files

Avoid files larger than necessary.

If a component or service becomes difficult to understand, split it by
responsibility.

Do not split code artificially into dozens of meaningless files.

The goal is clarity, not maximum file count.

------------------------------------------------------------------------

# 46. No Hard-Coded Business Logic in UI

Bad:

``` ts
if (score > 80) {
  // business decision
}
```

when the scoring rules belong to backend/domain logic.

The frontend should display backend-provided business decisions.

------------------------------------------------------------------------

# 47. Analytics

Track:

``` text
Total leads
Qualified leads
Qualification rate
Contacted leads
Reply rate
Positive reply rate
Meetings booked
Conversion rate
Campaign performance
Agent success/failure rate
```

Analytics MUST be based on persisted data rather than UI-only
calculations where historical accuracy matters.

------------------------------------------------------------------------

# 48. AI Agent Observability

The UI SHOULD expose useful agent state:

``` text
Queued
Running
Completed
Failed
Cancelled
```

For long-running agents, show progress where technically reliable.

Example:

``` text
Discovery Agent
████████████░░░░ 72%
Finding leads...
```

Do not fake progress percentages.

------------------------------------------------------------------------

# 49. Accessibility

The frontend MUST support:

-   Keyboard navigation
-   Visible focus states
-   Semantic HTML
-   Accessible labels
-   Sufficient contrast
-   Screen-reader-friendly controls
-   Proper button semantics

Do not use clickable `<div>` elements where a `<button>` is appropriate.

------------------------------------------------------------------------

# 50. Responsive Design

The UI MUST work across:

``` text
Mobile
Tablet
Desktop
Large desktop
```

Do not design only for a single desktop resolution.

------------------------------------------------------------------------

# 51. Performance

Frontend:

-   Prefer Server Components
-   Avoid unnecessary client JavaScript
-   Lazy-load heavy UI where appropriate
-   Paginate large lead datasets
-   Avoid rendering thousands of leads simultaneously

Backend:

-   Use async I/O where appropriate
-   Paginate database queries
-   Avoid N+1 queries
-   Cache expensive operations where useful
-   Move long-running work to background jobs

AI:

-   Avoid unnecessary model calls
-   Cache reusable research where appropriate
-   Use structured output
-   Keep prompts focused

------------------------------------------------------------------------

# 52. Integration Boundaries

External services MUST be isolated behind integration modules.

Example:

``` text
integrations/
├── llm/
├── email/
├── search/
└── crm/
```

The rest of the application should not depend directly on a specific
vendor implementation.

This allows providers to be replaced later.

------------------------------------------------------------------------

# 53. Vendor-Agnostic AI Layer

Do not spread provider-specific AI SDK calls throughout the application.

Prefer:

``` text
Agent
 ↓
LLM Service Interface
 ↓
Provider Adapter
 ↓
LLM Provider
```

This makes the AI layer replaceable.

------------------------------------------------------------------------

# 54. Database Independence

Business logic should not depend heavily on ORM-specific behavior.

Keep persistence concerns inside repositories.

------------------------------------------------------------------------

# 55. Documentation

Maintain:

``` text
README.md
docs/architecture.md
docs/api.md
docs/agents.md
docs/deployment.md
```

Whenever architecture changes significantly, update the relevant
documentation.

------------------------------------------------------------------------

# 56. Definition of Done

A feature is NOT complete until:

``` text
[ ] Requirement implemented
[ ] Backend implemented
[ ] API contract defined
[ ] Frontend integrated
[ ] Types added
[ ] Loading state added
[ ] Error state added
[ ] Empty state added
[ ] Validation added
[ ] Security reviewed
[ ] Tests added where appropriate
[ ] Lint passes
[ ] Type checks pass
[ ] Production build passes
[ ] No secrets committed
[ ] Documentation updated if needed
```

------------------------------------------------------------------------

# 57. Golden Rules for AI Coding Agents

When an AI coding agent modifies this repository:

1.  Read `constitution.md` before making architectural changes.
2.  Do not rewrite working code unnecessarily.
3.  Inspect existing patterns before creating new ones.
4.  Reuse existing components and utilities.
5.  Do not create duplicate API clients.
6.  Do not create duplicate UI primitives.
7.  Do not bypass the service/repository architecture.
8.  Do not put secrets in source code.
9.  Do not fabricate lead data.
10. Do not fabricate AI research facts.
11. Preserve existing API contracts unless intentionally changing them.
12. Update types whenever API contracts change.
13. Add error/loading/empty states to new asynchronous UI.
14. Keep components small and focused.
15. Keep AI agents independently testable.
16. Prefer explicit, readable code over clever abstractions.
17. Do not introduce a new dependency unless it solves a real problem.
18. Do not remove existing functionality without a clear requirement.
19. Run validation after meaningful changes.
20. Treat this constitution as the project's architectural contract.

------------------------------------------------------------------------

# 58. Final Architecture

The final system should conceptually look like:

``` text
                    ┌──────────────────────┐
                    │      Next.js 16      │
                    │      Frontend        │
                    └──────────┬───────────┘
                               │
                         REST / JSON
                               │
                    ┌──────────▼───────────┐
                    │       FastAPI        │
                    │      API Layer       │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │      Services        │
                    │   Business Logic     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
      ┌───────▼──────┐ ┌──────▼───────┐ ┌──────▼──────┐
      │ AI Agents    │ │ Integrations │ │ Repositories│
      │              │ │              │ │             │
      │ Discovery    │ │ LLM          │ │ Leads       │
      │ Enrichment   │ │ Search       │ │ Campaigns   │
      │ Research     │ │ Email        │ │ Users       │
      │ Qualification│ │ CRM          │ │ Agent Runs  │
      │ Personalize  │ │              │ │             │
      └───────┬──────┘ └──────────────┘ └──────┬──────┘
              │                                 │
              │                                 ▼
              │                          ┌─────────────┐
              │                          │  Database   │
              │                          └─────────────┘
              │
              ▼
       ┌──────────────┐
       │ AI Providers │
       └──────────────┘
```

------------------------------------------------------------------------

# 59. Constitution Priority

When there is a conflict between a quick implementation and the
architecture defined here, prefer the architecture.

The application should remain:

``` text
Modular
Typed
Secure
Testable
Observable
Reusable
Scalable
Maintainable
```

This constitution is the default engineering contract for the AI Lead
Generation Agent.
