from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class SignalMetric(BaseModel):
    id: str
    name: str
    score: float = Field(..., ge=0.0, le=100.0, description="0 is clean/authentic, 100 is highly anomalous/manipulated")
    severity: str = Field(..., description="Low, Medium, High, or Critical")
    confidence: float = Field(..., ge=0.0, le=100.0)
    description: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class ImageDimensions(BaseModel):
    width: int
    height: int
    aspect_ratio: str


class AnalysisResult(BaseModel):
    analysis_id: str
    media_type: str = "image"
    timestamp: str
    filename: str
    file_size: int
    dimensions: ImageDimensions
    format: str
    verdict: str  # "Likely Authentic", "Likely Manipulated", "Inconclusive"
    risk_score: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    summary_explanation: str
    signals: List[SignalMetric]
    ela_heatmap_base64: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    explanation: Optional[Dict[str, Any]] = None
    recommendation: str
    disclaimer: str


class ImageDetector(ABC):
    """
    Abstract interface for image detection engines.
    Allows modular swapping of real forensic engines and external model adapters.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    async def analyze(self, image_bytes: bytes, filename: str) -> AnalysisResult:
        pass
