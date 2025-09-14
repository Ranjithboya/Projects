import os
import json
import streamlit as st
import time
from datetime import datetime
import openai

from openai import OpenAI

client = OpenAI(api_key="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")

import os
import json
import time
import streamlit as st
from datetime import datetime
from openai import OpenAI

# === CONFIG ===
CONFIG_DIR = "config"
os.makedirs(CONFIG_DIR, exist_ok=True)

def load_json(path, default=[]):
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load configs
faqs = load_json(f"{CONFIG_DIR}/faqs.json")
bot_config = load_json(f"{CONFIG_DIR}/bot_config.json", default={"tone": "", "persona": ""})
nudges = load_json(f"{CONFIG_DIR}/nudges.json")
lead_fields = load_json(f"{CONFIG_DIR}/lead_fields.json")



# === SESSION STATE ===
st.session_state.setdefault("chat_log", [])
st.session_state.setdefault("lead_info", {})
st.session_state.setdefault("trace", [])
st.session_state.setdefault("knowledge_pack", "")

def save_trace_to_file(trace_data, filename="session_trace.json"):
    with open(filename, "w") as f:
        json.dump(trace_data, f, indent=2)

def save_lead_to_file(lead_data, filename="leads.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read().strip()
            existing = json.loads(content) if content else []
    else:
        existing = []
    existing.append(lead_data)
    with open(filename, "w") as f:
        json.dump(existing, f, indent=2)

# === HIDE STREAMLIT UI ELEMENTS ===
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712107.png", width=60)
st.sidebar.markdown("### 🤖 Sales Assistant Bot")

# === KNOWLEDGE PACK UPLOAD IN SIDEBAR ===
st.sidebar.markdown("#### 📦 Upload Knowledge Pack")
uploaded_pack = st.sidebar.file_uploader("Upload a .txt or .md file", type=["txt", "md"], key="sidebar_knowledge_pack")
if uploaded_pack:
    st.session_state.knowledge_pack = uploaded_pack.getvalue().decode("utf-8")
    st.sidebar.success("Knowledge pack uploaded successfully!")

# === HEADER ===
st.title("💬 Sales Page Quick-Answer & Lead Bot")

# === SITUATION PREVIEW ===
st.subheader("🧪 Situation → Bot Would Say...")
situation = st.text_input("Describe a visitor’s situation")
if st.button("Preview Response"):
    context = "\n".join([f"{faq['question']}: {faq['answer']}" for faq in faqs])
    full_context = context + "\n\n" + st.session_state.knowledge_pack
    preview_prompt = f"{full_context}\n\nSituation: {situation}\nBot:"
    preview_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": bot_config["persona"]},
            {"role": "user", "content": preview_prompt}
        ]
    )
    preview_text = preview_response.choices[0].message.content.strip()
    st.markdown(f"**Bot would say:**\n\n{preview_text}")

# === CHAT HISTORY ===
st.subheader("Live Q&A Chat")
for q, a, ts in st.session_state.chat_log:
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        st.markdown(a)

# === NEW QUESTION ===
question = st.chat_input("Ask me anything...")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    context = "\n".join([f"{faq['question']}: {faq['answer']}" for faq in faqs])
    full_context = context + "\n\n" + st.session_state.knowledge_pack
    prompt = f"{full_context}\n\nUser: {question}\nBot:"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": bot_config["persona"]},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response.choices[0].message.content.strip()

    with st.chat_message("assistant"):
        with st.spinner("Bot is typing..."):
            time.sleep(1.5)
            st.markdown(answer)

    timestamp = datetime.now().isoformat()
    st.session_state.chat_log.append((question, answer, timestamp))
    st.session_state.trace.append({"time": timestamp, "type": "Q&A", "text": question})
    st.session_state.trace.append({"time": timestamp, "type": "A", "text": answer})
    save_trace_to_file(st.session_state.trace)

    # Optional: nudge after 2 questions
    for nudge in nudges:
        if nudge["trigger"] == "2_questions" and len(st.session_state.chat_log) == 2:
            with st.chat_message("assistant"):
                st.markdown(f"💡 {nudge['message']}")

# === LEAD CAPTURE ===
if len(st.session_state.chat_log) >= 2 and not st.session_state.lead_info:
    st.subheader("📇 Interested? Get a quick quote")
    with st.form("lead_form"):
        lead_data = {}
        for field in lead_fields:
            value = st.text_input(field["label"])
            lead_data[field["key"]] = value
        submitted = st.form_submit_button("Submit")
        if submitted:
            lead_data["timestamp"] = datetime.now().isoformat()
            st.session_state.lead_info = lead_data
            st.session_state.trace.append({"time": lead_data["timestamp"], "type": "Lead", "text": json.dumps(lead_data)})
            save_trace_to_file(st.session_state.trace)
            save_lead_to_file(lead_data)
            st.success("Thanks! We'll be in touch soon.")