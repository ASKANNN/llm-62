import json

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from loggers.logger_req import logger
from routers.travel_routes import router

app = FastAPI()


@app.middleware("http")
async def logging_middleware(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


@app.middleware("http")
async def travel_response_validation_middleware(request, call_next):
    if request.url.path != "/travel/info" or request.method != "POST":
        return await call_next(request)

    body_bytes = await request.body()
    try:
        flags = json.loads(body_bytes)
    except json.JSONDecodeError:
        flags = {}

    response = await call_next(request)
    if response.status_code != 200:
        return response

    response_bytes = b"".join([chunk async for chunk in response.body_iterator])
    data = json.loads(response_bytes)

    optional_fields = {
        "iscapital": ["capital_to"],
        "isweather": ["weather"],
        "iscurrency": ["currency_code_from", "currency_code_to", "currency_name_from",
                        "currency_name_to", "exchange_rate"],
    }

    errors = []
    for flag_name, fields in optional_fields.items():
        flag_value = flags.get(flag_name)
        for field in fields:
            present = field in data
            if flag_value and not present:
                errors.append(f"{field} is required when {flag_name}=True")
            if not flag_value and present:
                errors.append(f"{field} must not exist when {flag_name}=False")

    if errors:
        return JSONResponse(status_code=500, content={"detail": "Response validation failed", "errors": errors})

    return JSONResponse(content=data, status_code=response.status_code)


@app.exception_handler(RequestValidationError)
def request_validation_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )


app.include_router(router)
