from datetime import datetime

from domain import Load, LoadStatus
from application import UpdateLoadStatus


def test_moves_load_to_new_status(load_repo):
    load = load_repo.add(Load(id=None, dropped_off_at=datetime.now(), customer_id=1, item_class_id=1,
                               quantity=1, price_charged=5000))
    updated = UpdateLoadStatus(load_repo).execute(load.id, LoadStatus.WASHING)
    assert updated.status == LoadStatus.WASHING