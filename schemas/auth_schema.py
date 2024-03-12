from pydantic import BaseModel, EmailStr, validator, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class ForgotPasswordRequest(BaseModel):
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @validator('confirm_password')
    def passwords_match(cls, confirm_password, values):
        if values['password'] != confirm_password:
            raise ValueError('Password and confirm password must match')
        return confirm_password

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "password": "securepassword",
                    "confirm_password": "securepassword"
                }
            ]
        }
    }


class EmailSentResponse(BaseModel):
    email_sent_to: EmailStr
    message: str

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "email_sent_to": "youremail@mail.com",
                    "message": "verification Email sent successfully"},
            ],
        }
    }


class ResendVerificationEmailRequest(BaseModel):
    email: EmailStr

    model_config = {
        'json_schema_extra': {
            "examples": [
                {
                    "email": "youremail@mail.com",
                },
            ],
        }
    }
