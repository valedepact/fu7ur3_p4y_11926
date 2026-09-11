from dataclasses import dataclass
from typing import Optional


@dataclass
class ItemClass:
    """A category of item that can be washed (sneakers, canvas, leather...),
    with a suggested price that a load can override."""

    id: Optional[int]
    name: str
    base_price: float
