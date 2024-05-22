from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Define Globel exceptions
# TODO: partition out repeated exceptions from routes


def global_handler(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(req: Request, exec: RequestValidationError):
        """
        Override the default 422 with 400
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": exec.errors()}),
        )
