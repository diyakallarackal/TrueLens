from fastapi import APIRouter
from app.services.detectors.real_analyzer import RealImageAnalyzer
from app.services.detectors.external import ExternalDetector

router = APIRouter()
real_detector = RealImageAnalyzer()
external_detector = ExternalDetector()


@router.get("/health")
async def health_check():
    """
    Health check endpoint returning engine status and detector module availability.
    """
    return {
        "status": "healthy",
        "service": "TrueLens Media Verification Platform API",
        "detectors": {
            "real_analyzer": {
                "name": real_detector.name,
                "available": real_detector.is_available,
                "type": "Primary Real Multi-Signal Forensics"
            },
            "external_detector": {
                "name": external_detector.name,
                "available": external_detector.is_available,
                "type": "Modular Remote API Adapter"
            }
        }
    }
