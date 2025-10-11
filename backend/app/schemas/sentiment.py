"""
AuraQuant - Pydantic Schemas for the SentimentData Model
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# --- Base Schema ---
# Contains the core attributes of a sentiment data point.
class SentimentDataBase(BaseModel):
    symbol: str = Field(..., max_length=50)
    sentiment_score: float = Field(..., description="Numerical score from -1.0 (very negative) to 1.0 (very positive).")
    sentiment_label: str = Field(..., max_length=20, description="Categorical label (e.g., 'positive', 'negative', 'neutral').")
    source: str = Field(..., max_length=100, description="The source of the news (e.g., 'Reuters').")
    headline: str = Field(..., max_length=512, description="The headline of the news article.")
    timestamp: datetime = Field(..., description="The original publication timestamp of the article.")


# --- Create Schema ---
# This is the schema used by the SentimentStorageService to create a new record in the database.
class SentimentDataCreate(SentimentDataBase):
    pass


# --- Response Schema ---
# This schema represents a sentiment data point as it is returned from the API.
# It includes the database-generated ID.
class SentimentDataInDB(SentimentDataBase):
    id: int

    model_config = ConfigDict(from_attributes=True)