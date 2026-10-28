from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.product import router as product_router
from app.api.cart import router as cart_router
from app.api.order import router as order_router

app = FastAPI(title="E-Commerce API")

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)

@app.get("/")
def home():
    return {"message": "E-Commerce API is running"}