from fastapi import APIRouter
from app.api.routes import health, products, analytics, reviews, recommendations

api_router = APIRouter()

# Register sub-routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(products.router, tags=["Products"])
api_router.include_router(analytics.router, tags=["Price Analytics"])
api_router.include_router(reviews.router, tags=["Reviews RAG"])
api_router.include_router(recommendations.router, tags=["Recommendations"])


