from fastapi import APIRouter, Path

from models import User
from util.db import db_dependency


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.post('/ban/{user_id}')
async def ban_user(db: db_dependency, user_id: int = Path(..., title='The ID of the user to ban', ge=1)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {'message': f'User {user_id} not found'}
    user.baned = True
    db.commit()
    return {'message': f'User {user_id} has been banned'}


@router.post('/unban/{user_id}')
async def unban_user(db: db_dependency, user_id: int = Path(..., title='The ID of the user to unban', ge=1)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {'message': f'User {user_id} not found'}
    user.baned = False
    db.commit()
    return {'message': f'User {user_id} has been unbanned'}
