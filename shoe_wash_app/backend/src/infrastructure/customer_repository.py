from typing import List, Optional

from domain import Customer
from application import CustomerRepository
from .supabase_client import get_client


class SupabaseCustomerRepository(CustomerRepository):
    def __init__(self):
        self._client = get_client()

    def add(self, customer: Customer) -> Customer:
        result = self._client.table("customers").insert(
            {"name": customer.name, "phone": customer.phone, "credit_limit": customer.credit_limit}
        ).execute()
        row = result.data[0]
        customer.id = row["id"]
        return customer

    def get(self, customer_id: int) -> Optional[Customer]:
        result = self._client.table("customers").select("*").eq("id", customer_id).execute()
        if not result.data:
            return None
        row = result.data[0]
        return Customer(id=row["id"], name=row["name"], phone=row["phone"], credit_limit=row["credit_limit"])

    def list_all(self) -> List[Customer]:
        rows = self._client.table("customers").select("*").execute().data
        return [Customer(id=r["id"], name=r["name"], phone=r["phone"], credit_limit=r["credit_limit"]) for r in rows]

    def update(self, customer: Customer) -> Customer:
        self._client.table("customers").update(
            {"name": customer.name, "phone": customer.phone, "credit_limit": customer.credit_limit}
        ).eq("id", customer.id).execute()
        return customer