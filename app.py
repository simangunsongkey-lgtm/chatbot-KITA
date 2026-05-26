import streamlit as st
import google.generativeai as genai

st.title("Chatbot AI Saya")

# Input API Key (bisa juga ditaruh di Streamlit Secrets)
api_key = st.text_input("AIzaSyAiJmfdLDFKANSQ-HhJpXmN_nLEtn-5rqY:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    # Tampilkan riwayat
    for message in st.session_state.chat.history:
        with st.chat_message("user" if message.role == "user" else "assistant"):
            st.markdown(message.parts[0].text)

    # Input User
    if prompt := st.chat_input("Apa yang ingin Anda tanyakan?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)