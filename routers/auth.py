from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from starlette import status
from sqlalchemy import or_

from models import User
from util.auth import authenticated_user, create_access_token, bcrypt_context
from util.db import db_dependency
from util.email import send_verification_token
from util.email_verification import token, verify_token
from schemas.auth_schema import Token, EmailSentResponse, ResendVerificationEmailRequest, ForgotPasswordRequest
from schemas.user_schema import CreateUserRequest, EmailRequest
from blacklist import black_list_token

from config import SERVER_ADDRESS

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EmailSentResponse)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):

    db_user = db.query(User).filter(
        or_(User.email == create_user_request.email,
            User.username == create_user_request.username)
    ).first()

    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email or username already registered")

    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        name=create_user_request.name,
        hashed_password=bcrypt_context.hash(create_user_request.password),

    )

    user_token = token(create_user_request.email)
    print('create_user_request.email: ', create_user_request.email)

    try:
        send_verification_token(create_user_request.email,
                                user_token, url='/auth/confirm-email')
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unable to send email try to genrate token again after some time from {SERVER_ADDRESS}/auth/resend-verification-email")
    db.add(create_user_model)
    db.commit()

    return {'email_sent_to': create_user_request.email, 'message': 'Email sent for verification'}


@router.post("/resend-verification-email", status_code=status.HTTP_201_CREATED, response_model=EmailSentResponse)
async def resend_verification_email(db: db_dependency,
                                    resend_email: ResendVerificationEmailRequest):

    db_user = db.query(User).filter(User.email == resend_email.email).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email not registered")
    print('resend_email.email: ', resend_email.email)
    user_token = token(db_user.email)

    try:
        send_verification_token(
            db_user.email, user_token, url='/auth/confirm-email')
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unable to send email try to genrate token again after some time from {SERVER_ADDRESS}/auth/resend-verification-email")

    return {'email_sent_to': resend_email.email, 'message': 'Email sent for verification'}


@router.post('/confirm-email/{token}/', status_code=status.HTTP_202_ACCEPTED, description="Email verification")
async def user_verification(token: str, db: db_dependency):

    token_data = verify_token(token)

    user = db.query(User).filter(User.email == token_data['email']).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found with this email")
    if user.verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already verified")
    user.verified = True

    db.add(user)
    db.commit()
    return {'message': 'Email verified successfully'}


@router.post('/confirm-email-change/{token}/', status_code=status.HTTP_202_ACCEPTED, description="Email change verification")
async def user_verification(token: str, db: db_dependency):

    token_data = verify_token(token, email_change=True)
    print(token_data)
    user = db.query(User).filter(User.id == token_data['id']).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found with this email")
    user.email = token_data['email']

    db.add(user)
    db.commit()
    return {'message': 'Email changed successfully'}


@router.post('/forgot-password/{token}/', status_code=status.HTTP_202_ACCEPTED, description="Forgot password")
async def forgot_password(token: str, db: db_dependency, forgot_password_request: ForgotPasswordRequest):

    token_data = verify_token(token)

    user = db.query(User).filter(User.email == token_data['email']).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found with this email")

    user.hashed_password = bcrypt_context.hash(
        forgot_password_request.password)

    db.add(user)
    db.commit()
    return {'message': 'Password changed successfully'}


@router.post('/forgot-password', status_code=status.HTTP_202_ACCEPTED, description="Forgot password", response_model=EmailSentResponse)
async def forgot_password(email_request: EmailRequest, db: db_dependency):

    user = db.query(User).filter(User.email == email_request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found with this email")

    user_token = token(email_request.email)
    try:
        send_verification_token(email_request.email,
                                user_token, url='/auth/forgot-password')
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unable to send email try to genrate token again after some time from {SERVER_ADDRESS}/auth/forgot-password")

    return {'email_sent_to': email_request.email, 'message': 'Email sent for password reset'}


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):

    user = authenticated_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate")
    print('user.verified: ', user.verified)
    if user.verified == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Email not verified, please verify your email")

    if user.baned:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User is baned")

    token = create_access_token(
        user.username, user.id, user.admin, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/log-out', status_code=status.HTTP_202_ACCEPTED, description="Log out")
async def log_out(token: Annotated[str, Depends(oauth2_bearer)]):

    black_list_token(token)
    return {'message': 'Logged out successfully'}
