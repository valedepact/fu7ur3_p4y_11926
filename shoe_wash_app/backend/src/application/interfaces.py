from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain import Customer, ItemClass, Load, Expense, BusinessSettings, PickupRequest


class CustomerRepository(ABC):
    @abstractmethod
    def add(self, customer: Customer) -> Customer: ...

    @abstractmethod
    def get(self, customer_id: int) -> Optional[Customer]: ...

    @abstractmethod
    def update(self, customer: Customer) -> Customer: ...

    @abstractmethod
    def list_all(self) -> List[Customer]: ...


class ItemClassRepository(ABC):
    @abstractmethod
    def add(self, item_class: ItemClass) -> ItemClass: ...

    @abstractmethod
    def get(self, item_class_id: int) -> Optional[ItemClass]: ...

    @abstractmethod
    def update(self, item_class: ItemClass) -> ItemClass: ...

    @abstractmethod
    def delete(self, item_class_id: int) -> None: ...

    @abstractmethod
    def list_all(self) -> List[ItemClass]: ...

class LoadRepository(ABC):
    @abstractmethod
    def add(self, load: Load) -> Load: ...

    @abstractmethod
    def get(self, load_id: int) -> Optional[Load]: ...

    @abstractmethod
    def update(self, load: Load) -> Load: ...

    @abstractmethod
    def list_between(self, start: date, end: date) -> List[Load]: ...


class ExpenseRepository(ABC):
    @abstractmethod
    def add(self, expense: Expense) -> Expense: ...

    @abstractmethod
    def list_between(self, start: date, end: date) -> List[Expense]: ...

class BusinessSettingsRepository(ABC):
    @abstractmethod
    def get(self) -> BusinessSettings: ...

    @abstractmethod
    def update(self, settings: BusinessSettings) -> BusinessSettings: ...

class PickupRequestRepository(ABC):
    @abstractmethod
    def add(self, request: PickupRequest) -> PickupRequest: ...

    @abstractmethod
    def get(self, request_id: int) -> Optional[PickupRequest]: ...

    @abstractmethod
    def update(self, request: PickupRequest) -> PickupRequest: ...

    @abstractmethod
    def list_by_status(self, status: str) -> List[PickupRequest]: ...