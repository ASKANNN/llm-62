from pydantic import BaseModel, Field


class TravelRequestDTO(BaseModel):
    country_from: str = Field(..., min_length=1)
    country_to: str = Field(..., min_length=1)
    iscapital: bool
    isweather: bool
    iscurrency: bool


class TravelResponse(BaseModel):
    country_from: str
    country_to: str
    capital_to: str | None = None
    weather: str | None = None
    currency_code_from: str | None = Field(default=None, min_length=3, max_length=3)
    currency_code_to: str | None = Field(default=None, min_length=3, max_length=3)
    currency_name_from: str | None = None
    currency_name_to: str | None = None
    exchange_rate: float | None = None
