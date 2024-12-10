from slugify import slugify
from app.schemas import CreateCart
from sqlalchemy import insert, select, update, delete
from app.models import *
from typing import Annotated
from app.backend.db_depends import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/update")
async def update_cart(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_cart: CreateCart,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    # Проверка существования продукта
    product = await db.scalar(select(Product).where(Product.id == create_cart.product_id))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Проверяем, есть ли такой товар с указанным радиусом в корзине пользователя
    cart_item = await db.scalar(
        select(Cart).where(
            Cart.user_id == get_user.get("user_id"),
            Cart.product_id == create_cart.product_id,
            Cart.radius == create_cart.radius
        )
    )

    if not cart_item:
        # Если товара нет в корзине, а запрос на уменьшение, возвращаем ошибку
        if create_cart.quantity == "-":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot decrease quantity. Item not in cart."
            )
        # Если товара нет, добавляем его в корзину с начальным количеством 1
        await db.execute(
            insert(Cart).values(
                user_id=get_user.get("user_id"),
                product_id=create_cart.product_id,
                radius=create_cart.radius
            )
        )
    else:
        # Если товар найден, изменяем его количество
        new_quantity = cart_item.quantity + \
            (1 if create_cart.quantity == "+" else -1)

        if new_quantity < 1:
            await db.execute(
                delete(Cart).where(Cart.id == cart_item.id)
            )
        else:
            await db.execute(
                update(Cart)
                .where(Cart.id == cart_item.id)
                .values(quantity=new_quantity)
            )
    await db.commit()
    return {"status_code": status.HTTP_200_OK, "message": "Cart updated successfully"}


@router.get("/get")
async def get_cart(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
):
    # Получаем корзину пользователя
    cart_items = await db.scalars(
        select(Cart).where(Cart.user_id == get_user.get("user_id"))
    )

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )

    result = []
    for item in cart_items:
        product = await db.scalar(select(Product).where(Product.id == item.product_id))
        if not product:
            continue
        result.append({
            "product_id": item.product_id,
            "product_name": product.name,
            "product_price": product.price,
            "radius": item.radius,
            "quantity": item.quantity,
            "total_price": product.price * item.quantity,
            "image_url": product.image_url,
        })

    return {"status_code": status.HTTP_200_OK, "cart": result}


@router.delete("/delete/{product_id}/{radius}")
async def delete_product_from_cart(
    product_id: int,
    radius: float,
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
):

    cart_item = await db.scalar(
        select(Cart).where(
            Cart.user_id == get_user.get("user_id"),
            Cart.product_id == product_id,
            Cart.radius == radius
        )
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )

    await db.execute(
        delete(Cart).where(
            Cart.id == cart_item.id
        )
    )
    await db.commit()

    return {"status_code": status.HTTP_200_OK, "message": "Product removed from cart"}