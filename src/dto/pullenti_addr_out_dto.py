from pydantic import BaseModel


class PullentiAddrOutDto(BaseModel):
    region: str | None
    city: str | None
    street: str | None
    house: str | None
    building: str | None
    corpus: str | None
    zip: str | None
    flat: str | None
