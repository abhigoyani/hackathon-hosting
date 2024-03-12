from database import Base

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class Winner(Base):
    __tablename__ = 'winners'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    submission_id = Column(Integer, ForeignKey(
        'submissions.id', ondelete='CASCADE'))
    prize_id = Column(Integer, ForeignKey('prizes.id', ondelete='CASCADE'))

    project = relationship("Project", back_populates="winners")
    submission = relationship("Submission", back_populates="winners")
