# models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    first_name: str = ""
    points: int = 0
    referral_code: str = ""
    referred_by: Optional[int] = None
    is_banned: bool = False
    restricted_features: list = None

    def __post_init__(self):
        if self.restricted_features is None:
            self.restricted_features = []