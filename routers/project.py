from sqlalchemy import desc
from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Path, File, UploadFile, Query
from starlette import status
from datetime import datetime

from config import SERVER_ADDRESS, PER_PAGE_LIMIT
from models import Project, Tag, ProjectImage, ProjectMember, User, Hackathon
from util.db import db_dependency
from util.auth import user_dependency
from util.file import save_image, delete_project_image
from util.submit import submit_project_to_hackathon
from util.project import project_not_submited_dependency
from util.filter import filter_projects
from schemas.project_schema import ProjectCreateRequest, AddTagRequest, ProjectPaginationSchema


router = APIRouter(
    prefix='/project',
    tags=['projects']
)


@router.get('/', status_code=status.HTTP_200_OK, description="Get all projects", response_model=ProjectPaginationSchema)
def get_projects(db: db_dependency, page: int = Query(1, ge=1), tags: Annotated[list[str] | None, Query()] = None, winner: bool = Query(None)):
    query = filter_projects(db, tags, winner).order_by(desc(Project.id))
    total = query.count()
    total = query.count()
    query = query.limit(PER_PAGE_LIMIT).offset((page-1)*PER_PAGE_LIMIT)

    response = {
        "total_projects": total,
        "project_from": (page-1)*PER_PAGE_LIMIT,
        "current_total_project": query.count(),
        "projects": query.all()
    }
    return response


# new route test
# from sqlalchemy import desc, and_
# from sqlalchemy.orm import aliased

# @router.get('/', status_code=status.HTTP_200_OK, description="Get all projects")
# def get_projects(db: db_dependency, page: int = Query(1, ge=1), tags: List[str] = Query(None)):
#     query = db.query(Project).order_by(desc(Project.id))

#     if tags:
#         TagAlias = aliased(Tag)
#         query = query.join(Project.tags.of_type(TagAlias)).filter(TagAlias.tag_name.in_(tags))

#     total = query.count()
#     query = query.limit(PER_PAGE_LIMIT).offset((page-1)*PER_PAGE_LIMIT)

#     response = {
#         "total_projects": total,
#         "project_from": (page-1)*PER_PAGE_LIMIT,
#         "current_total_project": query.count(),
#         "projects": query.all()
#     }
#     return response


@router.post('/', status_code=status.HTTP_200_OK)
async def create_project(user: user_dependency, db: db_dependency, project_request: ProjectCreateRequest):
    print('creating')
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    project = Project(
        author_id=user.get('id'),
        **project_request.model_dump(),
    )
    db.add(project)
    db.commit()
    return project


@router.delete('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(user: user_dependency, db: db_dependency, project: project_not_submited_dependency, project_id: int = Path(..., title="The ID of the project", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    if project.author_id != user.get('id') and user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    db.delete(project)
    db.commit()


@router.patch('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_project(project_request: ProjectCreateRequest, user: user_dependency, db: db_dependency, project: project_not_submited_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.author_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    project.update_from_dict(project_request.model_dump(exclude_none=True))
    db.commit()
    return project


@router.post('/{project_id}/tags', status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_project(tag_request: AddTagRequest, user: user_dependency, db: db_dependency, project_id: int = Path(..., title="The ID of the project", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    project_query = db.query(Project).filter(
        Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.author_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    tag = db.query(Tag).filter(Tag.tag_name == tag_request.tag_name).first()
    if tag in project.tags:
        raise HTTPException(
            status_code=409, detail="Tag already exists in project")
    if not tag:
        tag = Tag(tag_name=tag_request.tag_name)
        db.add(tag)
        db.commit()
    project.tags.append(tag)
    db.commit()
    return project


@router.delete('/{project_id}/tags/{tag_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_project(user: user_dependency, db: db_dependency, project_id: int = Path(..., title="The ID of the project", ge=1), tag_id: int = Path(..., title="The ID of the tag", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    project_query = db.query(Project).filter(
        Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.author_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    tag_query = db.query(Tag).filter(Tag.id == tag_id)
    tag = tag_query.first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    try:
        project.tags.remove(tag)
        db.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")


@router.post('/{project_id}/images', status_code=status.HTTP_201_CREATED)
def uplode_image(user: user_dependency, db: db_dependency, project: project_not_submited_dependency, project_id: int = Path(..., title="The ID of the project", ge=1), image: UploadFile = File(...)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if project.author_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    image_name = save_image(image)
    db.add(ProjectImage(image_url=image_name, project_id=project_id))
    db.commit()
    return {'image_url': f"{SERVER_ADDRESS}/image-content/{image_name}"}


@router.delete('/{project_id}/images/{image_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_image(user: user_dependency, project: project_not_submited_dependency, db: db_dependency, project_id: int = Path(..., title="The ID of the project", ge=1), image_id: int = Path(..., title="The ID of the image")):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if project.author_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    delete_project_image(image_id=image_id, project_id=project_id, db=db)


@router.post('/{project_id}/members/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def add_member_to_project(user: user_dependency, project: project_not_submited_dependency, db: db_dependency, project_id: int = Path(..., title="The ID of the project", ge=1), user_id: int = Path(..., title="The ID of the user", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if project.author_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id, ProjectMember.user_id == user_id).first()
    if member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already in project")

    new_team_member = db.query(User).filter(User.id == user_id).first()
    if not new_team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not new_team_member.verified or new_team_member.baned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not available for project participation")

    db.add(ProjectMember(project_id=project_id, user_id=user_id))
    db.commit()


@router.post('/{project_id}/submit/{hackathon_id}', status_code=status.HTTP_204_NO_CONTENT)
async def submit_project(user: user_dependency, project: project_not_submited_dependency, db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1), project_id: int = Path(..., title="The ID of the project", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    if project.author_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")

    if hackathon.end_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Hackathon has ended")

    if not project.are_members_participating(db, hackathon_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not all team members are participating")

    submit_project_to_hackathon(db, user.get('id'), hackathon_id, project_id)
