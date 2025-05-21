from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
import uuid

@dataclass
class Character:
    """
    Base class for all characters in The Last of Us universe.
    Tracks health and who dealt the fatal blow.
    """
    name: str
    health: int = field(default=100)
    killed_by: Optional['Character'] = field(default=None)

    @property
    def is_alive(self):
        return self.health > 0
