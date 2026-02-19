from typing import Optional, Dict
from domain.PlayerCharacter import PlayerCharacter
from net.rest import AuthResponse

import requests


class AuthClient:
    def __init__(self, base_url: str = "http://localhost:8169"):
        self.base_url = base_url
        self.auth_endpoint = f"{base_url}/api/auth/login"
        self.jwt_token: Optional[str] = None
        self.auth_data: Optional[AuthResponse] = None

    def login(self, account_name: str, password: str) -> AuthResponse:
        payload = {
            "accountName": account_name,
            "password": password
        }

        response = requests.post(self.auth_endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        characters = [PlayerCharacter(**char) for char in data.get("playerCharacterList", [])]
        self.auth_data = AuthResponse(id=data["id"], firstName=data["firstName"], lastName=data["lastName"],
                                      accountName=data["accountName"], emailAddress=data["emailAddress"],
                                      password=data["password"], playerCharacterList=characters)

        if "Authorization" in response.headers:
            self.jwt_token = response.headers["Authorization"]

        return self.auth_data

    def get_auth_headers(self) -> Dict[str, str]:
        if self.jwt_token:
            return {"Authorization": f"Bearer {self.jwt_token}"}
        return {}

    def is_authenticated(self) -> bool:
        return self.auth_data is not None

    def logout(self) -> None:
        self.jwt_token = None
        self.auth_data = None
