import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from datetime import datetime
import json

# 1. KẾT NỐI FIREBASE (Sử dụng Secrets để bảo mật)
if not firebase_admin._apps:
    # Lấy thông tin từ mục Secrets trên Streamlit Cloud
    key_dict = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. CẤU HÌNH SIÊU NÃO BỘ GEMINI 1.5 PRO
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# 3. GIAO DIỆN APP
st.set_page_config(page_title="LoveBot cho Hà", page_icon="❤️")
st.title("💖 HN's home")

# Hàm lấy phản hồi từ AI
# Cấu hình tính cách ngay khi khởi tạo model
gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction="Bạn là LoveBot, robot tình cảm cực kỳ xinh đẹp và dễ thương. Bạn là người nịnh Hà nhất thế giới. Khi trả lời Hà, hãy gọi Hà là 'công chúa' hoặc 'Hà ơi', nói năng ngọt ngào, ấm áp, sử dụng nhiều icon ❤️ và luôn đứng về phía Hà nhé!"
)

def get_response(prompt):
    try:
        # Giờ chỉ cần gửi prompt, model đã nhớ tính cách rồi
        res = gemini_model.generate_content(prompt)
        return res.text
    except Exception as e:
        return "Bot đang mải ngắm ảnh Hà nên hơi lag, Hà nhắn lại cho Bot nhé! ❤️"
# 4. HIỂN THỊ LỊCH SỬ CHAT (Lấy từ Firebase)
# Sắp xếp theo thời gian để tin nhắn cũ hiện lên trước
docs = db.collection("messages").order_by("time").stream()
for d in docs:
    m = d.to_dict()
    with st.chat_message(m['role']):
        st.write(m['content'])

# 5. Ô NHẬP TIN NHẮN
if p := st.chat_input("Nhắn gì đó cho Bot đi Hà..."):
    # Lưu tin nhắn của Hà vào Firebase
    db.collection("messages").add({
        "role": "user", 
        "content": p, 
        "time": datetime.now()
    })
    
    with st.chat_message("user"):
        st.write(p)

    # Bot suy nghĩ và trả lời
    with st.spinner("Bot đang nghĩ..."):
        ans = get_response(p)
    
    # Lưu câu trả lời của Bot vào Firebase
    db.collection("messages").add({
        "role": "assistant", 
        "content": ans, 
        "time": datetime.now()
    })

    with st.chat_message("assistant"):
        st.write(ans)

    # Làm mới trang để cập nhật tin nhắn mới nhất
    st.rerun()

