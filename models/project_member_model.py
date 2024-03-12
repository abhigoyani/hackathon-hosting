from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base


class ProjectMember(Base):
    __tablename__ = 'project_members'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    __table_args__ = (UniqueConstraint(
        'project_id', 'user_id', name='uix_project_user'),)
