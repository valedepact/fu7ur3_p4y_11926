from datetime import date

from domain import PickupRequestStatus, DeliveryMethod
from application import CreatePickupRequest, ConfirmPickupRequest, CancelPickupRequest, CollectPickupRequest, RecordLoad, LoadItemInput

def test_creating_a_request_starts_as_requested(pickup_request_repo):
    request = CreatePickupRequest(pickup_request_repo).execute(
        customer_name="Amina", phone="0772000000", address="Plot 4, Ntinda"
    )
    assert request.status == PickupRequestStatus.REQUESTED
    assert request.id is not None


def test_confirming_sets_status_and_scheduled_date(pickup_request_repo):
    request = CreatePickupRequest(pickup_request_repo).execute(
        customer_name="Amina", phone="0772000000", address="Plot 4, Ntinda"
    )
    confirmed = ConfirmPickupRequest(pickup_request_repo).execute(request.id, date(2026, 9, 20))
    assert confirmed.status == PickupRequestStatus.CONFIRMED
    assert confirmed.scheduled_date == date(2026, 9, 20)


def test_cancelling_sets_status(pickup_request_repo):
    request = CreatePickupRequest(pickup_request_repo).execute(
        customer_name="Amina", phone="0772000000", address="Plot 4, Ntinda"
    )
    cancelled = CancelPickupRequest(pickup_request_repo).execute(request.id)
    assert cancelled.status == PickupRequestStatus.CANCELLED


def test_collecting_creates_a_delivery_load_and_marks_request_collected(
    pickup_request_repo, load_repo, item_class_repo, customer_repo, settings_repo, sneakers
):
    request = CreatePickupRequest(pickup_request_repo).execute(
        customer_name="Amina", phone="0772000000", address="Plot 4, Ntinda"
    )
    record_load = RecordLoad(load_repo, item_class_repo, customer_repo, settings_repo)
    collect = CollectPickupRequest(pickup_request_repo, customer_repo, record_load)

    result = collect.execute(request.id, items=[LoadItemInput(item_class_id=sneakers.id, quantity=2)])

    assert result.load.delivery_method == DeliveryMethod.PICKUP_DELIVERY
    assert result.load.pickup_address == "Plot 4, Ntinda"

    updated_request = pickup_request_repo.get(request.id)
    assert updated_request.status == PickupRequestStatus.COLLECTED
    assert updated_request.collected_load_id == result.load.id