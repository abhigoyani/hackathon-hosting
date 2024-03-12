import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ.get('DB_URL')

SECRET_KEY = os.environ.get('SECRET_KEY')
ALOGIRITHM = "HS256"
PER_PAGE_LIMIT = 10


SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS')

MAILGUN_DOMAIN = "dev.kevalvavaliya.me"
MAILGUN_FROM_EMAIL = f"verify@{MAILGUN_DOMAIN}"
MAILGUN_API_ENDPOINT = F"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY_NEW')

REDIS_URL = os.environ.get('REDIS_URL')
