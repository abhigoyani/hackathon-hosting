from pydantic import BaseModel, validator, ConfigDict, model_validator
from typing import Optional
from datetime import datetime, timezone
from .user_schema import UserSchema
from .project_schema import ProjectSchema


class HackthonCreateRequest(BaseModel):
    name: str
    description: str
    detailed_description: str
    start_date: datetime
    end_date: datetime
    last_registration_date: datetime
    max_participant: int

    @validator('start_date', 'end_date', 'last_registration_date')
    def date_must_be_in_future(cls, v):
        if (v.tzinfo is None and v < datetime.now()) or (v.tzinfo is not None and v < datetime.now(timezone.utc)):
            raise ValueError('date must be in the future')
        return v

    @model_validator(mode='after')
    def dates_validation(self) -> 'HackthonCreateRequest':
        if self.start_date >= self.end_date:
            raise ValueError('start_date must be before end_date')
        if self.last_registration_date >= self.end_date:
            raise ValueError('last_registration_date must be before end_date')
        return self

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "name": "Hackathon 1",
                    "description": "This is a hackathon",
                    "detailed_description": "This is a detailed description",
                    "start_date": "2024-03-08T08:47:48.564",
                    "end_date": "2024-03-30T08:47:48.564",
                    "last_registration_date": "2024-03-30T00:00:00",
                    "max_participant": 100,
                }
            ]
        }
    }


class HackthonPatchRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    last_registration_date: Optional[datetime] = None
    max_participant: Optional[int] = None

    @validator('start_date', 'end_date', 'last_registration_date')
    def date_must_be_in_future(cls, v):
        if (v.tzinfo is None and v < datetime.now()) or (v.tzinfo is not None and v < datetime.now(timezone.utc)):
            raise ValueError('date must be in the future')
        return v

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "name": "Hackathon 1",
                    "description": "This is a hackathon",
                    "detailed_description": "This is a detailed description",
                    "start_date": "2024-03-08T08:47:48.564",
                    "end_date": "2024-03-30T08:47:48.564",
                    "last_registration_date": "2024-03-30T00:00:00",
                    "max_participant": 100,
                }
            ]
        }
    }


class HackthonSchema(BaseModel):
    id: int
    name: str
    description: str
    detailed_description: str
    start_date: datetime
    end_date: datetime
    last_registration_date: datetime
    max_participant: int
    organizer: UserSchema

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [
        {
            "id": 1,
            "name": "Hackathon 1",
            "description": "This is a hackathon",
            "detailed_description": "This is a detailed description",
            "start_date": "2024-03-08T08:47:48.564",
            "end_date": "2024-03-30T08:47:48.564",
            "last_registration_date": "2024-03-30T00:00:00",
            "max_participant": 100,
            "organizer": UserSchema.model_config['json_schema_extra']['examples'][0]
        }
    ]})


class HackthonPaginationSchema(BaseModel):
    total_hackathon: int
    hackathon_from: int
    current_total_hackathon: int
    hackathon: list[HackthonSchema]

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [
        {
            "total_hackathon": 20,
            "hackathon_from": 0,
            "current_total_hackathon": 5,
            "hackathon": [
                HackthonSchema.model_config['json_schema_extra']['examples'][0]
            ]
        }
    ]})


class SubmissionSchema(BaseModel):
    id: int
    project: ProjectSchema

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [
        {
            "id": 1,
            "project": ProjectSchema.model_config['json_schema_extra']['examples'][0],
            "hackathon": HackthonSchema.model_config['json_schema_extra']['examples'][0]
        }
    ]})


class ParticipantSchema(BaseModel):
    id: int
    user: UserSchema


class OrganizerPartcipantSchema(ParticipantSchema):
    baned: bool
