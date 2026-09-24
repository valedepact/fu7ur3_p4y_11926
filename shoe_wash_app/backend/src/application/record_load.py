from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from domain import Load, LoadItem
from .interfaces import LoadRepository, ItemClassRepository, CustomerRepository, BusinessSettingsRepository


@dataclass
class LoadItemInput:
    item_class_id: int
    quantity: int
    price_charged: Optional[float] = None


@dataclass
class RecordLoadResult:
    load: Load
    warnings: List[str] = field(default_factory=list)


class RecordLoad:
    def __init__(
        self,
        load_repo: LoadRepository,
        item_class_repo: ItemClassRepository,
        customer_repo: CustomerRepository,
        settings_repo: BusinessSettingsRepository,
    ):
        self._load_repo = load_repo
        self._item_class_repo = item_class_repo
        self._customer_repo = customer_repo
        self._settings_repo = settings_repo

    def execute(
        self,
        customer_id: int,
        items: List[LoadItemInput],
        expected_pickup_date: Optional[date] = None,
        dropped_off_at: Optional[datetime] = None,
        delivery_method: str = "walk_in",
        pickup_address: Optional[str] = None,
        delivery_address: Optional[str] = None,
    ) -> RecordLoadResult:
        if not items:
            raise ValueError("A load must contain at least one item")

        drop_off = dropped_off_at or datetime.now()
        load_items = []
        total_wash_minutes = 0

        for item_input in items:
            item_class = self._item_class_repo.get(item_input.item_class_id)
            if item_class is None:
                raise ValueError(f"No item class with id {item_input.item_class_id}")
            load_items.append(LoadItem(
                id=None,
                item_class_id=item_class.id,
                quantity=item_input.quantity,
                price_charged=(
                    item_input.price_charged if item_input.price_charged is not None else item_class.base_price
                ),
                unit_cost=item_class.unit_cost,
            ))
            total_wash_minutes += item_class.wash_minutes * item_input.quantity

        load = Load(
            id=None,
            dropped_off_at=drop_off,
            customer_id=customer_id,
            items=load_items,
            expected_pickup_date=expected_pickup_date,
            delivery_method=delivery_method,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
        )
        load = self._load_repo.add(load)

        warnings = []
        capacity_warning = self._check_capacity(total_wash_minutes, drop_off.date())
        if capacity_warning:
            warnings.append(capacity_warning)
        credit_warning = self._check_credit(customer_id)
        if credit_warning:
            warnings.append(credit_warning)

        return RecordLoadResult(load=load, warnings=warnings)

    def _check_capacity(self, this_load_minutes: int, on_date: date) -> Optional[str]:
        settings = self._settings_repo.get()
        todays_loads = self._load_repo.list_between(on_date, on_date)
        used_minutes = sum(
            (self._item_class_repo.get(item.item_class_id).wash_minutes or 0) * item.quantity
            for l in todays_loads for item in l.items
        )
        if used_minutes > settings.daily_operating_minutes:
            return (
                f"Today's washing time ({used_minutes} min) now exceeds "
                f"the {settings.daily_operating_minutes} min daily capacity."
            )
        return None

    def _check_credit(self, customer_id: int) -> Optional[str]:
        customer = self._customer_repo.get(customer_id)
        if customer is None or customer.credit_limit is None:
            return None
        all_loads = self._load_repo.list_between(date(2000, 1, 1), date.today())
        owed = sum(
            l.total - l.amount_paid for l in all_loads
            if l.customer_id == customer_id and l.amount_paid < l.total
        )
        if owed > customer.credit_limit:
            return f"{customer.name} now owes {owed}, over their credit limit of {customer.credit_limit}."
        return None