from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True, index=True)
    hackathon_id = Column(Integer, ForeignKey(
        'hackathons.id', ondelete='CASCADE'))
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    baned = Column(Boolean, default=False)

    hackathon = relationship("Hackathon", back_populates="submissions")
    winners = relationship("Winner",
                           back_populates="submission")
    project = relationship(
        "Project", back_populates="submissions", lazy="joined")
