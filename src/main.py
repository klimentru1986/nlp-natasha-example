from fastapi import Depends, FastAPI

from src.dto.predict_in_dto import PredictInDto
from src.services.nlp_service import NlpService
from src.services.nlp_pullenti import NlpPullenti

app = FastAPI()


@app.post("/predict/natasha")
def predict(predict_dto: PredictInDto, nlp_service: NlpService = Depends(NlpService)):
    result = nlp_service.predict(predict_dto=predict_dto)
    return result


@app.post("/predict/pullenti")
def predict(predict_dto: PredictInDto, nlp_service: NlpPullenti = Depends(NlpPullenti)):
    result = nlp_service.predict(predict_dto=predict_dto)
    return result
