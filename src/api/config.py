from os import getenv
from user import ApiUser
from pyotp import random_base32
from secrets import token_bytes
from base64 import b64encode
from typing import Final

# API
API_TITLE: Final[str] = "BNP Paribas Fortis API"
API_VERSION: str = getenv(key="API_VERSION", default="0.1.0")
API_IP: str = getenv(key="API_IP", default="0.0.0.0")
API_PORT: int = int(getenv(key="API_PORT", default=8000))
API_USER_NAME: str = getenv(key="API_USERNAME", default="john_doe")
API_USER_PASSWORD: str = getenv(key="API_PASSWORD", default="fake-password")
API_OTP_SECRET: Final[str] = getenv(key="API_TOKEN", default=random_base32())
API_USER: ApiUser = ApiUser(
    username=API_USER_NAME, password=API_USER_PASSWORD, otp_secret=API_OTP_SECRET
)

# DB
DB_USERNAME: str = getenv(key="DB_USERNAME", default="bnppf")
DB_PASSWORD: str = getenv(key="DB_PASSWORD", default="password")
DB_HOSTNAME: str = getenv(key="DB_HOSTNAME", default="localhost")
DB_PORT: int = int(getenv(key="DB_PORT", default=3306))
DB_NAME: str = getenv(key="DB_NAME", default="BNPPF")

# JWT
JWT_SECRET_KEY: str = getenv(
    key="JWT_SECRET_KEY", default=b64encode(token_bytes(32)).decode()
)
JWT_ALGORITHM: str = getenv(key="JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    getenv(key="JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
)


print(f"JWT secret key: {JWT_SECRET_KEY}")
print(f"API username: {API_USER.username}")
print(f"API username: {API_USER_PASSWORD}")
print(f"API user OTP secret: {API_USER.otp.secret}")
