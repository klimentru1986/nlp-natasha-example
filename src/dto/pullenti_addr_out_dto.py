from typing import TypedDict


class PullentiAddrOutDto(TypedDict):
    geo: str
    street: str
    house: str
    zip: str
    flat: str
