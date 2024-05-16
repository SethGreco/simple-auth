from fastapi import FastAPI
from api.database import engine, Base
from api.routers import users, admin, login
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    settings.CLIENT_BASE_URL
]

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
def health():
    return {"Status": "Healthy"}
