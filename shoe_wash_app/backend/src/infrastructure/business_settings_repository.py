from domain import BusinessSettings
from application import BusinessSettingsRepository
from .supabase_client import get_client


class SupabaseBusinessSettingsRepository(BusinessSettingsRepository):
    def __init__(self):
        self._client = get_client()

    def get(self) -> BusinessSettings:
        result = self._client.table("business_settings").select("*").eq("id", 1).execute()
        row = result.data[0]
        return BusinessSettings(
            daily_operating_minutes=row["daily_operating_minutes"],
            abandonment_days=row["abandonment_days"],
            default_credit_limit=row["default_credit_limit"],
        )

    def update(self, settings: BusinessSettings) -> BusinessSettings:
        self._client.table("business_settings").update(
            {
                "daily_operating_minutes": settings.daily_operating_minutes,
                "abandonment_days": settings.abandonment_days,
                "default_credit_limit": settings.default_credit_limit,
            }
        ).eq("id", 1).execute()
        return settings