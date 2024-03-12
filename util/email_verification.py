from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired

from config import SECRET_KEY

from pydantic import EmailStr
from fastapi import HTTPException
from starlette import status


token_algo = URLSafeTimedSerializer(
    SECRET_KEY, salt='Email_Verification')


def token(email: EmailStr):
    _token = token_algo.dumps(email)
    return _token


def change_email_token(email: EmailStr, id: int):
    _token = token_algo.dumps({"email": email, "id": id})
    return _token


def verify_token(token: str, email_change: bool = False):
    try:
        if email_change:
            email_id_data = token_algo.loads(token, max_age=1800)
            data = {"email": email_id_data["email"],
                    "id": email_id_data["id"], "check": True}
        else:
            email = token_algo.loads(token, max_age=1800)
            data = {'email': email, 'check': True}
    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token Expired")
    except BadTimeSignature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")
    return data
