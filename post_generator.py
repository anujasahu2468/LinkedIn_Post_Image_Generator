import os
import sqlite3
from dotenv import load_dotenv
from google import genai
from google.genai import types
from llm_helper import llm

load_dotenv()

# Initialize the 2026 GenAI Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_draft(length, language, topic, generate_image_prompt=False):
    # (Context database fetching logic remains here)

    # 1. Generate the LinkedIn Post (Polished and formatted)
    system_instruction = "You are a professional LinkedIn Ghostwriter. Use line breaks for readability. Start with a hook. End with 3 relevant hashtags. Ensure the post is grammatically perfect and ready to copy-paste."
    post_prompt = f"{system_instruction}\nWrite a {length} LinkedIn post about {topic} in {language}."

    post_text = llm.invoke(post_prompt).content
    image_prompt = ""

    # 2. Skip Image Prompt if not requested
    if generate_image_prompt:
        img_req = f"Write a 1-sentence prompt for a clean, professional 3D illustration for this topic: {topic}"
        image_prompt = llm.invoke(img_req).content

    return post_text, image_prompt


def generate_final_image(final_prompt):
    """
    Uses Imagen 4 (Fast) for $0.02 per generation.
    """
    try:
        response = client.models.generate_images(
            model='imagen-4.0-fast-generate-001',
            prompt=final_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                image_size="1K"
            )
        )
        image_path = "generated_image.png"
        response.generated_images[0].image.save(image_path)
        return image_path
    except Exception as e:
        print(f"Imagen 4 Fast Error: {e}")
        return None