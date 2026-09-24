from dataclasses import asdict
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

from domain import BusinessSettings, Customer, ItemClass
from application import (
    RecordLoad, RecordExpense, GetPeriodTotals, UpdateLoadStatus, MarkLoadPaid,
    RecordPayment, GetProfitability, GetDailyCapacity, GetAbandonedLoads,
    GetOutstandingBalance, GetCustomerBalance, GetPeakHours, GetItemClassPopularity,
    CreatePickupRequest, ConfirmPickupRequest, CancelPickupRequest, CollectPickupRequest,
    LoadItemInput,
)
from infrastructure import (
    SupabaseCustomerRepository,
    SupabaseItemClassRepository,
    SupabaseLoadRepository,
    SupabaseExpenseRepository,
    SupabaseBusinessSettingsRepository,
    SupabasePickupRequestRepository,
)

app = FastAPI(title="Shoe Wash API", docs_url=None, redoc_url=None)


@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
def docs():
        return """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Shoe Wash API</title>
            <style>
                body { font: 16px system-ui, sans-serif; margin: 2rem auto; max-width: 1000px; padding: 0 1rem; color: #17202a; }
                h1 { margin-bottom: .25rem; }
                .muted { color: #5f6b76; }
                .endpoint { border: 1px solid #d9e0e6; border-radius: 6px; margin: .75rem 0; padding: .85rem 1rem; }
                .method { display: inline-block; font: 700 12px monospace; min-width: 4rem; }
                .GET { color: #087f5b; } .POST { color: #1864ab; } .PATCH { color: #a15800; } .DELETE { color: #c92a2a; }
                code { background: #f1f3f5; border-radius: 3px; padding: .15rem .3rem; }
                pre { background: #f8f9fa; overflow: auto; padding: 1rem; }
            </style>
        </head>
        <body>
            <h1 id="title">Shoe Wash API</h1>
            <p class="muted">Local API documentation</p>
            <div id="content">Loading endpoints...</div>
            <script>
                const content = document.getElementById("content");
                fetch("/openapi.json")
                    .then((response) => {
                        if (!response.ok) throw new Error(`OpenAPI request failed (${response.status})`);
                        return response.json();
                    })
                    .then((schema) => {
                        document.getElementById("title").textContent = schema.info.title;
                        content.innerHTML = Object.entries(schema.paths).flatMap(([path, methods]) =>
                            Object.entries(methods).map(([method, details]) => `
                                <div class="endpoint">
                                    <span class="method ${method.toUpperCase()}">${method.toUpperCase()}</span>
                                    <code>${path}</code>
                                    <div>${details.summary || details.description || ""}</div>
                                </div>`)
                        ).join("");
                    })
                    .catch((error) => { content.innerHTML = `<p>${error.message}</p>`; });
            </script>
        </body>
        </html>
        """

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
    items: List[LoadItemCreate]
    expected_pickup_date: Optional[date] = None

class LoadItemCreate(BaseModel):
    item_class_id: int
    quantity: int
    price_charged: Optional[float] = None

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
    default_credit_limit: float


class PickupRequestCreate(BaseModel):
    customer_name: str
    phone: str
    address: str
    notes: Optional[str] = None


class PickupConfirm(BaseModel):
    scheduled_date: date


class PickupCollect(BaseModel):
    items: List[LoadItemCreate]
    expected_pickup_date: Optional[date] = None

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    credit_limit: Optional[float] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    credit_limit: Optional[float] = None


class ItemClassUpdate(BaseModel):
    name: Optional[str] = None
    base_price: Optional[float] = None
    unit_cost: Optional[float] = None
    wash_minutes: Optional[int] = None

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
            items=[LoadItemInput(item_class_id=i.item_class_id, quantity=i.quantity, price_charged=i.price_charged)
                   for i in payload.items],
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
            request_id,
            [LoadItemInput(item_class_id=i.item_class_id, quantity=i.quantity, price_charged=i.price_charged)
             for i in payload.items],
            payload.expected_pickup_date,
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


@app.post("/customers")
def create_customer(payload: CustomerCreate):
    customer = customer_repo.add(Customer(
        id=None, name=payload.name, phone=payload.phone, credit_limit=payload.credit_limit,
    ))
    return asdict(customer)

@app.patch("/customers/{customer_id}")
def update_customer(customer_id: int, payload: CustomerUpdate):
    customer = customer_repo.get(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"No customer with id {customer_id}")
    if payload.name is not None:
        customer.name = payload.name
    if payload.phone is not None:
        customer.phone = payload.phone
    if payload.credit_limit is not None:
        customer.credit_limit = payload.credit_limit
    return asdict(customer_repo.update(customer))

@app.patch("/item-classes/{item_class_id}")
def update_item_class(item_class_id: int, payload: ItemClassUpdate):
    item_class = item_class_repo.get(item_class_id)
    if item_class is None:
        raise HTTPException(status_code=404, detail=f"No item class with id {item_class_id}")
    if payload.name is not None:
        item_class.name = payload.name
    if payload.base_price is not None:
        item_class.base_price = payload.base_price
    if payload.unit_cost is not None:
        item_class.unit_cost = payload.unit_cost
    if payload.wash_minutes is not None:
        item_class.wash_minutes = payload.wash_minutes
    return asdict(item_class_repo.update(item_class))

@app.delete("/item-classes/{item_class_id}")
def delete_item_class(item_class_id: int):
    try:
        item_class_repo.delete(item_class_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"deleted": True}