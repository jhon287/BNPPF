from datetime import datetime, timedelta
from time import mktime, gmtime
from fastapi import APIRouter, status, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, Any
from jose import jwt
from jose.exceptions import JWTError

from config import (
    API_USER,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire: datetime = datetime.utcnow() + expires_delta
    else:
        expire: datetime = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        claims=to_encode, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
    )
    return encoded_jwt


def check_access_token(token: str) -> bool:
    try:
        decoded_jwt: dict[str, Any] = jwt.decode(
            token=token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM
        )
    except JWTError:
        return False
    if is_expired(expires=decoded_jwt["exp"]):
        return False
    return True


def is_expired(expires: float) -> bool:
    return expires < mktime(gmtime())


def check_authorization_header(authorization: Optional[str] = Header(None)):
    if authorization is None or not check_access_token(token=authorization[7::]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return True


api_user = API_USER

router = APIRouter(prefix="/auth")


@router.post(path="/login", status_code=status.HTTP_200_OK)
def post_login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    username: str = form_data.username
    if not api_user.authenticate(
        username=username, password=form_data.password[:-6], otp=form_data.password[-6:]
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"username": username, "access_token": access_token, "token_type": "bearer"}
