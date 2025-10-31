from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)   # например "🛏️ Спальная мебель"
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    subcategory = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    size = Column(String(100), nullable=True)
    price = Column(String(80), nullable=True)
    description = Column(Text, nullable=True)
    photo = Column(String(400), nullable=True)

    category = relationship("Category", back_populates="products")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String(200))
    customer_phone = Column(String(100))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(String(50), default="new")
