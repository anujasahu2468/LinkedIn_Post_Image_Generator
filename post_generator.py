import os
import time
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

USE_VERTEX = os.getenv("USE_VERTEX", "false").lower() == "true"

if USE_VERTEX:
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )
else:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

TEXT_MODEL = "gemini-2.5-flash"
IMAGE_MODEL = "gemini-2.5-flash-image"


def generate_draft(length, language, topic, quality_tier):
    """
    Generates the LinkedIn post text and an image prompt.

    Returns:
        post_text (str): Plain-text LinkedIn post (no markdown).
        image_style (str): Prompt for the image generator, or "" if disabled.
    """
    post_prompt = (
        f"Write a {length} LinkedIn post in {language} about: {topic}.\n"
        "Tone: professional but warm and engaging. Include relevant emojis.\n"
        "IMPORTANT: Do not use any markdown formatting. "
        "No asterisks, hashtags, bold, italics, or bullet symbols. "
        "Use plain text only. Separate sections with blank lines."
    )

    # Retry up to 3 times on 503 (model overloaded — transient)
    post_text = "Could not generate post. The model is busy — please try again."
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=TEXT_MODEL,
                contents=post_prompt,
            )
            post_text = response.text
            break
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(3)
                continue
            st.error(f"Text generation failed: {e}")
            break

    if quality_tier is None:
        return post_text, ""

    if "Free" in quality_tier:
        image_style = (
            f"A minimalist 2D flat vector illustration about {topic}. "
            "Professional corporate colors, clean white background, no text."
        )
    elif "Good" in quality_tier:
        image_style = (
            f"A professional business infographic about {topic}. "
            "Flat vector style, clean corporate color palette, high contrast, "
            "minimalist icons, white background."
        )
    else:
        image_style = (
            f"A detailed, photorealistic visual concept representing {topic}. "
            "Cinematic lighting, sharp focus, professional composition, 4K quality."
        )

    return post_text, image_style


def generate_final_image(prompt, quality_tier):
    """
    Generates an image and returns raw PNG bytes.

    Returning bytes (not a file path) lets Streamlit display them directly
    via st.image(), avoiding all working-directory and path issues.

    Returns:
        bytes | None: PNG image bytes, or None on failure.
    """
    try:
        if "Free" in quality_tier:
            response = _generate_with_retry(prompt, max_retries=3)
            if response is None:
                return None

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return part.inline_data.data

            st.error("Model responded but returned no image data.")
            return None

        else:
            # Imagen models — require billing on Google Cloud
            model_id = (
                "imagen-3.0-fast-generate-001"
                if "Good" in quality_tier
                else "imagen-3.0-generate-002"
            )
            response = client.models.generate_images(
                model=model_id,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1),
            )
            return response.generated_images[0].image.data

    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None


def _generate_with_retry(prompt, max_retries=3):
    """Calls the image model with exponential backoff on transient 503 errors."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=IMAGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                ),
            )
        except Exception as e:
            is_last_attempt = attempt == max_retries - 1
            if is_last_attempt:
                raise

            wait = 2 ** attempt  # 1s, 2s, 4s
            st.toast(
                f"Model busy, retrying in {wait}s... (attempt {attempt + 1}/{max_retries})",
                icon="⏳",
            )
            time.sleep(wait)

    return None