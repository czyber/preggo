from fastapi import APIRouter

from app.api.endpoints import items, logs, auth, pregnancies, family, posts, milestones, health

api_router = APIRouter()
api_router.include_router(items.router)
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(pregnancies.router, prefix="/pregnancies", tags=["pregnancies"])
api_router.include_router(family.router, prefix="/family", tags=["family"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(health.router, prefix="/health", tags=["health"])