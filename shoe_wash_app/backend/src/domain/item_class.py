from dataclasses import dataclass
from typing import Optional


@dataclass
class ItemClass:
    """A category of item that can be washed, with pricing, true cost,
    and how long one wash actually takes."""

    id: Optional[int]
    name: str
    base_price: float
    unit_cost: float = 0.0       # water/power/soap/upkeep allocated per item
    wash_minutes: int = 30       # how long one wash occupies the machine

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Item class name is required")
        if self.base_price <= 0:
            raise ValueError("Base price must be positive")
        if self.unit_cost < 0:
            raise ValueError("Unit cost cannot be negative")
        if self.wash_minutes <= 0:
            raise ValueError("Wash minutes must be positive")