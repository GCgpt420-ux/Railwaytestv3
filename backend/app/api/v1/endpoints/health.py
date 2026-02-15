from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def health_check():
    """
    Health check endpoint
    
    GET /api/v1/health/
    Returns: {"status": "ok"}
    """
    return {"status": "ok"}
