from typing import List, Annotated
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, Path
from starlette import status
from sqlalchemy import and_

from util.db import db_dependency
from util.auth import user_dependency
from util.filter import hackathon_filters, hackathons_submission_filter
from schemas.hackathon_schema import HackthonCreateRequest, HackthonPatchRequest, HackthonSchema, HackthonPaginationSchema, SubmissionSchema, ParticipantSchema
from schemas.user_schema import UserSchema
from models import Participant, Submission, Hackathon, User
from config import PER_PAGE_LIMIT

router = APIRouter(
    prefix='/hackathon',
    tags=['hackathon']
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=HackthonPaginationSchema, description="Get all hackthons")
def get_hackathons(db: db_dependency,
                   page: int = Query(1, ge=1),
                   ended: bool = Query(None),
                   ongoing: bool = Query(None),
                   upcoming: bool = Query(None),
                   registration_open: bool = Query(None),
                   registration_ended: bool = Query(None)
                   ):
    query = db.query(Hackathon)
    query = hackathon_filters(query, ended, ongoing, upcoming,
                              registration_open, registration_ended)
    total = query.count()
    query = query.limit(PER_PAGE_LIMIT).offset((page-1)*PER_PAGE_LIMIT)

    response = {
        "total_hackathon": total,
        "hackathon_from": (page-1)*PER_PAGE_LIMIT,
        "current_total_hackathon": query.count(),
        "hackathon": query.all()
    }
    print(response)
    return response


@router.post('/', status_code=status.HTTP_200_OK)
def create_hackathon(user: user_dependency, db: db_dependency, hackathon_request: HackthonCreateRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    hackathon = Hackathon(
        organizer_id=user.get('id'),
        **hackathon_request.model_dump(),
    )
    db.add(hackathon)
    db.commit()
    return hackathon


@router.get('/{hackathon_id}', status_code=status.HTTP_200_OK, response_model=HackthonSchema, description="Get a hackthon by id")
def get_hackathon(db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1)):
    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return hackathon


@router.patch('/{hackathon_id}', status_code=status.HTTP_204_NO_CONTENT, description="Update a hackthon by id")
def update_hackathon(hackathon_request: HackthonPatchRequest, user: user_dependency, db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    hackathon_query = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id)
    hackathon = hackathon_query.first()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    if hackathon.organizer_id != user.get('id'):
        raise HTTPException(status_code=403, detail="Forbidden")
    hackathon_query.update(hackathon_request.model_dump(exclude_none=True))
    db.commit()
    return hackathon


@router.delete('/{hackathon_id}', status_code=status.HTTP_204_NO_CONTENT, description="Delete a hackthon by id")
def delete_hackathon(user: user_dependency, db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    hackathon_query = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id)
    hackathon = hackathon_query.first()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    if (hackathon.organizer_id != user.get('id')) and (not user.get('admin')):
        raise HTTPException(status_code=403, detail="Forbidden")
    hackathon_query.delete()
    db.commit()


@router.post('/{hackathon_id}/join', status_code=status.HTTP_200_OK, description="Join a hackthon by id")
async def join_hackathon(user: user_dependency, db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")

    if hackathon.last_registration_date < datetime.now():
        raise HTTPException(
            status_code=403, detail="Registration period ended")

    if hackathon.max_participant and hackathon.participants.count() >= hackathon.max_participant:
        raise HTTPException(
            status_code=403, detail="Hackathon is full")

    participant = db.query(Participant).filter(Participant.user_id == user.get(
        'id'), Participant.hackathon_id == hackathon_id).first()
    if participant:
        raise HTTPException(status_code=400, detail="Already joined")
    participant = Participant(user_id=user.get('id'),
                              hackathon_id=hackathon_id)
    db.add(participant)
    db.commit()


@router.get('/{hackathon_id}/participants', status_code=status.HTTP_200_OK, response_model=List[ParticipantSchema], description="Get all participants of a hackthon by id")
def get_participants(db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1)):
    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return hackathon.participants.filter(Participant.baned == False).all()


@router.get('/{hackathon_id}/submissions', response_model=List[SubmissionSchema], status_code=status.HTTP_200_OK, description="Get all submissions of a hackthon by id")
def get_submissions(db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1), tags: Annotated[list[str] | None, Query()] = None, winner: bool = Query(None)):
    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    submissions = hackathons_submission_filter(
        db, tags, winner, hackathon_id).all()

    print('------usbmission------')
    print(submissions)

    return submissions
