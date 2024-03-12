from sqlalchemy import Column, Integer, String, ForeignKey, and_
from sqlalchemy.orm import relationship, Session
from database import Base

from .particpant_model import Participant


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    tag_line = Column(String)
    about_project = Column(String)
    try_out_link = Column(String)
    video_link = Column(String)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    author = relationship("User", back_populates="projects")
    tags = relationship(
        "Tag",
        secondary="project_tags",
        back_populates="projects",
        lazy="joined",
    )
    images = relationship(
        "ProjectImage", back_populates="project", lazy="joined")
    team_members = relationship(
        "User", secondary="project_members", back_populates="member_projects")
    winners = relationship(
        "Winner", back_populates="project")
    submissions = relationship("Submission", back_populates="project")

    def update_from_dict(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def are_members_participating(self, db: Session, hackathon_id: int):
        team_member_ids = [member.id for member in self.team_members]
        team_member_ids.append(self.author_id)

        count = db.query(Participant).filter(
            and_(
                Participant.hackathon_id == hackathon_id,
                Participant.user_id.in_(team_member_ids),
                Participant.baned == False
            )
        ).count()

        return count == len(team_member_ids)

    def __repr__(self):
        return f"<Project {self.id} {self.name}>"
