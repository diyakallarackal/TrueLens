from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.services.detectors.base import SignalMetric


class SampledFrameInfo(BaseModel):
    frame_index: int
    timestamp_sec: float
    frame_base64: str
    ela_base64: Optional[str] = None
    observations: str


class VideoAnalysisResult(BaseModel):
    analysis_id: str
    media_type: str = "video"
    timestamp: str
    filename: str
    file_size: int
    duration: float
    format: str
    verdict: str  # "Likely Authentic", "Likely Manipulated", "Inconclusive"
    risk_score: int = Field(..., ge=0, le=100)
    assessment_confidence: int = Field(..., ge=0, le=100)
    summary_explanation: str
    signals: List[SignalMetric]
    sampled_frames: List[SampledFrameInfo] = Field(default_factory=list)
    technical_metrics: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    explanation: Optional[Dict[str, Any]] = None
    recommendation: str
    disclaimer: str


class VideoDetector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    async def analyze(self, video_bytes: bytes, filename: str) -> VideoAnalysisResult:
        pass
