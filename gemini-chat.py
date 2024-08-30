import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env 파일의 환경 변수를 로드
load_dotenv()

# .env 파일에서 변수 가져오기
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

@st.cache_resource
def load_model():
    model = genai.GenerativeModel('gemini-pro')
    print("model loaded...")
    return model

model = load_model()
st.title("echo-bot")

if "chat_session" not in st.session_state:
    st.session_state["chat_session"] = model.start_chat(history=[])

for content in st.session_state.chat_session.history:
    with st.chat_message("ai" if content.role == "model" else "user"):
        st.markdown(content.parts[0].text)

if prompt := st.chat_input("메시지를 입력하세요."):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("ai"):
        #response = st.session_state.chat_session.send_message(prompt)
        #st.markdown(response.text)
        message_placeholder = st.empty() # DeltaGenerator 반환
        full_response = ""
        with st.spinner("메시지 처리 중입니다."):
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response)
        print(st.session_state.chat_session.history)
