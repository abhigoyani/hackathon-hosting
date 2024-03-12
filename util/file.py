from fastapi import UploadFile, HTTPException
from uuid import uuid4
from starlette import status
import os

from models import ProjectImage


def save_image(image: UploadFile):
    if not image.content_type.startswith('image'):
        raise HTTPException(status_code=400, detail="File is not an image")

    # save image with jpeg and store it in project_images folder
    image_name = f'{uuid4()}.jpeg'
    with open(f'project_images/{image_name}', 'wb') as f:
        f.write(image.file.read())

    return image_name


def delete_project_image(image_id: int, project_id: int, db):
    print('project id', str(type(project_id)))
    print('image id', str(type(image_id)))
    # delete image from project_images folder
    try:
        image_queary = db.query(ProjectImage).filter(
            ProjectImage.id == image_id, ProjectImage.project_id == project_id)
        image_object = image_queary.first()
        if not image_object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        image_url = image_object.image_url
        image_queary.delete()
        db.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    # delete image from project_images folder
    try:
        print(f'project_images/{image_url}')
        print(os.path.exists(f'project_images/{image_url}'))
        os.remove(f'project_images/{image_url}')
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
