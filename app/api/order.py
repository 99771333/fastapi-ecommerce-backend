
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.cart import Cart
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import OrderCreate

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/checkout")
def checkout(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart or not cart.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = Decimal("0.00")
    order_items_data = []

    for cart_item in cart.items:
        product = (
            db.query(Product)
            .filter(Product.id == cart_item.product_id)
            .with_for_update()
            .first()
        )

        if not product or not product.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Product {cart_item.product_id} is unavailable"
            )

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}"
            )

        price = Decimal(str(product.price))
        item_total = price * cart_item.quantity
        total_amount += item_total

        order_items_data.append({
    "product": product,
    "product_name": product.name,
    "quantity": cart_item.quantity,
    "price": price
    })

    try:
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            shipping_address=order_data.shipping_address,
            status="pending"
        )

        db.add(order)
        db.flush()

        for item in order_items_data:
            product = item["product"]

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=item["product_name"],
                quantity=item["quantity"],
                price=item["price"]
           )
            db.add(order_item)

            product.stock -= item["quantity"]

        cart.items.clear()

        db.commit()
        db.refresh(order)

        return {
            "message": "Order placed successfully",
            "order_id": order.id,
            "total_amount": str(order.total_amount),
            "status": order.status
        }

    except Exception:
        db.rollback()
        raise


@router.get("/")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return [
        {
            "order_id": order.id,
            "total_amount": str(order.total_amount),
            "shipping_address": order.shipping_address,
            "status": order.status,
            "created_at": order.created_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": str(item.price)
                }
                for item in order.items
            ]
        }
        for order in orders
    ]
