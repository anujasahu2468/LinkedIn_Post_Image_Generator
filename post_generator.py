import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize client using environment variable
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_draft(length, language, topic, quality_tier):
    """Generates the LinkedIn post text and a tier-specific image prompt."""

    # Use gemini-2.5-flash if gemini-3 is not yet appearing in your list
    TEXT_MODEL = "gemini-3-flash-preview"

    post_prompt = f"Write a {length} LinkedIn post in {language} about {topic}. Use professional but engaging tone with emojis."
    post_response = client.models.generate_content(model="gemini-3-flash-preview", contents=post_prompt)
    post_text = post_response.text

    if quality_tier is None:
        return post_text, ""

    # 2. Tier-specific Prompt Engineering
    if "Free" in quality_tier:
        image_style = f"A minimalist 2D vector illustration about {topic}, professional corporate colors, clean white background."
    elif "Good" in quality_tier:
        image_style = (
            f"A professional business infographic diagram about {topic}. "
            "Flat vector style, clean corporate color palette, high contrast, "
            "minimalist icons, white background, organized flowchart arrows."
        )
    else:  # Best
        image_style = (
            f"A detailed technical architecture diagram of {topic}. "
            "Professional engineering aesthetic, clean lines, crisp typography, "
            "legible text labels, high-contrast nodes, neutral background. 8k resolution."
        )
    return post_text, image_style


def generate_final_image(prompt, quality_tier):
    """Calls the correct Google model based on tier."""
    try:
        if "Free" in quality_tier:
            # Note: Multimodal generation requires specific model support
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_modalities=['IMAGE'])
            )
            image_bytes = response.candidates[0].content.parts[0].inline_data.data
        else:
            model_id = "imagen-3.0-generate-002"  # Fallback if 4.0 is locked
            if "Good" in quality_tier:
                model_id = "imagen-4.0-fast-generate-001"
            elif "Best" in quality_tier:
                model_id = "imagen-4.0-ultra-generate-001"

            response = client.models.generate_images(
                model=model_id,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1)
            )
            image_bytes = response.generated_images[0].image.data

        path = "generated_visual.png"
        with open(path, "wb") as f:
            f.write(image_bytes)
        return path

    except Exception as e:
        print(f"Error: {e}")
        return None