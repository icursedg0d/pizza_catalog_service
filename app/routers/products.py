from fastapi import Form
import uuid
from pathlib import Path
import shutil
from app.models import Product
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from app.schemas import CreateProduct
from slugify import slugify
from app.models import *
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


UPLOAD_FOLDER = "uploads"


@router.get("/")
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product).filter(Product.is_active == True)
    )
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There are no products"
        )
    return products.all()


@router.post("/create")
async def create_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: int = Form(...),
    file: UploadFile = File(...),
):
    if not get_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method",
        )

    # Генерируем уникальное имя для файла
    unique_filename = f"{uuid.uuid4()}-{file.filename}"
    file_location = Path(UPLOAD_FOLDER) / unique_filename
    file_location.parent.mkdir(parents=True, exist_ok=True)

    # Сохраняем файл
    with file_location.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    image_url = f"/static/{unique_filename}"

    # Добавляем продукт в базу данных
    await db.execute(
        insert(Product).values(
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            category_id=category,
            rating=0.0,
            slug=slugify(name),
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.get("/{category_slug}")
async def product_by_category(
    db: Annotated[AsyncSession, Depends(get_db)], category_slug: str
):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    subcategories = await db.scalars(
        select(Category).where(Category.parent_id == category.id)
    )
    categories_and_subcategories = [
        category.id] + [i.id for i in subcategories.all()]
    products = await db.scalars(
        select(Product).where(
            Product.category_id.in_(categories_and_subcategories),
            Product.is_active == True,
        )
    )
    return products.all()


@router.get("/detail/{product_slug}")
async def product_detail(
    db: Annotated[AsyncSession, Depends(get_db)], product_slug: str
):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.put("/detail/{product_slug}")
async def update_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    product_slug: str,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: int = Form(...),
    file: UploadFile = File(None),
):
    product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if not get_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method",
        )

    new_image_url = product_update.image_url
    if file:
        unique_filename = f"{uuid.uuid4()}-{file.filename}"
        file_location = Path(UPLOAD_FOLDER) / unique_filename
        file_location.parent.mkdir(parents=True, exist_ok=True)
        with file_location.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        new_image_url = f"/static/{unique_filename}"

    await db.execute(
        update(Product)
        .where(Product.slug == product_slug)
        .values(
            name=name,
            description=description,
            price=price,
            image_url=new_image_url,
            category_id=category,
            slug=slugify(name),
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Product update is successful"}


@router.delete("/delete/{product_id}")
async def delete_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: int,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    product_delete = await db.scalar(select(Product).where(Product.id == product_id))
    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if not get_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to use this method",
        )

    await db.execute(
        update(Product).where(Product.id == product_id).values(is_active=False)
    )
    await db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Product delete is successful"}
