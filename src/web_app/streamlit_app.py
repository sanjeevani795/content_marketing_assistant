import streamlit as st

from src.agents.query_handler import handle_query

st.set_page_config(page_title="Content Marketing Assistant", page_icon="🧠", layout="wide")
st.title("Content Marketing Assistant")
st.caption("Multi-agent conversational system for research, SEO blogs, LinkedIn posts, and image generation.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "runs" not in st.session_state:
    st.session_state.runs = []

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

user_input = st.chat_input("Ask for research, blog, LinkedIn, image, or a full campaign package")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Running multi-agent workflow..."):
            result = handle_query(user_input, st.session_state.chat_history)

        route = result.get("route", "unknown")
        outputs = result.get("outputs", {})
        quality = result.get("quality", {})

        st.markdown(f"**Route selected:** `{route}`")

        if outputs.get("research_report"):
            with st.expander("Research Report", expanded=True):
                st.json(outputs["research_report"])

        if outputs.get("seo_blog"):
            with st.expander("SEO Blog Draft", expanded=True):
                st.markdown(outputs["seo_blog"])

        if outputs.get("linkedin_post"):
            with st.expander("LinkedIn Post", expanded=True):
                st.markdown(outputs["linkedin_post"])

        image_asset = outputs.get("image_asset")
        if image_asset:
            with st.expander("Image Asset", expanded=True):
                st.markdown(f"**Prompt:** {image_asset.get('prompt', '')}")
                image_ref = image_asset.get("image", "")
                if image_ref.startswith("http") or image_ref.startswith("data:image"):
                    st.image(image_ref, caption="Generated visual")
                else:
                    st.code(image_ref)

        if quality:
            with st.expander("Quality Analysis", expanded=True):
                st.json(quality)

        st.session_state.runs.append(result)
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": f"Completed `{route}` workflow with quality score {quality.get('scores', {}).get('overall', 'N/A')}.",
            }
        )

with st.sidebar:
    st.subheader("Conversation")
    if st.button("Clear conversation"):
        st.session_state.chat_history = []
        st.session_state.runs = []
        st.rerun()

    if st.session_state.runs:
        st.download_button(
            "Download Last Run JSON",
            data=str(st.session_state.runs[-1]),
            file_name="content_run.json",
            mime="application/json",
        )
