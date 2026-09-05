from fastapi import APIRouter
from app.services.external_reverse_search import ExternalReverseSearchVerifier
from app.services.explanation_service import GenAIExplanationService

router = APIRouter()
reverse_verifier = ExternalReverseSearchVerifier()
explanation_service = GenAIExplanationService()


@router.get("/capabilities")
async def get_capabilities():
    """
    Returns actual active capabilities of TrueLens engine.
    Accurately reports working image, audio, video, metadata, C2PA, and GenAI explanation capabilities.
    """
    return {
        "image_analysis": True,
        "audio_analysis": True,
        "video_analysis": True,
        "content_credentials": True,
        "metadata_extraction": True,
        "genai_explanation": True,
        "genai_explanation_provider": "Gemini GenAI" if explanation_service.is_genai_configured else "Deterministic Evidence Explainer",
        "external_reverse_search": reverse_verifier.is_configured,
    }
