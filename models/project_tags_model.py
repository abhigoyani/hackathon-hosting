from sqlalchemy import Column, Integer, ForeignKey
from database import Base


class ProjectTags(Base):
    __tablename__ = 'project_tags'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'))
