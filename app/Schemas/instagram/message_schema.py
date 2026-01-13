# app/Schemas/instagram/analyze_output.py
from pydantic import BaseModel
from typing import Optional


class AnalyzeMessageOutput(BaseModel):
    brand_intent: Optional[str] = ""
    pricing_mentioned: Optional[bool] = False
    negotiation_stage: Optional[str] = ""
    negotiation_strategy: Optional[str] = ""
