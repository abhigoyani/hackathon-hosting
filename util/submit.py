from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from models import Project, Hackathon, Submission, Participant


def submit_project_to_hackathon(db: Session, user_id: int, hackathon_id: int, project_id: int):
    project_query = db.query(Project).filter(
        Project.id == project_id)
    project = project_query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    hackathon = db.query(Hackathon).filter(
        Hackathon.id == hackathon_id).first()

    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")

    if hackathon.start_date > datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Hackathon not started yet")
    if hackathon.end_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Hackathon already ended")

    participantion = db.query(Participant).filter(
        Participant.hackathon_id == hackathon_id, Participant.user_id == user_id).first()

    if not participantion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not participant in hackathon")

    submission = db.query(Submission).filter(
        Submission.project_id == project_id, Submission.hackathon_id == hackathon_id).first()

    if submission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Already submitted to hackathon")

    submission = Submission(
        project_id=project_id,
        hackathon_id=hackathon_id
    )
    db.add(submission)
    db.commit()
