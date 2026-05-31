"""
ui/app.py — Streamlit Frontend
Run with: streamlit run ui/app.py
"""

import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Job Application AI Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Job Application AI Agent")
st.caption("Built for Rushikesh Mohalkar — AI/ML Engineer, Bangalore")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Quick Actions")
    action = st.radio("What do you want to do?", [
        "💬 Chat with Agent",
        "📊 Analyse a JD",
        "✍️ Generate Cover Letter",
        "📝 Generate Resume Bullets",
    ])
    st.divider()
    st.markdown("**Tech Stack**")
    st.markdown("LangChain · RAG · FAISS\nFastAPI · Docker · Streamlit")

# ── Chat Mode ─────────────────────────────────────────────────────────────────
if action == "💬 Chat with Agent":
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Paste a JD, ask a question, or say 'am I a fit for this role?'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent thinking..."):
                try:
                    res = requests.post(f"{API_URL}/chat", json={"message": prompt}, timeout=60)
                    reply = res.json()["response"]
                except Exception as e:
                    reply = f"Error: {e}"
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# ── Analyse JD Mode ───────────────────────────────────────────────────────────
elif action == "📊 Analyse a JD":
    st.subheader("Fit Score & Gap Analysis")
    company = st.text_input("Company name", placeholder="e.g. Sarvam AI")
    jd = st.text_area("Paste Job Description", height=300)

    if st.button("Analyse My Fit", type="primary"):
        if not jd:
            st.warning("Please paste a job description.")
        else:
            with st.spinner("Analysing..."):
                try:
                    res = requests.post(
                        f"{API_URL}/analyse",
                        json={"job_description": jd, "company_name": company},
                        timeout=60
                    )
                    st.markdown(res.json()["response"])
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Generate Document Mode ────────────────────────────────────────────────────
elif action in ("✍️ Generate Cover Letter", "📝 Generate Resume Bullets"):
    doc_type = "cover_letter" if "Cover" in action else "resume_bullets"
    st.subheader(f"Generate {doc_type.replace('_', ' ').title()}")
    company = st.text_input("Company name", placeholder="e.g. Observe.AI")
    jd = st.text_area("Paste Job Description", height=300)

    if st.button("Generate", type="primary"):
        if not jd:
            st.warning("Please paste a job description.")
        else:
            with st.spinner("Writing..."):
                try:
                    res = requests.post(
                        f"{API_URL}/generate",
                        json={"job_description": jd, "company_name": company, "doc_type": doc_type},
                        timeout=60
                    )
                    output = res.json()["response"]
                    st.markdown(output)
                    st.download_button(
                        "Download as .txt",
                        data=output,
                        file_name=f"{doc_type}_{company or 'output'}.txt"
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
