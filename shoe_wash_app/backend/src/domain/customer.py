from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    """A person who brings items in for washing."""

    id: Optional[int]
    name: str
    phone: Optional[str] = None
    credit_limit: Optional[float] = None  # None = no cap on how much they can owe