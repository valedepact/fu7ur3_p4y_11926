from dataclasses import dataclass


@dataclass
class BusinessSettings:
    """Shop-wide configuration -- not tied to any one washing job."""

    daily_operating_minutes: int = 600
    abandonment_days: int = 14
    default_credit_limit: float = 50000.0

    def __post_init__(self):
        if self.daily_operating_minutes <= 0:
            raise ValueError("Daily operating minutes must be positive")
        if self.abandonment_days <= 0:
            raise ValueError("Abandonment days must be positive")
        if self.default_credit_limit < 0:
            raise ValueError("Default credit limit cannot be negative")