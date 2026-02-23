# app.py

import streamlit as st
import asyncio
from mcp_agent import run_agent

st.set_page_config(page_title="MCP Tool Agent", page_icon="🤖")

st.title("🤖 MCP Tool Agent 🤖")
# st.markdown("LangChain + MCP + Groq + Streamlit")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Ask something...")

if prompt:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(run_agent(prompt))
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})