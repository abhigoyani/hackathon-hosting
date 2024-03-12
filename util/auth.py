
from sqlalchemy.orm import Session
from database import SessionLocal
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status

import logging
from datetime import timedelta, datetime
from typing import Annotated

import blacklist
from models.user_model import User
from config import SECRET_KEY, ALOGIRITHM


logging.getLogger('passlib').setLevel(logging.ERROR)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def authenticated_user(username: str, password: str, db: Session):
    """
    Authenticate a user using their username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        db (Session): The database session to use for the query.

    Returns:
        User: The authenticated user.
        None: If the user is not authenticated.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if user.baned:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, admin: str, expires_delta: timedelta) -> str:
    """
    Creates an access token for the given user.

    Args:
        username (str): The username of the user.
        user_id (int): The ID of the user.
        admin (str): The admin status of the user.
        expires_delta (timedelta): The time duration for which the token will be valid.

    Returns:
        str: The generated access token.
    """
    expires = datetime.utcnow() + expires_delta
    encode = {
        'sub': username,
        'id': user_id,
        'admin': admin,
        'exp': expires
    }

    return jwt.encode(encode, SECRET_KEY, ALOGIRITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    if blacklist.check_blacklist(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has been blacklisted")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALOGIRITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        admin: str = payload.get('admin')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate")

        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate")
        if user.baned:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User is baned")

        return {'username': username, 'id': user_id, 'admin': admin, 'token': token}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate")


user_dependency = Annotated[dict, Depends(get_current_user)]
