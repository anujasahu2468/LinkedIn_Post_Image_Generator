import streamlit as st
from post_generator import generate_draft, generate_final_image


def main():
    st.set_page_config(page_title="LinkedIn Post Studio", layout="wide", page_icon="📝")
    st.title("🚀 LinkedIn Post & Visual Generator")

    # Persistent Custom Topics
    if "custom_topics" not in st.session_state:
        st.session_state.custom_topics = ["AI in QA", "Engineering Leadership", "Software Testing"]

    # Session States for persistence
    if "post_content" not in st.session_state: st.session_state.post_content = ""
    if "image_prompt" not in st.session_state: st.session_state.image_prompt = ""
    if "image_path" not in st.session_state: st.session_state.image_path = None

    # --- SIDEBAR: Settings ---
    with st.sidebar:
        st.header("⚙️ App Settings")
        enable_visuals = st.toggle("Enable Paid Visuals (Imagen 4 Fast)", value=False)
        if enable_visuals:
            st.warning("💰 **Paid Feature:** Each image costs **$0.02**.")

        st.divider()
        st.subheader("Manage Topics")
        new_topic = st.text_input("Add a new topic:")
        if st.button("Add"):
            if new_topic and new_topic not in st.session_state.custom_topics:
                st.session_state.custom_topics.append(new_topic)
                st.rerun()

    # --- MAIN UI: Dropdowns ---
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.selectbox("Topic", st.session_state.custom_topics, key="sel_topic")
    with col_b:
        st.selectbox("Length", ["Short", "Medium", "Long"], key="sel_length")
    with col_c:
        st.selectbox("Language", ["English"], key="sel_lang")

    # GENERATE BUTTON: Now optimized for Text-Only vs Multimodal
    if st.button("Generate Post", type="primary", use_container_width=True):
        with st.spinner("Crafting your post..."):
            # logic: Pass enable_visuals to the generator to skip prompt gen if not needed
            post, prompt = generate_draft(
                st.session_state.sel_length,
                st.session_state.sel_lang,
                st.session_state.sel_topic,
                generate_image_prompt=enable_visuals  # New logic flag
            )
            st.session_state.post_content = post
            st.session_state.image_prompt = prompt

            if enable_visuals and prompt:
                st.session_state.image_path = generate_final_image(prompt)
            else:
                st.session_state.image_path = None
        st.rerun()

    st.divider()

    # --- OUTPUT AREA ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Ready-to-Post Text")
        # Editable text area
        st.session_state.post_content = st.text_area(
            "Copy and paste this into LinkedIn:",
            value=st.session_state.post_content,
            height=450
        )

        # DOWNLOAD BUTTON for the Text Post
        if st.session_state.post_content:
            st.download_button(
                label="📥 Download Post (.txt)",
                data=st.session_state.post_content,
                file_name=f"linkedin_post_{st.session_state.sel_topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    with col2:
        st.subheader("🎨 Image Studio")
        if st.session_state.post_content:
            if st.session_state.image_path:
                st.image(st.session_state.image_path, use_container_width=True)
                with open(st.session_state.image_path, "rb") as f:
                    st.download_button("💾 Download Graphic", f, "visual.png", use_container_width=True)

            elif enable_visuals:
                st.error("Image generation failed. Verify billing.")

            else:
                st.info("✨ Text-only mode active. Toggle 'Enable Paid Visuals' to add a graphic.")

            # If an image was generated, allow prompt adjustment
            if st.session_state.image_prompt:
                st.divider()
                st.session_state.image_prompt = st.text_area("Refine Visual Style:",
                                                             value=st.session_state.image_prompt)
                if st.button("🔄 Regenerate Image ($0.02)", use_container_width=True):
                    st.session_state.image_path = generate_final_image(st.session_state.image_prompt)
                    st.rerun()
        else:
            st.info("Your generated post will appear here.")


if __name__ == "__main__":
    main()