from fastapi import APIRouter

from app.api.v1 import agents, analytics, auth, campaigns, leads, outreach, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(leads.router)
api_router.include_router(campaigns.router)
api_router.include_router(agents.router)
api_router.include_router(outreach.router)
api_router.include_router(analytics.router)
