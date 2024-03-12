from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict

from typing import Optional


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    name: str
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @validator('confirm_password')
    def passwords_match(cls, confirm_password, values):
        if 'password' in values and values['password'] != confirm_password:
            raise ValueError('Password and confirm password must match')
        return confirm_password

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "username": "rajeshkumar",
                    "email": "rajeshkumar@example.com",
                    "password": "securepassword",
                    "confirm_password": "securepassword",
                    "name": "Rajesh Kumar"
                }
            ]
        }
    }


class UserPasswordVerificationRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @validator('confirm_password')
    def passwords_match(cls, confirm_password, values):
        print(values)
        if 'new_password' not in values or values['new_password'] != confirm_password:
            raise ValueError('Password and confirm password must match')
        return confirm_password

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "password": "securepassword",
                    "confirm_password": "securepassword",
                    "new_password": "securepassword",

                }
            ]
        }
    }


class UserSchema(BaseModel):
    id: int
    username: str
    name: str
    id: int

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [
        {
            "id": 1,
            "username": "rajeshkumar",
            "name": "Rajesh Kumar"
        }
    ]})


class UserPaginationSchema(BaseModel):
    total_users: int
    user_from: int
    current_total_users: int
    users: list[UserSchema]

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [
        {
            "total_users": 1,
            "user_from": 0,
            "current_total_users": 1,
            "users": [
                {
                    "id": 1,
                    "username": "rajeshkumar",
                    "name": "Rajesh Kumar"
                }
            ]
        }
    ]})


class FullUserSchema(UserSchema):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"examples": [
        {
            "id": 1,
            "username": "rajeshkumar",
            "name": "Rajesh Kumar",
            "email": "mail@mail.com"
        }
    ]})


class UsernameUpdateRequest(BaseModel):
    username: str

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "username": "rajeshkumar"
                }
            ]
        }
    }


class NameUpdateRequest(BaseModel):
    name: str

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "name": "Rajesh Kumar"
                }
            ]
        }
    }


class EmailRequest(BaseModel):
    email: EmailStr

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "email": "mail@mail.com"
                }
            ]
        }
    }
