from fastapi import APIRouter
from app.api.routes import health, products

api_router = APIRouter()

# Register sub-routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(products.router, tags=["Products"])
