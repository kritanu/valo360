from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WeaponList:
    _id: str
    wp_list: list = field(default_factory=list)