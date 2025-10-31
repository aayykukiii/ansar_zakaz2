from database.db import SessionLocal
from database.models import Category, Product, Order
from sqlalchemy import select, delete

async def add_category(name: str, description: str):
    async with SessionLocal() as session:
        c = Category(name=name, description=description)
        session.add(c)
        await session.commit()
        await session.refresh(c)
        return c

async def list_categories():
    async with SessionLocal() as session:
        res = await session.execute(select(Category))
        return res.scalars().all()

async def get_category_by_id(cid: int):
    async with SessionLocal() as session:
        res = await session.execute(select(Category).where(Category.id == cid))
        return res.scalars().first()

async def get_category_by_name(name: str):
    async with SessionLocal() as session:
        res = await session.execute(select(Category).where(Category.name == name))
        return res.scalars().first()

# ----- PRODUCTS -----
async def add_product(name, category_id, subcategory, country, size, price, description, photo):
    async with SessionLocal() as session:
        p = Product(
            name=name,
            category_id=category_id,
            subcategory=subcategory,
            country=country,
            size=size,
            price=price,
            description=description,
            photo=photo
        )
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p

async def list_products():
    async with SessionLocal() as session:
        res = await session.execute(select(Product))
        return res.scalars().all()

async def list_products_by_category_id(cat_id: int):
    async with SessionLocal() as session:
        res = await session.execute(select(Product).where(Product.category_id == cat_id))
        return res.scalars().all()

async def list_products_by_category_name(cat_name: str):
    async with SessionLocal() as session:
        res = await session.execute(
            select(Product).join(Category).where(Category.name == cat_name)
        )
        return res.scalars().all()

async def list_products_by_category_and_subcat(cat_name: str, subcat: str):
    async with SessionLocal() as session:
        res = await session.execute(
            select(Product).join(Category).where(Category.name == cat_name, Product.subcategory == subcat)
        )
        return res.scalars().all()

async def get_product_by_id(pid: int):
    async with SessionLocal() as session:
        res = await session.execute(select(Product).where(Product.id == pid))
        return res.scalars().first()

async def delete_product_by_id(pid: int):
    async with SessionLocal() as session:
        await session.execute(delete(Product).where(Product.id == pid))
        await session.commit()

# ----- ORDERS -----
async def add_order(customer_name, customer_phone, product_id, product_name, comment=None):
    async with SessionLocal() as session:
        o = Order(
            customer_name=customer_name,
            customer_phone=customer_phone,
            product_id=product_id,
            product_name=product_name,
            comment=comment,
            status="new"
        )
        session.add(o)
        await session.commit()
        await session.refresh(o)
        return o

async def list_orders():
    async with SessionLocal() as session:
        res = await session.execute(select(Order))
        return res.scalars().all()
