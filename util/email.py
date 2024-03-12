import requests
from config import MAILGUN_API_KEY, MAILGUN_FROM_EMAIL, SERVER_ADDRESS, MAILGUN_API_ENDPOINT
from pydantic import EmailStr
from requests import Response
from .email_verification import token
from fastapi import HTTPException
from starlette import status


def send_email(email_address: EmailStr, subject: str, content: str) -> Response:
    print(email_address)
    respone = requests.post(
        MAILGUN_API_ENDPOINT,
        auth=("api", MAILGUN_API_KEY),
        data={"from": MAILGUN_FROM_EMAIL,
              "to": [email_address],
              "subject": subject,
              "text": content,
              })
    print('-------mail--------')
    print(respone.__dict__)
    print(respone.status_code)
    print('-------mail--------')
    return respone


def send_verification_token(email_address: EmailStr, token: str, url: str = "/", emailChange: bool = False):

    if emailChange:
        subject = "verify your changed email"
        content = f"Click the link to verify your email change: {
            SERVER_ADDRESS}{url}/{token}"
    else:
        subject = "Email Verification"
        content = f"Click the link to verify your email: {
            SERVER_ADDRESS}{url}/{token}"

    response = send_email(email_address, subject, content)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Email sending failed")
