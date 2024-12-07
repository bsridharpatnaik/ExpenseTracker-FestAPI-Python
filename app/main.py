from fastapi import FastAPI
from app.models import Base
from app.database import engine
from app.routers import auth_router, file_router, transaction_router
from app.routers import dashboard_router

app = FastAPI()

Base.metadata.create_all(bind=engine, checkfirst=True)

app.include_router(auth_router)
app.include_router(file_router)
app.include_router(transaction_router)
app.include_router(dashboard_router)