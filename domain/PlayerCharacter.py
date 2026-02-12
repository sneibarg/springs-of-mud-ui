from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PlayerCharacter:
    id: str
    accountId: str
    name: str
    title: str
    description: Optional[str]
    race: str
    sex: Optional[str]
    characterClass: str
    roomId: str
    areaId: str
    guild: str
    role: str
    cloaked: bool
    inventory: List[str]
    health: int
    mana: int
    movement: int
    level: int
    experience: int
    accumulatedExperience: int
    trains: int
    practices: int
    gold: int
    silver: int
    wimpy: int
    position: int
    maxWeight: int
    maxItems: int
    reputation: int
    piercing: int
    bashing: int
    slashing: int
    magic: int