from fastapi import APIRouter, HTTPException
from sqlmodel import select

from apps.forms import ProductForm
from apps.models import Product, SessionDep

router = APIRouter(tags=["product"])


@router.get("/product/list")
async def product_list(session: SessionDep):
    products = session.exec(select(Product)).all()
    return products


@router.get("/product/{product_id}")
async def product_detail(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product topilmadi")
    return product


@router.patch("/product/{product_id}/update")
async def product_partial_update(product_id: int, product_form: ProductForm, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product topilmadi")

    data = product_form.model_dump(exclude_unset=True)  # faqat yuborilgan maydonlar
    for key, value in data.items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return {"message": "Success partial update!", "status": 200, "data": product}


@router.delete("/product/{product_id}/delete")
async def product_delete(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product topilmadi")
    session.delete(product)
    session.commit()
    return {"message": "Success delete!", "status": 200}
