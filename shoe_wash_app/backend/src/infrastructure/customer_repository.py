from typing import List, Optional

from domain import Customer
from application import CustomerRepository
from .supabase_client import get_client


class SupabaseCustomerRepository(CustomerRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, customer: Customer) -> Customer:
        result = self._client.table("customers").insert(
            {"name": customer.name, "phone": customer.phone}
        ).execute()
        row = result.data[0]
        customer.id = row["id"]
        return customer

    def get(self, customer_id: int) -> Optional[Customer]:
        result = self._client.table("customers").select("*").eq("id", customer_id).execute()
        if not result.data:
            return None
        row = result.data[0]
        return Customer(id=row["id"], name=row["name"], phone=row["phone"])

    def list_all(self) -> List[Customer]:
        result = self._client.table("customers").select("*").execute()
        return [Customer(id=row["id"], name=row["name"], phone=row["phone"]) for row in result.data]