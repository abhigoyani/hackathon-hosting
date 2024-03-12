from database import Base

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
# from user_model import User


class Hackathon(Base):
    __tablename__ = 'hackathons'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    detailed_description = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    last_registration_date = Column(DateTime, nullable=False)
    max_participant = Column(Integer, nullable=True)
    organizer_id = Column(Integer, ForeignKey(
        'users.id', ondelete='SET NULL'), nullable=True)

    organizer = relationship("User", back_populates="hackathons_organized")
    submissions = relationship(
        "Submission", back_populates="hackathon", lazy="dynamic")
    prizes = relationship("Prize", back_populates="hackathon")
    # users = relationship("User", secondary="participants",
    #                      back_populates="hackathons", lazy="dynamic")
    participants = relationship(
        "Participant", back_populates="hackathon", lazy="dynamic")

    def __repr__(self):
        return f"<Hackathon(id={self.id}, name={self.name}, organizer_id={self.organizer_id})>"
