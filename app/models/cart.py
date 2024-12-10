from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from app.models import *


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    radius = Column(Float, index=True)
    quantity = Column(Integer, default=1)
    product = relationship("Product")
