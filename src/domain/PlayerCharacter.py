import json
import re

from dataclasses import dataclass, field, fields
from typing import Any, Dict, List


def _snake_to_camel(key: str) -> str:
    if "_" not in key:
        return key
    head, *tail = key.split("_")
    return head + "".join(part.capitalize() for part in tail)


def _camel_to_snake(key: str) -> str:
    key = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", key)
    key = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return key.lower()


def _convert_keys(value: Any, key_converter) -> Any:
    if isinstance(value, dict):
        return {key_converter(str(k)): _convert_keys(v, key_converter) for k, v in value.items()}
    if isinstance(value, list):
        return [_convert_keys(v, key_converter) for v in value]
    return value


@dataclass
class PlayerCharacter:
    id: str = ""
    account_id: str = ""
    name: str = ""
    title: str = ""
    description: str = ""
    race: str = ""
    cloaked: bool = False
    guild: str = ""
    sex: str = "male"
    character_class: Dict[str, Any] = field(default_factory=dict)
    room_id: str = ""
    area_id: str = ""
    role: str = "player"
    character_flags: Dict[str, Any] = field(default_factory=dict)
    armor_class: Dict[str, Any] = field(default_factory=dict)
    character_attributes: Dict[str, Any] = field(default_factory=dict)
    temporal_mechanics: Dict[str, Any] = field(default_factory=dict)
    equipped: Any = field(default_factory=dict)
    prompt_format: Dict[str, bool] = field(default_factory=dict)
    inventory: List[Any] = field(default_factory=list)
    effects: List[Any] = field(default_factory=list)
    skills: List[Any] = field(default_factory=list)
    spells: List[Any] = field(default_factory=list)
    hit: int = 0
    max_hit: int = 0
    mana: int = 0
    max_mana: int = 0
    movement: int = 0
    max_movement: int = 0
    level: int = 1
    experience: int = 0
    accumulated_experience: int = 0
    experience_per_level: int = 1000
    gold: int = 0
    silver: int = 0
    trust: int = 0
    invis_level: int = 0
    incog_level: int = 0
    train: int = 0
    practice: int = 0
    points: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any], from_camel_case: bool = True) -> "PlayerCharacter":
        payload = _convert_keys(data, _camel_to_snake) if from_camel_case else dict(data)
        valid_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in payload.items() if k in valid_names}
        return cls(**filtered)

    @classmethod
    def from_json(cls, payload_json: str, from_camel_case: bool = True) -> "PlayerCharacter":
        return cls.from_dict(json.loads(payload_json), from_camel_case=from_camel_case)

    def to_dict(self, to_camel_case: bool = True) -> Dict[str, Any]:
        payload = dict(self.__dict__)
        return _convert_keys(payload, _snake_to_camel) if to_camel_case else payload

    def to_json(self, to_camel_case: bool = True) -> str:
        return json.dumps(self.to_dict(to_camel_case=to_camel_case))
