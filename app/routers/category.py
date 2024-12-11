from slugify import slugify
from app.schemas import CreateCategory
from sqlalchemy import insert, select, update
from app.models import *
from typing import Annotated
from app.backend.db_depends import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.auth import get_current_user

router = APIRouter(prefix="/category", tags=["category"])


@router.get("/all_categories")
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active == True))
    return categories.all()


@router.post("/create")
async def create_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_category: CreateCategory,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get("is_admin"):
        # Убедитесь, что parent_id равен None, если нет родительской категории
        parent_id = create_category.parent_id if create_category.parent_id and await db.get(Category, create_category.parent_id) else None

        await db.execute(
            insert(Category).values(
                name=create_category.name,
                parent_id=parent_id,
                slug=slugify(create_category.name),
            )
        )
        await db.commit()
        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be admin user for this",
        )


@router.put("/update_category/{category_id}")
async def update_category(
    category_id: int,
    update_category: CreateCategory,
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get("is_admin"):
        # Retrieve the existing category
        category = await db.scalar(select(Category).where(Category.id == category_id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        # Ensure that the parent_id is valid if provided
        if update_category.parent_id and not await db.get(Category, update_category.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent category ID",
            )

        # Update the category
        await db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(
                name=update_category.name,
                slug=slugify(update_category.name),
                parent_id=update_category.parent_id if update_category.parent_id else None,
            )
        )

        await db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "Category update is successful",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin user for this",
        )


@router.delete("/delete")
async def delete_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int,
    get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get("is_admin"):
        category = await db.scalar(select(Category).where(Category.id == category_id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no category found",
            )
        await db.execute(
            update(Category).where(Category.id ==
                                   category_id).values(is_active=False)
        )
        await db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "Category delete is successful",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be admin user for this",
        )
