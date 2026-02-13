import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import ollama
from datetime import datetime

# 1. KẾT NỐI FIREBASE (Đã có file key.json trong thư mục)
if not firebase_admin._apps:
    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. NÃO DỰ PHÒNG GEMINI (Dán key bro lấy từ aistudio.google.com vào đây)
genai.configure(api_key="AIzaSyD2mdx4C6MyV8homepQ0EovotLyN4dbwTk")
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# 3. GIAO DIỆN
st.set_page_config(page_title="LoveBot", page_icon="❤️")
st.title("💖 HN's home")

def get_response(prompt):
    instruction = "Bạn là LoveBot, robot nịnh Hà nhất thế giới. Nói tiếng Việt ngọt ngào ❤️."
    try:
        # Dùng não 1.5b bro đã tải xong
        res = ollama.chat(model='qwen2.5:1.5b', messages=[
            {'role': 'system', 'content': instruction},
            {'role': 'user', 'content': prompt}
        ])
        return res['message']['content']
    except:
        # Nếu máy lag, dùng Gemini gánh
        res = gemini_model.generate_content(f"{instruction}\nHà nhắn: {prompt}")
        return res.text

# 4. HIỂN THỊ CHAT
docs = db.collection("messages").order_by("time").stream()
for d in docs:
    m = d.to_dict()
    with st.chat_message(m['role']):
        st.write(m['content'])

# 5. NHẬN TIN NHẮN
if p := st.chat_input("Nhắn gì đó cho Bot đi Hà..."):
    db.collection("messages").add({"role": "user", "content": p, "time": datetime.now()})
    with st.spinner("Bot đang nghĩ..."):
        ans = get_response(p)
    db.collection("messages").add({"role": "assistant", "content": ans, "time": datetime.now()})
    st.rerun()
