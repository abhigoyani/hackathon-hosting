from typing import List
from fastapi import APIRouter, HTTPException, Path, Query
from starlette import status
from sqlalchemy import union, or_

from models import User
from util.db import db_dependency
from util.auth import bcrypt_context, user_dependency
from util.email_verification import change_email_token
from util.email import send_verification_token
from schemas.user_schema import UserPasswordVerificationRequest, UserSchema, FullUserSchema, UsernameUpdateRequest, NameUpdateRequest, EmailRequest
from schemas.hackathon_schema import HackthonSchema
from schemas.project_schema import ProjectSchema
from models import Hackathon, Project, ProjectMember
from config import PER_PAGE_LIMIT

router = APIRouter(
    prefix='/user',
    tags=['user']
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=FullUserSchema)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(User).filter(User.id == user.get('id')).first()


@router.get('/{user_id}', status_code=status.HTTP_200_OK, response_model=UserSchema)
async def get_user_by_id(db: db_dependency, user_id: int = Path(..., title="get user profile", ge=1)):
    return db.query(User).filter(User.id == user_id).first()


@router.patch('/username', status_code=status.HTTP_204_NO_CONTENT)
async def update_username(user: user_dependency, db: db_dependency, username_request: UsernameUpdateRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User not found')

    username_check = db.query(User).filter(User.id != user.get(
        'id'), User.username == username_request.username).first()
    if username_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    user_model.username = username_request.username
    db.add(user_model)
    db.commit()


@router.patch('/name', status_code=status.HTTP_204_NO_CONTENT)
async def update_name(user: user_dependency, db: db_dependency, name_request: NameUpdateRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User not found')
    user_model.name = name_request.name
    db.add(user_model)
    db.commit()


@router.patch('/email', status_code=status.HTTP_200_OK)
async def genrate_email_update_token_and_send(user: user_dependency, db: db_dependency, email_request: EmailRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User not found')
    email_check = db.query(User).filter(User.id != user.get(
        'id'), User.email == email_request.email).first()
    if email_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    verification_token = change_email_token(
        email_request.email, user.get('id'))
    send_verification_token(email_request.email,
                            verification_token, emailChange=True, url='/auth/confirm-email-change')
    return {'email_sent_to': email_request.email, 'message': 'Email sent for verification'}


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_password_verification: UserPasswordVerificationRequest):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if not bcrypt_context.verify(user_password_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(
        user_password_verification.new_password)
    db.add(user_model)
    db.commit()


@router.get('/projects/all', status_code=status.HTTP_200_OK, response_model=List[ProjectSchema])
async def get_user_projects(user: user_dependency, db: db_dependency, page: int = Query(1, ge=1)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    db_user = db.query(User).filter(User.id == user.get('id')).first()

    projects = db_user.projects.all() + db_user.member_projects.all()

    return projects


@router.get('/{user_id}/hackathon/organized', response_model=list[HackthonSchema], status_code=status.HTTP_200_OK)
async def get_organized_hackathons(user_id: int, db: db_dependency):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return db.query(Hackathon).filter(Hackathon.organizer_id == user_id).all()


@router.get('/{user_id}/hackathon/participated', response_model=list[HackthonSchema], status_code=status.HTTP_200_OK)
async def get_participated_hackathons(user_id: int, db: db_dependency):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    response = [participant.hackathon for participant in user.participants]

    print(response)
    return response
