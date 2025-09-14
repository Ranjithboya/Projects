# pip install streamlit openai python-dotenv pyyaml

import streamlit as st
import time, json, yaml
from utils.model import build_prompt, generate_response
from utils.faq_loader import load_faq
from utils.config_loader import load_config
from utils.lead_persistence import save_lead
from utils.trace_logger import log_trace

# Hide Streamlit chrome
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("🔧 Configuration")

# 1️⃣ Optional upload: FAQ pack
uploaded_faq = st.sidebar.file_uploader("Upload FAQ JSON", type="json")
if uploaded_faq:
    try:
        faq_data = json.load(uploaded_faq)
        st.sidebar.success("Loaded FAQ pack")
    except Exception as e:
        st.sidebar.error(f"Invalid JSON: {e}")
else:
    faq_data = load_faq("data/faq_knowledge.json")

# 2️⃣ Optional upload: Bot config (lead fields, nudges, etc.)
uploaded_cfg = st.sidebar.file_uploader("Upload config YAML", type=["yml", "yaml"])
if uploaded_cfg:
    try:
        config = yaml.safe_load(uploaded_cfg)
        st.sidebar.success("Loaded config")
    except Exception as e:
        st.sidebar.error(f"Invalid YAML: {e}")
else:
    config = load_config("config/bot_config.yaml")

# Initialize session state
session = st.session_state
session.setdefault("chat_history", [])
session.setdefault("questions_asked", 0)
session.setdefault("show_lead_form", False)
session.setdefault("start_time", time.time())
session.setdefault("intent_shown", False)
session.setdefault("chat_enabled", False)

# App title
st.title("SalesbotAI 🤖 — Quick-Answer & Lead Capture")

# 🚩 Right-moment nudge: linger
elapsed = time.time() - session.start_time
if elapsed > config["nudges"]["linger_seconds"] and not session.intent_shown:
    st.info(config["nudges"]["linger_message"])
    session.intent_shown = True

# 💬 Reveal chat on intent
if session.intent_shown and not session.chat_enabled:
    if st.button(config["nudges"]["trigger_button_label"]):
        session.chat_enabled = True

# ——— CHAT WIDGET ———
if session.chat_enabled:
    user_q = st.chat_input("Ask your question…")
    if user_q:
        prompts = build_prompt(
            session.chat_history,
            user_q,
            faq_data=faq_data,
            page_context=session.get("current_page", None)
        )
        answer = generate_response(prompts)
        time.sleep(config["bot"]["response_delay"])  # natural pacing

        # Update history & trace
        session.chat_history.append({"user": user_q, "bot": answer})
        session.questions_asked += 1
        log_trace(user_q, answer)

        # Lead form after threshold
        if session.questions_asked >= config["lead"]["threshold"]:
            session.show_lead_form = True

    # Render chat history
    for turn in session.chat_history:
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"**Bot:** {turn['bot']}")

# ——— LEAD CAPTURE ———
if session.show_lead_form:
    st.info(config["lead"]["prompt"])
    with st.form("lead_form"):
        lead = {}
        for field in config["lead"]["fields"]:
            fld = config["lead"]["fields"][field]
            if fld["type"] == "text":
                lead[field] = st.text_input(fld["label"])
            elif fld["type"] == "select":
                lead[field] = st.selectbox(
                    fld["label"],
                    options=fld["options"],
                    index=fld.get("default_index", 0)
                )
        if st.form_submit_button("Submit"):
            save_lead(lead)
            st.success("Thanks! We’ll be in touch soon.")

# ——— MESSAGE REVIEW TOOL ———
with st.expander("📋 Situation → Bot Preview"):
    page = st.selectbox("Simulate Page", config["pages"])
    question = st.text_input("Sample visitor question")
    if question:
        preview_ctx = build_prompt([], question, faq_data=faq_data, page_context=page)
        preview_ans = generate_response(preview_ctx)
        st.markdown(f"**Bot would say:** {preview_ans}")

# ——— RESET ———
if st.button("🔄 Clear all"):
    for key in ["chat_history", "questions_asked", "show_lead_form",
                "start_time", "intent_shown", "chat_enabled"]:
        session[key] = [] if isinstance(session[key], list) else False
    session.start_time = time.time()
