
from groq import Groq

from app.core.config import settings


def get_groq_client() -> Groq:
    """
    Create and return an authenticated Groq client.
    """

    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Please check your backend .env file."
        )

    return Groq(
        api_key=settings.GROQ_API_KEY,
        timeout=30.0,
        max_retries=2,
    )

groq_client = get_groq_client()
