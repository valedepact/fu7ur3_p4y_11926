from domain import Load
from .interfaces import LoadRepository


class UpdateLoadStatus:
    """Use case: move a load through dropped_off -> washing -> ready -> picked_up."""

    def __init__(self, load_repo: LoadRepository):
        self._load_repo = load_repo

    def execute(self, load_id: int, new_status: str) -> Load:
        load = self._load_repo.get(load_id)
        if load is None:
            raise ValueError(f"No load with id {load_id}")
        load.status = new_status
        return self._load_repo.update(load)