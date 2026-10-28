
from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    # # Checkout ke waqt shipping address required hai
    shipping_address: str = Field(min_length=5, max_length=300)
