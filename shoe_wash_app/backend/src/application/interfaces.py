from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain import Customer, ItemClass, Load, Expense


class CustomerRepository(ABC):
    @abstractmethod
    def add(self, customer: Customer) -> Customer: ...

    @abstractmethod
    def get(self, customer_id: int) -> Optional[Customer]: ...

    @abstractmethod
    def list_all(self) -> List[Customer]: ...


class ItemClassRepository(ABC):
    @abstractmethod
    def add(self, item_class: ItemClass) -> ItemClass: ...

    @abstractmethod
    def get(self, item_class_id: int) -> Optional[ItemClass]: ...

    @abstractmethod
    def list_all(self) -> List[ItemClass]: ...


class LoadRepository(ABC):
    @abstractmethod
    def add(self, load: Load) -> Load: ...

    @abstractmethod
    def list_between(self, start: date, end: date) -> List[Load]: ...


class ExpenseRepository(ABC):
    @abstractmethod
    def add(self, expense: Expense) -> Expense: ...

    @abstractmethod
    def list_between(self, start: date, end: date) -> List[Expense]: ...
