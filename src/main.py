from fastapi import Depends, FastAPI

from src.dto.predict_in_dto import PredictInDto
from src.services.nlp_service import NlpService

app = FastAPI()


@app.post("/predict")
def predict(predict_dto: PredictInDto, nlp_service: NlpService = Depends(NlpService)):
    result = nlp_service.predict(predict_dto=predict_dto)
    return result
