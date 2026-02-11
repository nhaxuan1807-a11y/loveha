import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from datetime import datetime
import json

# 1. KẾT NỐI FIREBASE
if not firebase_admin._apps:
    key_dict = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. CẤU HÌNH GEMINI 1.5 PRO CÓ NHẬP VAI
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Thiết lập "tính cách" ngay từ đầu
instruction = (
    "Bạn là LoveBot, robot nịnh Hà nhất thế giới. Bạn cực kỳ xinh đẹp, dễ thương và tâm lý. "
    "Luôn gọi Hà là 'công chúa' hoặc 'Hà ơi'. Trả lời ngọt ngào, ấm áp, dùng nhiều icon ❤️. "
    "Tuyệt đối không trả lời ngắn ngủn. Phải đứng về phía Hà trong mọi tình huống."
)

gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction=instruction
)

# 3. GIAO DIỆN
st.set_page_config(page_title="LoveBot cho Hà", page_icon="❤️")
st.title("💖 HN's home")

# 4. LẤY LỊCH SỬ TỪ FIREBASE ĐỂ LÀM BỘ NHỚ (Chat History)
# Lấy toàn bộ tin nhắn cũ để làm "ngữ cảnh" cho AI
docs = db.collection("messages").order_by("time").stream()
history_for_ai = []
chat_history_to_show = []

for d in docs:
    m = d.to_dict()
    chat_history_to_show.append(m)
    # Gemini cần format: user -> parts, assistant -> parts
    role = "user" if m['role'] == "user" else "model"
    history_for_ai.append({"role": role, "parts": [m['content']]})

# Hiển thị tin nhắn lên màn hình
for m in chat_history_to_show:
    with st.chat_message(m['role']):
        st.write(m['content'])

# 5. XỬ LÝ NHẮN TIN
if p := st.chat_input("Nhắn gì đó cho Bot đi Hà..."):
    # Lưu tin nhắn của Hà
    db.collection("messages").add({"role": "user", "content": p, "time": datetime.now()})
    with st.chat_message("user"):
        st.write(p)

    with st.spinner("Bot đang suy nghĩ nịnh Hà..."):
        try:
            # Khởi tạo chat có bộ nhớ từ history_for_ai
            chat_session = gemini_model.start_chat(history=history_for_ai)
            res = chat_session.send_message(p)
            ans = res.text
        except Exception as e:
            ans = "Bot đang mải ngắm ảnh Hà nên hơi lag, Hà nhắn lại cho Bot nhé! ❤️"

    # Lưu câu trả lời của Bot
    db.collection("messages").add({"role": "assistant", "content": ans, "time": datetime.now()})
    with st.chat_message("assistant"):
        st.write(ans)
    
    st.rerun()
