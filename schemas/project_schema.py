from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict, model_validator
from schemas.user_schema import UserSchema
from typing import Optional, List
from pydantic import HttpUrl
from urllib.parse import urlparse


class TagSchema(BaseModel):
    id: int
    tag_name: str


class ProjectCreateRequest(BaseModel):
    name: Optional[str] = None
    tag_line: Optional[str] = None
    about_project: Optional[str] = None
    try_out_link: Optional[HttpUrl] = None
    video_link: Optional[HttpUrl] = None

    @model_validator(mode='after')
    def convert_urls(self):
        if self.try_out_link:
            self.try_out_link = str(self.try_out_link)
            domain = len(urlparse(self.try_out_link).netloc.split('.'))
            print(domain)
            if not domain >= 2:
                raise ValueError('Invalid URL')
        if self.video_link:
            self.video_link = str(self.video_link)
            domain = len(urlparse(self.video_link).netloc.split('.'))
            print(domain)
            if not domain >= 2:
                raise ValueError('Invalid URL')
        return self


class ImageSchema(BaseModel):
    id: int
    image_url: str


class ProjectSchema(ProjectCreateRequest):
    id: int
    tags: List[TagSchema]
    images: List[ImageSchema]
    team_members: List[UserSchema]

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "name": "Project 1",
                    "tag_line": "This is a tag line",
                    "about_project": "This is a detailed description",
                    "try_out_link": "https://www.google.com",
                    "video_link": "https://www.youtube.com",
                    "team_members": [
                        UserSchema.model_config['json_schema_extra']['examples'][0],
                    ]
                }
            ]}
    }


class ProjectPaginationSchema(BaseModel):
    total_projects: int
    project_from: int
    current_total_project: int
    projects: List[ProjectSchema]

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "total_projects": 100,
                    "project_from": 0,
                    "current_total_project": 10,
                    "projects": [
                        ProjectSchema.model_config['json_schema_extra']['examples'][0]
                    ]
                }
            ]
        }

    }


class AddTagRequest(BaseModel):
    tag_name: Optional[str] = None

    @model_validator(mode='after')
    def validate_tag(self):
        self.tag_name = self.tag_name.lower().strip()
        return self
