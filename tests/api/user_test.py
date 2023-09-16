import unittest
from pyotp import TOTP, random_base32
from user import ApiUser


class UserTests(unittest.TestCase):
    my_totp_secret: str = random_base32()
    my_totp: TOTP = TOTP(s=my_totp_secret)
    my_username: str = "toto"
    my_password: str = "pouet"
    my_token: str = "fake-YzRiNDQ5YmRmNWE3OWMyNzBjNmYxZDA5OWM0Nzk2MzgK"
    my_user: ApiUser = ApiUser(
        username=my_username, password=my_password, otp_secret=my_totp_secret
    )

    def test_check_otp(self):
        self.assertTrue(expr=self.my_user.check_otp(otp=self.my_totp.now()))

    def test_check_password(self):
        self.assertTrue(expr=self.my_user.check_password(password=self.my_password))
