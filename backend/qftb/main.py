from fastapi import FastAPI
from qftb.database import engine, Base
from qftb.routers import users, admin, login
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from qftb.exceptions import global_handler
from qftb.config import settings

# Comment out if you want to build from DDL file.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Example Title",
    description="Example Description",
    version="1.0.0",
)

global_handler(app)

origins = [settings.CLIENT_BASE_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(login.router)


@app.get("/health")
async def health():
    return {"Status": "Healthy"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    for _, method_item in app.openapi_schema.get("paths").items():
        for _, param in method_item.items():
            responses = param.get("responses")
            # remove 422 response, also can remove other status code
            if "422" in responses:
                del responses["422"]
    return app.openapi_schema


app.openapi = custom_openapi
