from datetime import datetime

from sqlalchemy.orm import Query, Session, joinedload

from models import Hackathon, Project, Tag, Winner, Submission, ProjectTags
from sqlalchemy import or_, and_, not_, any_


def hackathon_filters(query: Query, ended: bool = False, ongoing: bool = False, upcoming: bool = False, registration_open: bool = False, registration_ended: bool = False):

    conditions = []

    if ended is not None:
        condition = Hackathon.end_date < datetime.now()
        if ended:
            conditions.append(condition)
        else:
            conditions.append(not_(condition))
    if ongoing is not None:
        condition = and_(Hackathon.start_date <=
                         datetime.now(), Hackathon.end_date >= datetime.now())
        if ongoing:
            conditions.append(condition)
        else:
            conditions.append(not_(condition))
    if upcoming is not None:
        condition = Hackathon.start_date > datetime.now()
        if upcoming:
            conditions.append(condition)
        else:
            conditions.append(not_(condition))
    if registration_ended is not None:
        condition = Hackathon.last_registration_date < datetime.now()
        if registration_ended:
            conditions.append(condition)
        else:
            conditions.append(not_(condition))

    if registration_open is not None:
        condition = Hackathon.last_registration_date > datetime.now()
        if registration_open:
            conditions.append(condition)
        else:
            conditions.append(not_(condition))

    query = query.filter(or_(*conditions))
    return query


def filter_projects(db: Session, tags=None, winner=None):
    query = db.query(Project)

    if tags:
        query = query.join(Project.tags).filter(
            or_(Tag.tag_name == tag for tag in tags))

    if winner is not None:
        query = query.join(Project.winners).filter(Winner.id.isnot(
            None)) if winner else query.filter(~Project.winners.any())

    return query


def hackathons_submission_filter(db: Session, tags=None, winner=None, hackathon_id: int = None):
    queary = db.query(Submission).options(joinedload(Submission.project)).filter(
        Submission.hackathon_id == hackathon_id)

    if tags:
        queary = queary.filter(Submission.project.has(Project.tags.any(
            or_(Tag.tag_name == tag for tag in tags))))

    if winner is not None:
        queary = queary.filter(Submission.project.has(Project.winners.any(
        ))) if winner else queary.filter(~Submission.project.has(Project.winners.any()))

    return queary
