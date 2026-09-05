import os
from typing import Optional
from app.services.detectors.base import ImageDetector, AnalysisResult


class ExternalDetector(ImageDetector):
    """
    Modular External Detector interface for third-party AI image APIs (e.g. Hive AI, Sightengine).
    Checks dynamically for API key in environment variables (TRUELENS_EXTERNAL_API_KEY).
    If unconfigured or key is missing, correctly reports `is_available = False` 
    and raises an error if invoked, ensuring core forensic analysis operates safely without faking.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("TRUELENS_EXTERNAL_API_KEY")

    @property
    def name(self) -> str:
        return "External API Detector (Modular)"

    @property
    def is_available(self) -> bool:
        return bool(self._api_key and len(self._api_key.strip()) > 0)

    async def analyze(self, image_bytes: bytes, filename: str) -> AnalysisResult:
        if not self.is_available:
            raise RuntimeError(
                "ExternalDetector is unconfigured. Missing TRUELENS_EXTERNAL_API_KEY environment variable. "
                "Core RealImageAnalyzer will process the forensic analysis."
            )
        # Real HTTP call implementation would go here when credentials exist
        raise NotImplementedError("External API call requested without configured remote provider endpoint.")
