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
        st.subheader("Image Generation")

        # Master switch
        enable_img = st.toggle("Enable Image Generation", value=False, key="master_img")

        if enable_img:
            # 1. Define Callback Functions to manage mutual exclusivity
            def select_free():
                st.session_state.best_active = False
                st.session_state.good_active = False

            def select_good():
                st.session_state.free_active = False
                st.session_state.best_active = False

            def select_best():
                st.session_state.free_active = False
                st.session_state.good_active = False

            # 2. Initialize Session States for toggles
            if "free_active" not in st.session_state: st.session_state.free_active = True
            if "good_active" not in st.session_state: st.session_state.good_active = False
            if "best_active" not in st.session_state: st.session_state.best_active = False

            # 3. Create the Toggles
            st.toggle("Free (Illustration)", key="free_active", on_change=select_free)
            st.toggle("Good Quality ($0.02)", key="good_active", on_change=select_good)
            st.toggle("Best Quality ($0.06)", key="best_active", on_change=select_best)

            # 4. Final Quality Mapping
            if st.session_state.best_active:
                quality_choice = "Best ($0.06)"
                st.success("💎 Premium: Imagen 4.0 Ultra")
            elif st.session_state.good_active:
                quality_choice = "Good ($0.02)"
                st.warning("💰 Paid: Imagen 4.0 Fast")
            elif st.session_state.free_active:
                quality_choice = "Free (Illustration)"
                st.info("✨ Free: Gemini 3.0 Flash")
            else:
                quality_choice = None
        else:
            quality_choice = None
            st.info("💡 Text-only mode active.")

        st.divider()

        st.subheader("Manage Topics")
        new_topic = st.text_input("Add a new topic:")
        if st.button("Add"):
            if new_topic and new_topic not in st.session_state.custom_topics:
                st.session_state.custom_topics.append(new_topic)
                st.rerun()

    # --- MAIN UI ---
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.selectbox("Topic", st.session_state.custom_topics, key="sel_topic")
    with col_b:
        st.selectbox("Length", ["Short", "Medium", "Long"], key="sel_length")
    with col_c:
        st.selectbox("Language", ["English"], key="sel_lang")

    if st.button("Generate Post", type="primary", use_container_width=True):
        with st.spinner("Crafting your post..."):
            # 1. Generate text (Always)
            # We pass quality_choice to decide if we even need an image prompt
            post, prompt = generate_draft(
                st.session_state.sel_length,
                st.session_state.sel_lang,
                st.session_state.sel_topic,
                quality_tier=quality_choice  # This can now be None
            )
            st.session_state.post_content = post
            st.session_state.image_prompt = prompt

            # 2. Conditional Image Generation
            if quality_choice:
                st.session_state.image_path = generate_final_image(prompt, quality_choice)
            else:
                st.session_state.image_path = None

        st.rerun()

    st.divider()

    # --- OUTPUT AREA ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📝 Ready-to-Post Text")
        st.session_state.post_content = st.text_area(
            "Edit your post:", value=st.session_state.post_content, height=400
        )
        if st.session_state.post_content:
            st.download_button("📥 Download Post (.txt)", st.session_state.post_content, "post.txt",
                               use_container_width=True)

    with col2:
        st.subheader("🎨 Image Studio")
        if st.session_state.image_path:
            st.image(st.session_state.image_path, use_container_width=True)
            with open(st.session_state.image_path, "rb") as f:
                st.download_button("💾 Download Graphic", f, "visual.png", use_container_width=True)

            st.divider()
            st.session_state.image_prompt = st.text_area("Refine Visual Prompt:", value=st.session_state.image_prompt)
            if st.button("🔄 Regenerate Image", use_container_width=True):
                st.session_state.image_path = generate_final_image(st.session_state.image_prompt, quality_choice)
                st.rerun()
        else:
            st.info("Visuals will appear here after generation.")


if __name__ == "__main__":
    main()