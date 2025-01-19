from fastapi import APIRouter
from app.api.endpoints.ai.gen_text import router as gen_text_router
from app.api.endpoints.ai.gen_text_together import router as gen_text_together_router
from app.api.endpoints.ai.gen_image import router as gen_image_router
router = APIRouter()

router.include_router(gen_text_router, tags=["ai"])
router.include_router(gen_text_together_router, tags=["ai"])
router.include_router(gen_image_router, tags=["ai"])