from dataclasses import dataclass
from typing import List
from domain.PlayerCharacter import PlayerCharacter


@dataclass
class AuthResponse:
    id: str
    firstName: str
    lastName: str
    accountName: str
    emailAddress: str
    password: str
    playerCharacterList: List[PlayerCharacter]