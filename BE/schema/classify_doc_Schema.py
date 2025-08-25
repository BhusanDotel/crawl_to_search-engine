from pydantic import BaseModel
from typing import Dict

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    predicted_category: str
    probabilities: Dict[str, float]
    