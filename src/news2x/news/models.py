from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Article:
    title: str
    url: str
    source: str
    published_at: Optional[datetime]
    summary: str = ""
    image_url: Optional[str] = None