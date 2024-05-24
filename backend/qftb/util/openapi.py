from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from ..config import settings

SHOW_DOCS_ENVIRONMENT = ("local")  # explicit list of allowed envs\


def set_docs_url() -> str | None:
    if settings.ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
        return None  # set url for docs as null
    return "/openapi.json"


def custom_openapi(app: FastAPI) -> None:
    def replace_http_422():
        if app.openapi_schema:
            return app.openapi_schema
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes
        )
        for _, method_item in app.openapi_schema.get("paths").items():
            for _, param in method_item.items():
                responses = param.get("responses")
                # remove 422 response, also can remove other status code
                if "422" in responses:
                    del responses["422"]
        return app.openapi_schema
    app.openapi = replace_http_422
