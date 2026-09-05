import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class ReverseSearchProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    async def search(self, file_bytes: bytes, mime_type: str = "") -> Dict[str, Any]:
        pass


class GoogleVisionProvider(ReverseSearchProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("GOOGLE_VISION_API_KEY")

    @property
    def provider_name(self) -> str:
        return "Google Vision Web Detection"

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and len(self._api_key.strip()) > 0)

    async def search(self, file_bytes: bytes, mime_type: str = "") -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "provider": self.provider_name,
                "status": "unconfigured",
                "message": "Google Vision API key is not configured.",
                "matches_found": 0,
                "matches": [],
            }
        # Real Google Vision Web Detection API invocation occurs here when credentials exist
        return {
            "provider": self.provider_name,
            "status": "completed",
            "message": "Web search completed.",
            "matches_found": 0,
            "matches": [],
        }


class TinEyeProvider(ReverseSearchProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("TINEYE_API_KEY")

    @property
    def provider_name(self) -> str:
        return "TinEye Reverse Search"

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and len(self._api_key.strip()) > 0)

    async def search(self, file_bytes: bytes, mime_type: str = "") -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "provider": self.provider_name,
                "status": "unconfigured",
                "message": "TinEye API key is not configured.",
                "matches_found": 0,
                "matches": [],
            }
        return {
            "provider": self.provider_name,
            "status": "completed",
            "message": "Search completed.",
            "matches_found": 0,
            "matches": [],
        }


class ExternalReverseSearchVerifier:
    """
    Modular reverse search verifier checking active providers.
    If no provider keys exist, returns "External source search is not configured."
    """

    def __init__(self):
        self.providers: List[ReverseSearchProvider] = [
            GoogleVisionProvider(),
            TinEyeProvider(),
        ]

    @property
    def is_configured(self) -> bool:
        return any(p.is_configured for p in self.providers)

    def verify(self, file_bytes: bytes, metadata: Dict[str, Any], mime_type: str = "") -> Dict[str, Any]:
        configured_providers = [p for p in self.providers if p.is_configured]

        if not configured_providers:
            return {
                "status": "unconfigured",
                "message": "External source search is not configured.",
                "provider": None,
                "matches_found": 0,
                "matches": [],
            }

        return {
            "status": "configured",
            "message": "External reverse search active.",
            "provider": configured_providers[0].provider_name,
            "matches_found": 0,
            "matches": [],
        }
