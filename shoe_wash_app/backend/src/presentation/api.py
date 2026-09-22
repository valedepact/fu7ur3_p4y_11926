from dataclasses import asdict
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from domain import BusinessSettings, Customer, ItemClass
from application import (
    RecordLoad, RecordExpense, GetPeriodTotals, UpdateLoadStatus, MarkLoadPaid,
    RecordPayment, GetProfitability, GetDailyCapacity, GetAbandonedLoads,
    GetOutstandingBalance, GetCustomerBalance, GetPeakHours, GetItemClassPopularity,
    CreatePickupRequest, ConfirmPickupRequest, CancelPickupRequest, CollectPickupRequest,
)
from infrastructure import (
    SupabaseCustomerRepository,
    SupabaseItemClassRepository,
    SupabaseLoadRepository,
    SupabaseExpenseRepository,
    SupabaseBusinessSettingsRepository,
    SupabasePickupRequestRepository,
)

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
settings_repo = SupabaseBusinessSettingsRepository()
pickup_request_repo = SupabasePickupRequestRepository()

record_load = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)
record_expense = RecordExpense(expense_repo)
get_period_totals = GetPeriodTotals(load_repo, expense_repo)
update_load_status = UpdateLoadStatus(load_repo)
mark_load_paid = MarkLoadPaid(load_repo)
record_payment = RecordPayment(load_repo)
get_profitability = GetProfitability(load_repo)
get_daily_capacity = GetDailyCapacity(load_repo, item_class_repo, settings_repo)
get_abandoned_loads = GetAbandonedLoads(load_repo, settings_repo)
get_outstanding_balance = GetOutstandingBalance(load_repo)
get_customer_balance = GetCustomerBalance(load_repo)
get_peak_hours = GetPeakHours(load_repo)
get_item_class_popularity = GetItemClassPopularity(load_repo)

create_pickup_request = CreatePickupRequest(pickup_request_repo)
confirm_pickup_request = ConfirmPickupRequest(pickup_request_repo)
cancel_pickup_request = CancelPickupRequest(pickup_request_repo)
collect_pickup_request = CollectPickupRequest(pickup_request_repo, customer_repo, record_load)


class LoadCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    item_class_id: int
    quantity: int
    price_charged: Optional[float] = None
    expected_pickup_date: Optional[date] = None


class ExpenseCreate(BaseModel):
    category: str
    amount: float
    note: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


class ItemClassCreate(BaseModel):
    name: str
    base_price: float
    unit_cost: float = 0.0
    wash_minutes: int = 30


class PaymentCreate(BaseModel):
    amount: float


class SettingsUpdate(BaseModel):
    daily_operating_minutes: int
    abandonment_days: int


class PickupRequestCreate(BaseModel):
    customer_name: str
    phone: str
    address: str
    notes: Optional[str] = None


class PickupConfirm(BaseModel):
    scheduled_date: date


class PickupCollect(BaseModel):
    item_class_id: int
    quantity: int
    price_charged: Optional[float] = None
    expected_pickup_date: Optional[date] = None


@app.get("/customers")
def list_customers():
    return [asdict(c) for c in customer_repo.list_all()]


@app.get("/item-classes")
def list_item_classes():
    return [asdict(i) for i in item_class_repo.list_all()]


@app.post("/loads")
def create_load(payload: LoadCreate):
    customer = customer_repo.add(Customer(id=None, name=payload.customer_name, phone=payload.customer_phone))
    try:
        result = record_load.execute(
            customer_id=customer.id,
            item_class_id=payload.item_class_id,
            quantity=payload.quantity,
            price_charged=payload.price_charged,
            expected_pickup_date=payload.expected_pickup_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"load": asdict(result.load), "warnings": result.warnings}


@app.get("/loads")
def list_loads(start: date, end: date):
    return [asdict(l) for l in load_repo.list_between(start, end)]


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


@app.post("/loads/{load_id}/payments")
def record_payment_endpoint(load_id: int, payload: PaymentCreate):
    try:
        load = record_payment.execute(load_id, payload.amount)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return asdict(load)


@app.post("/expenses")
def create_expense(payload: ExpenseCreate):
    expense = record_expense.execute(
        category=payload.category,
        amount=payload.amount,
        note=payload.note,
    )
    return asdict(expense)


@app.get("/expenses")
def list_expenses(start: date, end: date):
    return [asdict(e) for e in expense_repo.list_between(start, end)]


@app.get("/totals")
def totals(start: date, end: date):
    result = get_period_totals.execute(start, end)
    return asdict(result)


@app.post("/item-classes")
def create_item_class(payload: ItemClassCreate):
    item_class = item_class_repo.add(ItemClass(
        id=None, name=payload.name, base_price=payload.base_price,
        unit_cost=payload.unit_cost, wash_minutes=payload.wash_minutes,
    ))
    return asdict(item_class)


@app.get("/reports/profitability")
def profitability(start: date, end: date):
    return asdict(get_profitability.execute(start, end))


@app.get("/reports/capacity")
def capacity(on_date: date):
    result = get_daily_capacity.execute(on_date)
    return {
        "used_minutes": result.used_minutes,
        "total_minutes": result.total_minutes,
        "remaining_minutes": result.remaining_minutes,
    }


@app.get("/reports/abandoned")
def abandoned():
    return [asdict(l) for l in get_abandoned_loads.execute()]


@app.get("/reports/outstanding-balance")
def outstanding_balance():
    return {"total_owed": get_outstanding_balance.execute()}


@app.get("/customers/{customer_id}/balance")
def customer_balance(customer_id: int):
    return {"customer_id": customer_id, "owed": get_customer_balance.execute(customer_id)}


@app.get("/reports/peak-hours")
def peak_hours(start: date, end: date):
    return get_peak_hours.execute(start, end)


@app.get("/reports/popular-items")
def popular_items(start: date, end: date):
    return [asdict(e) for e in get_item_class_popularity.execute(start, end)]


@app.get("/settings")
def get_settings():
    return asdict(settings_repo.get())


@app.put("/settings")
def update_settings(payload: SettingsUpdate):
    settings = settings_repo.update(BusinessSettings(**payload.dict()))
    return asdict(settings)


@app.post("/pickup-requests")
def request_pickup(payload: PickupRequestCreate):
    request = create_pickup_request.execute(
        customer_name=payload.customer_name, phone=payload.phone,
        address=payload.address, notes=payload.notes,
    )
    return asdict(request)


@app.get("/pickup-requests")
def list_pickup_requests(status: str = "requested"):
    return [asdict(r) for r in pickup_request_repo.list_by_status(status)]


@app.patch("/pickup-requests/{request_id}/confirm")
def confirm_pickup(request_id: int, payload: PickupConfirm):
    try:
        request = confirm_pickup_request.execute(request_id, payload.scheduled_date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return asdict(request)


@app.patch("/pickup-requests/{request_id}/collect")
def collect_pickup(request_id: int, payload: PickupCollect):
    try:
        result = collect_pickup_request.execute(
            request_id, payload.item_class_id, payload.quantity,
            payload.price_charged, payload.expected_pickup_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"load": asdict(result.load), "warnings": result.warnings}


@app.patch("/pickup-requests/{request_id}/cancel")
def cancel_pickup(request_id: int):
    try:
        request = cancel_pickup_request.execute(request_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return asdict(request)
