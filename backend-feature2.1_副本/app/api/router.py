from fastapi import APIRouter

from app.api.routes import agent, meta, narration_history


api_router = APIRouter()

api_router.include_router(agent.router)
api_router.include_router(meta.router)
api_router.include_router(narration_history.router)