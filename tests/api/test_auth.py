from datetime import timedelta
from time import mktime, gmtime
from unittest import TestCase
from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from httpx import Response, codes
from pyotp import TOTP
from jose import jwt
from main import api
from config import API_OTP_SECRET, API_USER_NAME, API_USER_PASSWORD
from auth import (
    is_expired,
    check_access_token,
    create_access_token,
    check_authorization_header,
)


class AuthTests(TestCase):
    client: TestClient = TestClient(app=api)

    def test_create_access_token(self):
        encoded_jwt: str = create_access_token(data={"a": 1, "b": 2, "c": 3})
        self.assertEqual(type(encoded_jwt), str)

    def test_check_access_token(self):
        access_token: str = create_access_token(data={"sub": "john-doe"})
        self.assertTrue(expr=check_access_token(token=access_token))

        access_token = jwt.encode(
            claims={"sub": "toto"}, key="secret", algorithm="HS384"
        )
        self.assertFalse(expr=check_access_token(token=access_token))

        access_token = create_access_token(
            data={"sub": "john-doe"}, expires_delta=timedelta(minutes=-15)
        )
        print(access_token)
        self.assertFalse(expr=check_access_token(token=access_token))

    def test_is_expired(self):
        self.assertTrue(expr=is_expired(expires=mktime(gmtime()) - 10))
        self.assertFalse(expr=is_expired(expires=mktime(gmtime()) + 10))

    def test_check_authorization_header(self):
        access_token: str = create_access_token(data={"sub": "toto"})
        self.assertTrue(
            expr=check_authorization_header(authorization=f"Bearer {access_token}")
        )
        with self.assertRaises(expected_exception=HTTPException):
            check_authorization_header(authorization=f"Bearer my-fake-token")

    def test_post_login_ok(self):
        otp: TOTP = TOTP(s=API_OTP_SECRET)
        reponse: Response = self.client.post(
            url="/auth/login",
            data={
                "username": API_USER_NAME,
                "password": f"{API_USER_PASSWORD}{otp.now()}",
            },
        )
        self.assertEqual(first=reponse.status_code, second=codes.OK)
        self.assertTrue(expr="bearer" in reponse.text)

    def test_post_login_nok(self):
        otp: TOTP = TOTP(s=API_OTP_SECRET)
        # Bad username
        reponse: Response = self.client.post(
            url="/auth/login",
            data={"username": "toto", "password": f"{API_USER_PASSWORD}{otp.now()}"},
        )
        self.assertEqual(first=reponse.status_code, second=codes.UNAUTHORIZED)
        # Bad TOTP
        reponse = self.client.post(
            url="/auth/login",
            data={"username": API_USER_NAME, "password": f"{API_USER_PASSWORD}123456"},
        )
        self.assertEqual(first=reponse.status_code, second=codes.UNAUTHORIZED)
