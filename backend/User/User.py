from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class User:
    name: str
    email: str
    id: Optional[str] = None
    is_active: bool = True

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def deactivate(self):
        self.is_active = False