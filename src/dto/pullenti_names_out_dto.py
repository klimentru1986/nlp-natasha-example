from pydantic import BaseModel


from pydantic import BaseModel


class PullentiNamesOutDto(BaseModel):
    sex: str | None
    firstname: str | None
    lastname: str | None
    middlename: str | None
