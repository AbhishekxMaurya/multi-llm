import streamlit as st
import httpx

st.set_page_config(page_title="Groq Gateway Client", page_icon="⚡")
st.title("⚡ Groq Gateway Client")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Capture user input
if prompt := st.chat_input("Ask something..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare standard payload for your local FastAPI Gateway
    payload = {
        "model": "auto",
        "messages": st.session_state.messages,
        "temperature": 0.7
    }

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post("http://gateway:8000/v1/chat/completions", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"]
                    response_placeholder.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # Display performance metrics from headers
                    latency = response.headers.get("X-Gateway-Latency-Ms", "Unknown")
                    st.caption(f"Gateway Latency: {latency}ms")
                else:
                    response_placeholder.error(f"Gateway Error: {response.status_code}")
        except Exception as e:
            response_placeholder.error(f"Failed to connect to gateway: {str(e)}")