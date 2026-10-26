from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate
from fastapi import APIRouter

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

@router.post("/items")
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check whether product exists
    product = db.query(Product).filter(
        Product.id == item_data.product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or inactive"
        )

    # 2. Check stock availability
    if item_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    # 3. Find user's cart or create one
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()

    # 4. Check whether product is already in cart
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id
    ).first()

    if cart_item:
        new_quantity = cart_item.quantity + item_data.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock for requested quantity"
            )

        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=item_data.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Product added to cart successfully",
        "cart_item_id": cart_item.id,
        "product_id": product.id,
        "quantity": cart_item.quantity
    }

@router.get("/")
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        return {
            "items": [],
            "total_price": 0
        }

    items = []
    total_price = 0

    for cart_item in cart.items:
        product = cart_item.product

        item_total = float(product.price) * cart_item.quantity
        total_price += item_total

        items.append({
            "cart_item_id": cart_item.id,
            "product_id": product.id,
            "product_name": product.name,
            "price": float(product.price),
            "quantity": cart_item.quantity,
            "item_total": round(item_total, 2)
        })

    return {
        "cart_id": cart.id,
        "items": items,
        "total_price": round(total_price, 2)
    }

@router.put("/items/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = (
        db.query(CartItem)
        .join(Cart)
        .filter(
            CartItem.id == cart_item_id,
            Cart.user_id == current_user.id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = cart_item.product

    if not product.is_active:
        raise HTTPException(
            status_code=400,
            detail="Product is inactive"
        )

    if item_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    cart_item.quantity = item_data.quantity

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart quantity updated successfully",
        "cart_item_id": cart_item.id,
        "product_id": product.id,
        "quantity": cart_item.quantity
    }

@router.delete("/items/{cart_item_id}")
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = (
        db.query(CartItem)
        .join(Cart)
        .filter(
            CartItem.id == cart_item_id,
            Cart.user_id == current_user.id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Product removed from cart successfully"
    }