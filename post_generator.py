from google import genai
from google.genai import types
import streamlit as st

# Initialize client (uses streamlit secrets)
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])


def generate_draft(length, language, topic, quality_tier):
    """Generates the LinkedIn post text and a tier-specific image prompt."""

    # 1. Generate Post Text
    post_prompt = f"Write a {length} LinkedIn post in {language} about {topic}. Use professional but engaging tone with emojis."
    post_response = client.models.generate_content(model="gemini-3-flash-preview", contents=post_prompt)
    post_text = post_response.text

    # If user chose 'None' (text-only), return an empty prompt
    if quality_tier is None:
        return post_text, ""

    # If user chose 'None' (text-only), return an empty prompt
    if quality_tier is None:
        return post_text, ""

    # 2. Tier-specific Prompt Engineering
    if "Free" in quality_tier:
        image_style = f"A minimalist 2D vector illustration about {topic}, professional corporate colors, clean white background."
    elif "Good" in quality_tier:
        # Good Tier ($0.02)
        # Good Tier: Focus on 'Infographic' style.
        # Clean, flat, and professional, but less detail on text.
        image_style = (
            f"A professional business infographic diagram about {topic}. "
            "Flat vector style, clean corporate color palette (blues and grays), "
            "high contrast, minimalist icons, clear white background. "
            "Organized layout with simple flowchart arrows."
        )
    else:
        # Best Tier ($0.06)
        # Best Tier: Focus on 'Technical Accuracy' and 'Typography'.
        # Uses 'Imagen 4 Ultra' logic to ensure readable text and complex nodes.
        image_style = (
            f"A detailed technical architecture diagram of {topic}. "
            "Professional engineering aesthetic, clean lines, crisp typography, "
            "legible text labels, high-contrast nodes and connections. "
            "Isolate on a neutral light background. 8k resolution, "
            "photorealistic print-quality graphics, highly structured and logical."
        )
    return post_text, image_style


def generate_final_image(prompt, quality_tier):
    """Calls the correct Google model based on tier and saves the image."""
    try:
        if "Free" in quality_tier:
            # Free tier uses the multimodal capabilities of Gemini 3 Flash
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(response_modalities=['IMAGE'])
            )
            image_bytes = response.candidates[0].content.parts[0].inline_data.data

        else:
            # Paid tiers use specialized Imagen models
            model_id = "imagen-4.0-fast-generate-001" if "Good" in quality_tier else "imagen-4.0-ultra-generate-001"
            response = client.models.generate_images(
                model=model_id,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1)
            )
            image_bytes = response.generated_images[0].image.data

        # Save locally for Streamlit to display
        path = "generated_visual.png"
        with open(path, "wb") as f:
            f.write(image_bytes)
        return path

    except Exception as e:
        print(f"Image generation error: {e}")
        return None