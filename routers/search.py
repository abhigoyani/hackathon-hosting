from fastapi import APIRouter, Query
from sqlalchemy import or_

from models import Hackathon, Project, User
from schemas.hackathon_schema import HackthonPaginationSchema
from schemas.project_schema import ProjectPaginationSchema
from schemas.user_schema import UserPaginationSchema
from util.db import db_dependency
from config import PER_PAGE_LIMIT

router = APIRouter(
    prefix='/search',
    tags=['search']
)


@router.get('/hackathon', response_model=HackthonPaginationSchema)
async def search_hackathon(db: db_dependency, name: str = Query(..., title='The name of the hackathon to search for'), page: int = Query(1, title='The page number to return')):

    hackathons = db.query(Hackathon).filter(
        Hackathon.name.ilike(f'%{name}%')).order_by(Hackathon.id)

    total_hackathon = hackathons.count()
    hackathon_from = (page - 1) * PER_PAGE_LIMIT
    current_total_hackathon = hackathons.count()
    hackathon = hackathons.offset(hackathon_from).limit(PER_PAGE_LIMIT).all()

    response = {
        'total_hackathon': total_hackathon,
        'hackathon_from': hackathon_from,
        'current_total_hackathon': current_total_hackathon,
        'hackathon': hackathon
    }
    return response


@router.get('/project', response_model=ProjectPaginationSchema)
async def search_project(db: db_dependency, name: str = Query(..., title='The name of the project to search for'), page: int = Query(1, title='The page number to return')):

    projects = db.query(Project).filter(
        Project.name.ilike(f'%{name}%')).order_by(Project.id)

    total_projects = projects.count()
    project_from = (page - 1) * PER_PAGE_LIMIT
    current_total_project = projects.count()
    projects = projects.offset(project_from).limit(PER_PAGE_LIMIT).all()

    response = {
        'total_projects': total_projects,
        'project_from': project_from,
        'current_total_project': current_total_project,
        'projects': projects
    }
    return response


@router.get('/user', response_model=UserPaginationSchema)
async def search_user(db: db_dependency, name: str = Query(..., title='The name of the user to search for'), page: int = Query(1, title='The page number to return')):

    users = db.query(User).filter(
        or_(User.name.ilike(f'%{name}%'), User.username.ilike(f'%{name}%'))).order_by(User.id)

    total_users = users.count()
    user_from = (page - 1) * PER_PAGE_LIMIT
    current_total_users = users.count()
    users = users.offset(user_from).limit(PER_PAGE_LIMIT).all()

    response = {
        'total_users': total_users,
        'user_from': user_from,
        'current_total_users': current_total_users,
        'users': users
    }
    return response
