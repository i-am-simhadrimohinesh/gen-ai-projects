import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
)


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:

    raise RuntimeError(
        "DATABASE_URL environment variable is not set."
    )
if not GEMINI_MODEL:

    raise RuntimeError(
        "GEMINI_MODEL environment variable is not set."
    )