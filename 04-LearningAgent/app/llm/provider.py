import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():

    return ChatGoogleGenerativeAI(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        ),
        temperature=0.2,
    )