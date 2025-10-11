"""
AuraQuant - Pydantic Schemas for AI/ML Services
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ChartPatternType(str, Enum):
    """
    Enum for common chart patterns.
    """
    HEAD_AND_SHOULDERS = "Head and Shoulders"
    DOUBLE_TOP = "Double Top"
    DOUBLE_BOTTOM = "Double Bottom"
    RISING_WEDGE = "Rising Wedge"
    FALLING_WEDGE = "Falling Wedge"
    TRIANGLE = "Triangle"
    UNKNOWN = "Unknown"

class ChartPatternDetection(BaseModel):
    """
    Represents a detected chart pattern.
    """
    pattern_type: ChartPatternType
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of the detection (0 to 1)")
    start_timestamp: int
    end_timestamp: int
    key_points: Optional[Dict[str, Any]] = Field(None, description="Coordinates or timestamps of key pattern points")
    recommended_action: str = Field(..., description="e.g., 'Potential bearish reversal', 'Continuation expected'")

class ModelInfo(BaseModel):
    """
    Represents metadata about a registered ML model from the model registry.
    """
    name: str
    version: str
    stage: str # e.g., 'Staging', 'Production', 'Archived'
    description: Optional[str] = None
    creation_timestamp: int
    last_updated_timestamp: int
    run_id: str