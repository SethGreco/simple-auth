from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .exceptions import global_handler
from .routers import admin, auth, health, users
from .util.openapi import custom_openapi, set_docs_url

# Comment out if you want to build from DDL file.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Example Title",
    description="Example Description",
    version="1.0.0",
    openapi_url=set_docs_url(),
)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(auth.router)

origins = [settings.CLIENT_BASE_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global Exceptions
global_handler(app)
# Custom /docs
custom_openapi(app)
