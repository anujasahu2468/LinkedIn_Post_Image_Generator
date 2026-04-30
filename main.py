import os
import streamlit as st
from dotenv import load_dotenv
from post_generator import generate_draft, generate_final_image

load_dotenv()


def main():
    st.set_page_config(
        page_title="LinkedIn Post Studio", layout="wide", page_icon="📝"
    )
    st.title("🚀 LinkedIn Post & Visual Generator")

    defaults = {
        "custom_topics": ["AI in QA", "Engineering Leadership", "Software Testing"],
        "post_content": "",
        "image_prompt": "",
        "image_bytes": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        enable_img = st.toggle("Enable Image Generation", value=True, key="master_img")

        if enable_img:
            quality_choice = st.radio(
                "Image Quality",
                options=["Free (Illustration)", "Good (Infographic)", "Best (Photorealistic)"],
                index=0,
                help=(
                    "Free uses Gemini's built-in image model. "
                    "Good and Best use Imagen and require billing on your Google Cloud project."
                ),
            )
        else:
            quality_choice = None
            st.info("💡 Text-only mode active.")

        st.divider()
        st.subheader("Manage Topics")
        new_topic = st.text_input("Add a new topic:")
        if st.button("Add Topic"):
            if new_topic and new_topic not in st.session_state.custom_topics:
                st.session_state.custom_topics.append(new_topic)
                st.rerun()

        st.caption("Current topics:")
        for topic in st.session_state.custom_topics:
            col_t, col_x = st.columns([4, 1])
            col_t.write(topic)
            if col_x.button("✕", key=f"remove_{topic}"):
                st.session_state.custom_topics.remove(topic)
                st.rerun()

    # Input controls
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.selectbox("Topic", st.session_state.custom_topics, key="sel_topic")
    with col_b:
        st.selectbox("Length", ["Short", "Medium", "Long"], key="sel_length")
    with col_c:
        st.selectbox("Language", ["English", "Hindi", "Spanish"], key="sel_lang")

    if st.button("✨ Generate Content", type="primary", use_container_width=True):
        with st.spinner("Generating your post..."):
            post, prompt = generate_draft(
                length=st.session_state.sel_length,
                language=st.session_state.sel_lang,
                topic=st.session_state.sel_topic,
                quality_tier=quality_choice,
            )
            st.session_state.post_content = post
            st.session_state.image_prompt = prompt

        if enable_img and quality_choice:
            with st.spinner("Generating image..."):
                st.session_state.image_bytes = generate_final_image(
                    prompt, quality_choice
                )

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Text Studio")
        st.session_state.post_content = st.text_area(
            "Edit and finalize your copy:",
            value=st.session_state.post_content,
            height=400,
        )
        if st.session_state.post_content:
            st.download_button(
                "📥 Save as .txt",
                st.session_state.post_content,
                file_name="linkedin_post.txt",
                mime="text/plain",
            )

    with col2:
        st.subheader("🎨 Visual Studio")

        if st.session_state.image_bytes:
            st.image(st.session_state.image_bytes, use_container_width=True)

            st.download_button(
                "💾 Download Visual",
                data=st.session_state.image_bytes,
                file_name="visual.png",
                mime="image/png",
                use_container_width=True,
            )

            st.divider()
            st.session_state.image_prompt = st.text_area(
                "Refine image prompt:",
                value=st.session_state.image_prompt,
                key="refine_prompt",
            )

            if st.button("🔄 Regenerate Image Only", use_container_width=True):
                with st.spinner("Updating visual..."):
                    new_bytes = generate_final_image(
                        st.session_state.image_prompt, quality_choice
                    )
                    if new_bytes:
                        st.session_state.image_bytes = new_bytes
                st.rerun()

        elif enable_img:
            st.info("Generate content above to see your visual here.")
        else:
            st.warning("Image generation is disabled in settings.")


if __name__ == "__main__":
    main()