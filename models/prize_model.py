from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Prize(Base):
    __tablename__ = 'prizes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    hackathon_id = Column(Integer, ForeignKey(
        'hackathons.id', ondelete='CASCADE'))

    hackathon = relationship("Hackathon", back_populates="prizes")
