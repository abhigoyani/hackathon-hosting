from typing import List
from fastapi import APIRouter, HTTPException, Path
from starlette import status
from sqlalchemy import and_
from models import Prize, Hackathon, Winner, Submission, Participant, Submission, Winner
from util.db import db_dependency
from util.auth import user_dependency
from schemas.prize_schema import PrizeCreateRequest, PrizePatchRequest
from schemas.hackathon_schema import OrganizerPartcipantSchema


router = APIRouter(
    prefix='/organizer',
    tags=['organizer']
)


@router.get('/{hackathon_id}/participants', status_code=status.HTTP_200_OK, response_model=List[OrganizerPartcipantSchema], description="Get all participants of a hackthon by id")
def get_participants(user: user_dependency, db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1)):
    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    if (not (hackathon.organizer_id == user.get('id'))) and (not user.get('is_admin')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to get participants')

    return hackathon.participants.all()


@router.post('/{hackathon_id}/participant/{participant_id}/ban', status_code=status.HTTP_200_OK)
async def ban_participant(user: user_dependency, db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1), participant_id: int = Path(..., title="The ID of the participant", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to ban participant')

    participant = db.query(Participant).filter(
        Participant.id == participant_id, Participant.hackathon_id == hackathon_id).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

    project_ids = [project.id for project in participant.user.projects.all()]
    project_ids += [project.id for project in participant.user.member_projects.all()]

    submission = db.query(Submission).filter(
        and_(
            Submission.project_id.in_(project_ids),
            Submission.hackathon_id == hackathon_id
        )
    ).first()
    participant.baned = True
    db.commit()
    print(participant.user.projects.all())
    if submission:
        print('submission : ', submission)
        return {
            "msg": "Participant banned",
            "participant_submission": submission.id
        }


@router.post('/{hackathon_id}/participant/{participant_id}/unban', status_code=status.HTTP_200_OK)
async def unban_participant(user: user_dependency, db: db_dependency, hackathon_id: int = Path(..., title="The ID of the hackathon", ge=1), participant_id: int = Path(..., title="The ID of the participant", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to unban participant')

    participant = db.query(Participant).filter(
        Participant.id == participant_id, Participant.hackathon_id == hackathon_id).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

    participant.baned = False
    db.commit()


@router.post('/{hacakthon_id}/submission/{submission_id}/ban', status_code=status.HTTP_204_NO_CONTENT)
async def ban_submission(user: user_dependency, db: db_dependency, hacakthon_id: int = Path(..., title="The ID of the hackathon", ge=1), submission_id: int = Path(..., title="The ID of the submission", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hacakthon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to ban submission')

    submission = db.query(Submission).filter(
        Submission.id == submission_id, Submission.hackathon_id == hacakthon_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    winner = db.query(Winner).filter(
        Winner.submission_id == submission_id).first()
    if winner:
        db.delete(winner)

    submission.baned = True

    db.commit()


@router.post('/{hacakthon_id}/submission/{submission_id}/unban', status_code=status.HTTP_204_NO_CONTENT)
async def unban_submission(user: user_dependency, db: db_dependency, hacakthon_id: int = Path(..., title="The ID of the hackathon", ge=1), submission_id: int = Path(..., title="The ID of the submission", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hacakthon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to unban submission')

    submission = db.query(Submission).filter(
        Submission.id == submission_id, Submission.hackathon_id == hacakthon_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    submission.baned = False
    db.commit()


@router.post('/{hacakthon_id}/prize', status_code=status.HTTP_200_OK)
async def create_prize(user: user_dependency, db: db_dependency, prize_request: PrizeCreateRequest, hacakthon_id: int = Path(..., title="The ID of the hackathon", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hacakthon_id).first()
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    prize = Prize(
        hackathon_id=hacakthon_id,
        **prize_request.model_dump(),
    )
    db.add(prize)
    db.commit()
    return prize


@router.patch('/{hacakthon_id}/prize/{prize_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_prize(user: user_dependency, db: db_dependency, prize_request: PrizePatchRequest, hacakthon_id: int = Path(..., title="The ID of the hackathon", ge=1), prize_id: int = Path(..., title="The ID of the prize", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    prize_queary = db.query(Prize).filter(
        Prize.id == prize_id, Prize.hackathon_id == hacakthon_id)
    prize = prize_queary.first()
    if not prize:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prize not found")

    if prize.hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to update prize')
    print(prize.hackathon.organizer_id)
    prize_queary.update(prize_request.model_dump(exclude_none=True))
    db.commit()


@router.delete('/{hacakthon_id}/prize/{prize_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_prize(user: user_dependency, db: db_dependency, hacakthon_id: int = Path(..., title="The ID of the hackathon", ge=1), prize_id: int = Path(..., title="The ID of the prize", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    prize_queary = db.query(Prize).filter(
        Prize.id == prize_id, Prize.hackathon_id == hacakthon_id)
    prize = prize_queary.first()
    if not prize:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prize not found")

    if prize.hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to delete prize')

    prize_queary.delete()
    db.commit()


@router.post('/{submission_id}/winner/prize/{prize_id}', status_code=status.HTTP_204_NO_CONTENT)
async def add_winner(user: user_dependency, db: db_dependency, prize_id: int = Path(..., title="The ID of the prize", ge=1), submission_id: int = Path(..., title="The ID of the submission", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    prize_queary = db.query(Prize).filter(
        Prize.id == prize_id)
    prize = prize_queary.first()

    if not prize:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prize not found")

    if prize.hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to add winner')

    submission = db.query(Submission).filter(
        Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    if submission.hackathon_id != prize.hackathon_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Submission not from {prize.hackathon.title}")

    if submission.baned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Submission is banned")

    if db.query(Winner).filter(Winner.submission_id == submission_id, Winner.prize_id == prize_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Submission already won {prize.title}")

    winner = Winner(
        submission_id=submission_id,
        prize_id=prize_id,
        project_id=submission.project_id
    )
    db.add(winner)
    db.commit()


@router.delete('/{submission_id}/winner/prize/{prize_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_winner(user: user_dependency, db: db_dependency, prize_id: int = Path(..., title="The ID of the prize", ge=1), submission_id: int = Path(..., title="The ID of the submission", ge=1)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    prize_queary = db.query(Prize).filter(
        Prize.id == prize_id)
    prize = prize_queary.first()

    if not prize:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prize not found")

    if prize.hackathon.organizer_id != user.get('id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to remove winner')

    submission = db.query(Submission).filter(
        Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    winner = db.query(Winner).filter(
        Winner.submission_id == submission_id, Winner.prize_id == prize_id).first()
    if not winner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Winner not found")

    db.delete(winner)
    db.commit()


# @router.post('/{submission_id}/ban', status_code=status.HTTP_204_NO_CONTENT)

# @router.post('/ban/submission/{submission_id}', status_code=status.HTTP_204_NO_CONTENT)
