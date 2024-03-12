from fastapi import Depends, HTTPException, Path
from typing import Annotated

from util.db import db_dependency
from models import Project


def project_not_submited(db: db_dependency, project_id: int = Path(...)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.submissions:
        raise HTTPException(
            status_code=400, detail="Project is already submitted")
    return project


project_not_submited_dependency = Annotated[Project, Depends(
    project_not_submited)]
