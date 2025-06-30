# Gen-z: Advanced AI Chatbot with GPT-3.5/4, Voice & UI Enhancements
# Requirements: openai, streamlit, pyttsx3, speech_recognition, python-dotenv

import streamlit as st
import openai
import datetime
import os
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Gen-z AI Chatbot", layout="centered")
st.markdown("""
<style>
.chat-box {
    background-color: #f0f2f6;
    border-radius: 12px;
    padding: 10px;
    margin: 10px 0;
}
.user {
    color: #0057e7;
    font-weight: bold;
}
.bot {
    color: #008744;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Gen-z: Smart AI Chatbot")

engine = pyttsx3.init()

# Chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Voice input function
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now!")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError:
        return "Error with speech recognition service."

# Voice output function
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# GPT-3.5 or GPT-4 response generator
def get_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # change to gpt-4 if needed
        messages=[
            {"role": "system", "content": "You are Gen-z, a friendly and smart assistant."},
            *[{"role": "user" if i % 2 == 0 else "assistant", "content": m[1]} for i, m in enumerate(st.session_state.chat_history)],
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# Input box or voice input
use_voice = st.checkbox("🎤 Use Voice Input")

if use_voice:
    if st.button("Start Recording"):
        user_input = recognize_speech()
        st.text_input("You:", user_input, key="input")
else:
    user_input = st.text_input("You:", "", key="input")

if st.button("Send"):
    if user_input:
        st.session_state.chat_history.append(("You", user_input))
        reply = get_openai_response(user_input)
        st.session_state.chat_history.append(("Gen-z", reply))
        speak_text(reply)

# Display chat history
st.write("---")
st.subheader("💬 Chat History")
for speaker, text in st.session_state.chat_history:
    speaker_class = "user" if speaker == "You" else "bot"
    st.markdown(f"<div class='chat-box'><span class='{speaker_class}'>{speaker}:</span> {text}</div>", unsafe_allow_html=True)

# Save chat
if st.button("💾 Save Chat History"):
    folder = "genz_chats"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"chat_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        for speaker, text in st.session_state.chat_history:
            f.write(f"{speaker}: {text}\n")
    st.success(f"Chat history saved to {filename}")

# Load previous chat
if st.button("📂 Load Last Chat"):
    folder = "genz_chats"
    try:
        files = sorted(os.listdir(folder), reverse=True)
        if files:
            with open(os.path.join(folder, files[0]), encoding="utf-8") as f:
                lines = f.readlines()
                st.session_state.chat_history = [tuple(line.strip().split(": ", 1)) for line in lines if ": " in line]
            st.success("Last chat loaded!")
        else:
            st.warning("No previous chat found.")
    except FileNotFoundError:
        st.warning("Chat folder not found.")
