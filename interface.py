import streamlit as st
from project.app import OllamaChatbot

# Initialize chatbot object in session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = OllamaChatbot()

# Streamlit UI
st.set_page_config(page_title="Ask Anything", layout="centered")
st.title("🤖 Ask Anything")

with st.form("chat_form"):
    user_input = st.text_input("Your question:", "")
    submit = st.form_submit_button("Go")

if submit and user_input.strip():
    response = st.session_state.chatbot.ask(user_input)
    st.markdown(f"**🧠 Response:** {response}")

# Conversation history
with st.expander("💬 Conversation History"):
    for msg in st.session_state.chatbot.get_history():
        role = "🧍 You" if msg["role"] == "user" else "🤖 Bot"
        st.markdown(f"**{role}:** {msg['content']}")
