import streamlit as st

from src.agents.query_handler import handle_query
from src.core.observability import langsmith_project_name, tracing_enabled

st.set_page_config(page_title="Content Marketing Assistant", page_icon="🧠", layout="wide")
st.title("Content Marketing Assistant")
st.caption("Multi-agent conversational system for research, SEO blogs, LinkedIn posts, and image generation.")


def render_research_report(report: dict) -> None:
    summary = report.get("summary")
    findings = report.get("findings", [])
    sources = report.get("sources", [])
    provider = report.get("provider", "unknown")

    st.markdown(f"**Provider:** `{provider}`")

    if summary:
        st.markdown("### Summary")
        st.markdown(summary)

    if findings:
        st.markdown("### Key Findings")
        for finding in findings:
            if finding:
                st.markdown(f"- {finding}")

    if sources:
        st.markdown("### Sources")
        for source in sources:
            title = source.get("title", "Untitled source")
            url = source.get("url", "")
            snippet = source.get("snippet", "")
            if url:
                st.markdown(f"- [{title}]({url})")
            else:
                st.markdown(f"- {title}")
            if snippet:
                st.caption(snippet)

def render_quality_analysis(quality: dict) -> None:
    scores = quality.get("scores", {})
    improvements = quality.get("improvements", [])
    metrics = quality.get("metrics", {})
    thresholds = quality.get("thresholds", {})
    review_required = quality.get("review_required", {})

    if scores:
        st.markdown("### Scores")
        ordered = [("overall", "Overall"), ("research", "Research"), ("blog", "Blog"), ("linkedin", "LinkedIn")]
        for key, label in ordered:
            if key in scores:
                st.markdown(f"- **{label}:** {scores[key]}")

    review_items = []
    for key, label in [("blog", "Blog"), ("linkedin", "LinkedIn"), ("research", "Research")]:
        if review_required.get(key):
            threshold = thresholds.get(key)
            if threshold is not None:
                review_items.append(f"{label} score is below the review threshold of {int(threshold)}.")
            else:
                review_items.append(f"{label} score needs review.")

    if review_items:
        st.warning("Human review recommended for this run.")
        for item in review_items:
            st.markdown(f"- {item}")

    if improvements:
        st.markdown("### Suggested Improvements")
        for item in improvements:
            st.markdown(f"- {item}")

    if metrics:
        st.markdown("### Metrics")
        st.json(metrics)


def render_execution_notes(result: dict) -> None:
    route_source = result.get("route_source", "query")
    routing_details = result.get("routing_details", {})
    errors = result.get("errors", [])

    st.caption(f"Routing source: `{route_source}`")
    if result.get("ambiguity_detected"):
        st.info("The request looked ambiguous, so the router used conversation history or a safe fallback path.")

    if routing_details.get("last_route"):
        st.caption(f"Last routed agent in history: `{routing_details['last_route']}`")

    if errors:
        st.warning("One or more agents hit an error and switched to fallback behavior.")
        with st.expander("Execution errors", expanded=False):
            for item in errors:
                st.markdown(f"- {item}")


def review_target(result: dict) -> str:
    route = result.get("route")
    outputs = result.get("outputs", {})
    if route == "blog" or outputs.get("seo_blog"):
        return "blog"
    if route == "linkedin" or outputs.get("linkedin_post"):
        return "linkedin"
    return ""


def append_assistant_summary(result: dict) -> None:
    quality = result.get("quality", {})
    route = result.get("route", "unknown")
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": f"Completed `{route}` workflow with quality score {quality.get('scores', {}).get('overall', 'N/A')}.",
        }
    )


def run_revision(notes: str) -> None:
    if not st.session_state.runs:
        return

    prior_run = st.session_state.runs[-1]
    target = review_target(prior_run) or prior_run.get("route", "content")
    revision_prompt = f"Revise this {target} draft with the following human review notes: {notes}"

    st.session_state.chat_history.append({"role": "user", "content": revision_prompt})
    result = handle_query(
        revision_prompt,
        st.session_state.chat_history,
        prior_run=prior_run,
    )
    result["human_review"] = {"status": "revised", "notes": notes}
    st.session_state.runs.append(result)
    append_assistant_summary(result)
    st.session_state.review_mode = False
    st.session_state.review_notes = ""
    st.rerun()


def render_review_controls(result: dict) -> None:
    target = review_target(result)
    if target not in {"blog", "linkedin"}:
        return

    review_record = result.get("human_review", {})
    status = review_record.get("status", "pending")
    if status != "pending":
        st.caption(f"Human review status: `{status}`")
        if review_record.get("notes"):
            st.markdown(f"**Review notes:** {review_record['notes']}")
        return

    st.markdown("### Human Review")
    cols = st.columns(3)

    if cols[0].button("Approve", use_container_width=True):
        result["human_review"] = {"status": "approved", "notes": ""}
        st.session_state.review_mode = False
        st.session_state.review_notes = ""
        st.rerun()

    if cols[1].button("Revise", use_container_width=True):
        st.session_state.review_mode = True

    if cols[2].button("Reject", use_container_width=True):
        result["human_review"] = {"status": "rejected", "notes": ""}
        st.session_state.review_mode = False
        st.session_state.review_notes = ""
        st.rerun()

    if st.session_state.get("review_mode"):
        st.session_state.review_notes = st.text_area(
            "Reviewer notes",
            value=st.session_state.get("review_notes", ""),
            placeholder="Example: Tighten the opening, shorten the middle, and end with a stronger CTA.",
        )
        if st.button("Submit Revision Request", type="primary"):
            notes = st.session_state.get("review_notes", "").strip()
            if notes:
                run_revision(notes)
            else:
                st.warning("Add reviewer notes before submitting a revision request.")


def render_result(result: dict) -> None:
    route = result.get("route", "unknown")
    outputs = result.get("outputs", {})
    quality = result.get("quality", {})

    st.markdown(f"**Route selected:** `{route}`")
    render_execution_notes(result)

    if outputs.get("safety_response"):
        st.error(outputs["safety_response"])

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
            render_quality_analysis(quality)

    render_review_controls(result)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "runs" not in st.session_state:
    st.session_state.runs = []
if "review_mode" not in st.session_state:
    st.session_state.review_mode = False
if "review_notes" not in st.session_state:
    st.session_state.review_notes = ""

for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

if st.session_state.runs:
    st.subheader("Latest Output")
    render_result(st.session_state.runs[-1])

user_input = st.chat_input("Ask for research, blog, LinkedIn, image, or a full campaign package")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Running multi-agent workflow..."):
            result = handle_query(
                user_input,
                st.session_state.chat_history,
                prior_run=st.session_state.runs[-1] if st.session_state.runs else None,
            )
        result["human_review"] = {"status": "pending", "notes": ""}
        st.session_state.runs.append(result)
        append_assistant_summary(result)
        st.session_state.review_mode = False
        st.session_state.review_notes = ""
        st.rerun()

with st.sidebar:
    st.subheader("Conversation")
    st.caption(
        f"LangSmith tracing: `{'enabled' if tracing_enabled() else 'disabled'}`"
        f" | project: `{langsmith_project_name()}`"
    )
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
