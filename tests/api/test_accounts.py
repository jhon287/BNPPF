from unittest import TestCase
from fastapi.testclient import TestClient
from fastapi.datastructures import Headers
from httpx import Response, codes
from typing import Optional
from pyotp import TOTP
from main import api
from config import API_USER_NAME, API_USER_PASSWORD, API_OTP_SECRET


def auth_login(
    client: TestClient, username: str, password: str, otp_secret: str
) -> Optional[str]:
    otp: TOTP = TOTP(s=otp_secret)
    reponse: Response = client.post(
        url="/auth/login",
        data={"username": username, "password": f"{password}{otp.now()}"},
    )
    if reponse.status_code == codes.OK and "bearer" in reponse.text:
        reponse_json: dict[str, str] = reponse.json()
        return str(reponse_json.get("access_token"))
    return None

class AccountsTests(TestCase):
    client: TestClient = TestClient(app=api)

    def test_get_accounts(self):
        token: Optional[str] = auth_login(
            client=self.client,
            username=API_USER_NAME,
            password=API_USER_PASSWORD,
            otp_secret=API_OTP_SECRET,
        )
        self.assertIsNotNone(obj=token)

        response: Response = self.client.get(
            "/accounts", headers=Headers({"authorization": f"Bearer {token}"})
        )
        self.assertEqual(first=response.status_code, second=codes.OK)
        self.assertEqual(
            first=response.json(), second={"accounts": ["BE01234567890123"]}
        )
