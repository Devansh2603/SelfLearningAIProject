import streamlit as st
import requests

# Set page config
st.set_page_config(page_title="Ask Me", page_icon="🤖", layout="centered")

# Title
st.title("Ask Me")

# User input
user_query = st.text_input("Enter your question:", placeholder="e.g., What services were done yesterday?")

# Button
if st.button("Let's Go"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            try:
                # Replace with your FastAPI endpoint
                response = requests.post("http://localhost:8000/query", json={"query": user_query})
                if response.status_code == 200:
                    result = response.json()
                    st.success("Response:")
                    st.write(result.get("response", "No response found."))
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")

