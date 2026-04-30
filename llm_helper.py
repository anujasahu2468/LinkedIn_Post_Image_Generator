import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# gemini-2.0-flash is the current stable, fast model for text tasks.
# It supports structured output via .with_structured_output() and is
# available globally including through Vertex AI.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)