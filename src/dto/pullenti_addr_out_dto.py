from pydantic import BaseModel


class PullentiAddrOutDto(BaseModel):
    geo: str | None
    street: str | None
    house: str | None
    zip: str | None
    flat: str | None
