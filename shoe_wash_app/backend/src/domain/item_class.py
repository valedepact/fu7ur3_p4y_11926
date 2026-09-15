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