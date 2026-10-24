from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.product import router as product_router

app = FastAPI(title="E-Commerce API")

app.include_router(auth_router)
app.include_router(product_router)


@app.get("/")
def home():
    return {"message": "E-Commerce API is running"}