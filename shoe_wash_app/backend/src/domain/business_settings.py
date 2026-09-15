from dataclasses import dataclass


@dataclass
class BusinessSettings:
    """Shop-wide configuration -- not tied to any one washing job."""

    daily_operating_minutes: int = 600  # e.g. 10 hours
    abandonment_days: int = 14