from dataclasses import dataclass
from datetime import date
from typing import Optional


class ExpenseCategory:
    """Plain string constants -- easy to add a new category without touching
    any other file."""

    SUPPLIES = "supplies"
    UTILITIES = "utilities"
    MACHINE_UPKEEP = "machine_upkeep"
    OTHER = "other"


@dataclass
class Expense:
    """One outgoing cost -- supplies, utilities, machine upkeep, or other."""

    id: Optional[int]
    date: date
    category: str
    amount: float
    note: Optional[str] = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Expense amount must be positive")
