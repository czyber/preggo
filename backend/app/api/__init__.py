from fastapi import APIRouter

from app.api.endpoints import (
    items, logs, auth, pregnancies, family, posts, milestones, health, feed, baby_development,
    enhanced_reactions, threaded_comments
)

api_router = APIRouter()
api_router.include_router(items.router)
api_router.include_router(logs.router, tags=["logs"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(pregnancies.router, tags=["pregnancies"])
api_router.include_router(baby_development.router, prefix="/baby-development", tags=["baby-development"])
api_router.include_router(family.router, tags=["family"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(milestones.router,  tags=["milestones"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(feed.router, tags=["feed"])
api_router.include_router(enhanced_reactions.router, prefix="/api/v1", tags=["enhanced-reactions"])
api_router.include_router(threaded_comments.router, prefix="/api/v1", tags=["threaded-comments"])
