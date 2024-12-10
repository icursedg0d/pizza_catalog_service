from pydantic import BaseModel


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    category: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None


class CreateCart(BaseModel):
    product_id: int
    radius: float
    quantity: str
