from dataclasses import dataclass
from typing import Optional 


@dataclass
class Consideration:
    type: str
    id: Optional[int] = None

