from dataclasses import asdict
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from domain import Customer, ItemClass
from application import RecordLoad, RecordExpense, GetPeriodTotals
from infrastructure import (
    SupabaseCustomerRepository,
    SupabaseItemClassRepository,
    SupabaseLoadRepository,
    SupabaseExpenseRepository,
)
from application import RecordLoad, RecordExpense, GetPeriodTotals, UpdateLoadStatus, MarkLoadPaid


app = FastAPI(title="Shoe Wash API")

# Dev-friendly for now -- tighten allow_origins once the dashboard has a real domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

customer_repo = SupabaseCustomerRepository()
item_class_repo = SupabaseItemClassRepository()
load_repo = SupabaseLoadRepository()
expense_repo = SupabaseExpenseRepository()

record_load = RecordLoad(load_repo, item_class_repo)
record_expense = RecordExpense(expense_repo)
get_period_totals = GetPeriodTotals(load_repo, expense_repo)

update_load_status = UpdateLoadStatus(load_repo)
mark_load_paid = MarkLoadPaid(load_repo)


class LoadCreate(BaseModel):
    customer_name: str
    item_class_id: int
    quantity: int
    price_charged: Optional[float] = None


class ExpenseCreate(BaseModel):
    category: str
    amount: float
    note: Optional[str] = None


@app.get("/customers")
def list_customers():
    return [asdict(c) for c in customer_repo.list_all()]


@app.get("/item-classes")
def list_item_classes():
    return [asdict(i) for i in item_class_repo.list_all()]


@app.post("/loads")
def create_load(payload: LoadCreate):
    customer = customer_repo.add(Customer(id=None, name=payload.customer_name))
    try:
        load = record_load.execute(
            customer_id=customer.id,
            item_class_id=payload.item_class_id,
            quantity=payload.quantity,
            price_charged=payload.price_charged,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return asdict(load)


@app.post("/expenses")
def create_expense(payload: ExpenseCreate):
    expense = record_expense.execute(
        category=payload.category,
        amount=payload.amount,
        note=payload.note,
    )
    return asdict(expense)


@app.get("/totals")
def totals(start: date, end: date):
    result = get_period_totals.execute(start, end)
    return asdict(result)

class LoadCreate(BaseModel):
    customer_name: str
    item_class_id: int
    quantity: int
    price_charged: Optional[float] = None
    expected_pickup_date: Optional[date] = None


class StatusUpdate(BaseModel):
    status: str


@app.post("/loads")
def create_load(payload: LoadCreate):
    customer = customer_repo.add(Customer(id=None, name=payload.customer_name))
    try:
        load = record_load.execute(
            customer_id=customer.id,
            item_class_id=payload.item_class_id,
            quantity=payload.quantity,
            price_charged=payload.price_charged,
            expected_pickup_date=payload.expected_pickup_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return asdict(load)


@app.patch("/loads/{load_id}/status")
def update_status(load_id: int, payload: StatusUpdate):
    try:
        load = update_load_status.execute(load_id, payload.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return asdict(load)


@app.patch("/loads/{load_id}/pay")
def mark_paid(load_id: int):
    try:
        load = mark_load_paid.execute(load_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return asdict(load)

@app.get("/loads")
def list_loads(start: date, end: date):
    return [asdict(l) for l in load_repo.list_between(start, end)]

@app.get("/expenses")
def list_expenses(start: date, end: date):
    return [asdict(e) for e in expense_repo.list_between(start, end)]


class ItemClassCreate(BaseModel):
    name: str
    base_price: float


@app.post("/item-classes")
def create_item_class(payload: ItemClassCreate):
    item_class = item_class_repo.add(ItemClass(id=None, name=payload.name, base_price=payload.base_price))
    return asdict(item_class)