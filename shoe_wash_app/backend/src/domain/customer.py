from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    """A person who brings items in for washing."""

    id: Optional[int]
    name: str
    phone: Optional[str] = None
    credit_limit: Optional[float] = None  # None = no cap on how much they can owe

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Customer name is required")
        if self.credit_limit is not None and self.credit_limit < 0:
            raise ValueError("Credit limit cannot be negative")