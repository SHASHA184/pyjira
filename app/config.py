from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DEFAULT_USER')}:" \
    f"{os.getenv('DEFAULT_PASSWORD')}@" \
    f"{os.getenv('DEFAULT_HOST')}:{os.getenv('DEFAULT_PORT')}/" \
    f"{os.getenv('DEFAULT_DB')}"
