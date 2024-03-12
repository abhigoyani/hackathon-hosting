from database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)  # Added nullable=False
    # Added nullable=False
    username = Column(String, unique=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    baned = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)

    hackathons_organized = relationship(
        "Hackathon", back_populates="organizer", lazy="dynamic")
    projects = relationship("Project", back_populates="author", lazy="dynamic")
    member_projects = relationship(
        "Project", secondary="project_members", back_populates="team_members", lazy="dynamic")
    # hackathons = relationship(
    #     "Hackathon", secondary="participants", back_populates="users", lazy="dynamic")
    participants = relationship(
        "Participant", back_populates="user", lazy="dynamic")
