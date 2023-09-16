from pyotp import TOTP
from bcrypt import gensalt, hashpw, checkpw


class ApiUser:
    username: str
    hashed_password: bytes
    otp: TOTP

    def __init__(self, username: str, password: str, otp_secret: str) -> None:
        self.username = username
        self.otp = TOTP(s=otp_secret)
        self.hashed_password = hashpw(password=password.encode(), salt=gensalt())

    def check_otp(self, otp: str) -> bool:
        return self.otp.verify(otp)

    def check_password(self, password: str):
        return checkpw(password.encode(), self.hashed_password)

    def authenticate(self, username: str, password: str, otp: str):
        return (
            self.username == username
            and self.check_password(password=password)
            and self.check_otp(otp=otp)
        )
