from datetime import date
from typing import Dict, List, Optional

import pytest

from domain import Customer, ItemClass, Load, Expense, BusinessSettings
from application import (
    CustomerRepository, ItemClassRepository, LoadRepository, ExpenseRepository, BusinessSettingsRepository,
)


class FakeCustomerRepository(CustomerRepository):
    def __init__(self):
        self._items: Dict[int, Customer] = {}
        self._next_id = 1

    def add(self, customer: Customer) -> Customer:
        customer.id = self._next_id
        self._items[customer.id] = customer
        self._next_id += 1
        return customer

    def get(self, customer_id: int) -> Optional[Customer]:
        return self._items.get(customer_id)

    def list_all(self) -> List[Customer]:
        return list(self._items.values())


class FakeItemClassRepository(ItemClassRepository):
    def __init__(self):
        self._items: Dict[int, ItemClass] = {}
        self._next_id = 1

    def add(self, item_class: ItemClass) -> ItemClass:
        item_class.id = self._next_id
        self._items[item_class.id] = item_class
        self._next_id += 1
        return item_class

    def get(self, item_class_id: int) -> Optional[ItemClass]:
        return self._items.get(item_class_id)

    def list_all(self) -> List[ItemClass]:
        return list(self._items.values())


class FakeLoadRepository(LoadRepository):
    def __init__(self):
        self._items: Dict[int, Load] = {}
        self._next_id = 1

    def add(self, load: Load) -> Load:
        load.id = self._next_id
        self._items[load.id] = load
        self._next_id += 1
        return load

    def get(self, load_id: int) -> Optional[Load]:
        return self._items.get(load_id)

    def update(self, load: Load) -> Load:
        self._items[load.id] = load
        return load

    def list_between(self, start: date, end: date) -> List[Load]:
        return [l for l in self._items.values() if start <= l.date <= end]


class FakeExpenseRepository(ExpenseRepository):
    def __init__(self):
        self._items: Dict[int, Expense] = {}
        self._next_id = 1

    def add(self, expense: Expense) -> Expense:
        expense.id = self._next_id
        self._items[expense.id] = expense
        self._next_id += 1
        return expense

    def list_between(self, start: date, end: date) -> List[Expense]:
        return [e for e in self._items.values() if start <= e.date <= end]


class FakeBusinessSettingsRepository(BusinessSettingsRepository):
    def __init__(self):
        self._settings = BusinessSettings()

    def get(self) -> BusinessSettings:
        return self._settings

    def update(self, settings: BusinessSettings) -> BusinessSettings:
        self._settings = settings
        return self._settings


@pytest.fixture
def customer_repo():
    return FakeCustomerRepository()


@pytest.fixture
def item_class_repo():
    return FakeItemClassRepository()


@pytest.fixture
def load_repo():
    return FakeLoadRepository()


@pytest.fixture
def expense_repo():
    return FakeExpenseRepository()


@pytest.fixture
def settings_repo():
    return FakeBusinessSettingsRepository()


@pytest.fixture
def sneakers(item_class_repo):
    return item_class_repo.add(ItemClass(id=None, name="sneakers", base_price=5000, unit_cost=1500, wash_minutes=30))


@pytest.fixture
def customer(customer_repo):
    return customer_repo.add(Customer(id=None, name="Test Customer"))