from fastapi import APIRouter

from app.api.endpoints import items, logs, auth, pregnancies, family, posts, milestones, health

api_router = APIRouter()
api_router.include_router(items.router)
api_router.include_router(logs.router, tags=["logs"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(pregnancies.router, tags=["pregnancies"])
api_router.include_router(family.router, tags=["family"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(milestones.router,  tags=["milestones"])
api_router.include_router(health.router, tags=["health"])
