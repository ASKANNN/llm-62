from fastapi import APIRouter, HTTPException, Query

from loggers.logger_req import logger
from models.travel_model import TravelRequestDTO, TravelResponse
from services.travel_service import get_country_info, get_exchange_rate, get_weather

router = APIRouter(prefix="/travel")


@router.post("/info", response_model=TravelResponse, response_model_exclude_none=True)
async def post_travel_info(travel_dto: TravelRequestDTO):
    logger.debug(f"Travel info requested: {travel_dto.country_from} -> {travel_dto.country_to}")

    response_data = {
        "country_from": travel_dto.country_from,
        "country_to": travel_dto.country_to,
    }

    if not travel_dto.iscapital and not travel_dto.isweather and not travel_dto.iscurrency:
        return TravelResponse(**response_data)

    info_to = await get_country_info(travel_dto.country_to)
    if not info_to:
        raise HTTPException(status_code=404, detail=f"Country not found: {travel_dto.country_to}")

    if travel_dto.iscapital:
        response_data["capital_to"] = info_to["capital"]

    if travel_dto.isweather:
        weather = await get_weather(info_to["capital"])
        if not weather:
            raise HTTPException(status_code=404, detail="Weather not found")
        response_data["weather"] = weather

    if travel_dto.iscurrency:
        info_from = await get_country_info(travel_dto.country_from)
        if not info_from:
            raise HTTPException(status_code=404, detail=f"Country not found: {travel_dto.country_from}")

        rate = await get_exchange_rate(info_from["currency_code"], info_to["currency_code"])
        if rate is None:
            raise HTTPException(status_code=404, detail="Exchange rate not found")

        response_data["currency_code_from"] = info_from["currency_code"]
        response_data["currency_code_to"] = info_to["currency_code"]
        response_data["currency_name_from"] = info_from["currency_name"]
        response_data["currency_name_to"] = info_to["currency_name"]
        response_data["exchange_rate"] = rate

    return TravelResponse(**response_data)


@router.get("/info", response_model=TravelResponse)
async def get_travel_info(
        country_from: str = Query(...),
        country_to: str = Query(...),
):
    logger.debug(f"Travel info requested (GET): {country_from} -> {country_to}")

    info_from = await get_country_info(country_from)
    if not info_from:
        raise HTTPException(status_code=404, detail=f"Country not found: {country_from}")

    info_to = await get_country_info(country_to)
    if not info_to:
        raise HTTPException(status_code=404, detail=f"Country not found: {country_to}")

    weather = await get_weather(info_to["capital"])
    if not weather:
        raise HTTPException(status_code=404, detail="Weather not found")

    rate = await get_exchange_rate(info_from["currency_code"], info_to["currency_code"])
    if rate is None:
        raise HTTPException(status_code=404, detail="Exchange rate not found")

    return TravelResponse(
        country_from=country_from,
        country_to=country_to,
        capital_to=info_to["capital"],
        weather=weather,
        currency_code_from=info_from["currency_code"],
        currency_code_to=info_to["currency_code"],
        currency_name_from=info_from["currency_name"],
        currency_name_to=info_to["currency_name"],
        exchange_rate=rate,
    )
