from datetime import datetime

import pytest

from domain import Load, LoadItem, LoadStatus
from application import UpdateLoadStatus


def _load():
    return Load(
        id=None, dropped_off_at=datetime.now(), customer_id=1,
        items=[LoadItem(id=None, item_class_id=1, quantity=1, price_charged=5000)],
    )


def test_moves_load_to_new_status(load_repo):
    load = load_repo.add(_load())
    updated = UpdateLoadStatus(load_repo).execute(load.id, LoadStatus.WASHING)
    assert updated.status == LoadStatus.WASHING


def test_rejects_an_invalid_transition(load_repo):
    load = load_repo.add(_load())
    with pytest.raises(ValueError):
        UpdateLoadStatus(load_repo).execute(load.id, LoadStatus.PICKED_UP)