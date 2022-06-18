from pydantic import BaseModel


class PredictInDto(BaseModel):
    text: str
