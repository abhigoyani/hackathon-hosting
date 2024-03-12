from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String, unique=True)

    projects = relationship(
        "Project",
        secondary="project_tags",
        back_populates="tags",
        lazy="dynamic",
    )
