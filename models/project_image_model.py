from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class ProjectImage(Base):
    __tablename__ = 'project_images'

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'))

    project = relationship("Project", back_populates="images")
