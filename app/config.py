from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DEFAULT_USER')}:" \
    f"{os.getenv('DEFAULT_PASSWORD')}@" \
    f"{os.getenv('DEFAULT_HOST')}:{os.getenv('DEFAULT_PORT')}/" \
    f"{os.getenv('DEFAULT_DB')}"

MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_TLS = os.getenv('MAIL_TLS')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30