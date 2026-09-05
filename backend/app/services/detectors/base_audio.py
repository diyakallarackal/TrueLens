from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.services.detectors.base import SignalMetric


class AudioAnalysisResult(BaseModel):
    analysis_id: str
    media_type: str = "audio"
    timestamp: str
    filename: str
    file_size: int
    duration: float
    format: str
    verdict: str  # "Likely Authentic", "Likely Manipulated", "Inconclusive"
    risk_score: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    summary_explanation: str
    signals: List[SignalMetric]
    technical_metrics: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    explanation: Optional[Dict[str, Any]] = None
    spectrogram_base64: Optional[str] = None
    recommendation: str
    disclaimer: str


class AudioDetector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    async def analyze(self, audio_bytes: bytes, filename: str) -> AudioAnalysisResult:
        pass
