from database import Base


from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
# from user_model import User
# from hackathon_model import Hackathon


class Participant(Base):
    __tablename__ = 'participants'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hackathon_id = Column(Integer, ForeignKey(
        'hackathons.id', ondelete='CASCADE'))
    baned = Column(Boolean, default=False)

    user = relationship("User", back_populates="participants")
    hackathon = relationship("Hackathon", back_populates="participants")

    __table_args__ = (UniqueConstraint(
        'user_id', 'hackathon_id', name='uix_user_hackathon'),)
