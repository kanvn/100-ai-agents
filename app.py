import streamlit as st
import asyncio
import os
# Import class từ file core_logic.py (File code Python dài nhất ở câu trả lời trước)
# Lưu ý: Bạn phải lưu file code dài đó thành tên 'core_logic.py'
from core_logic import GrandCouncilPipeline, CONFIG 

# Cấu hình trang
st.set_page_config(page_title="AI Hive Mind Server", page_icon="🧠", layout="wide")

st.title("🧠 SERVER: ĐẠI HỘI ĐỒNG 100 AI")
st.markdown("---")

# Sidebar cấu hình
with st.sidebar:
    st.header("🎛️ Control Panel")
    CONFIG["TOTAL_AGENTS"] = st.slider("Số lượng Agents", 10, 100, 50)
    CONFIG["SIMULATION_MODE"] = st.toggle("Chế độ Giả lập", value=True)
    
    # Nhập Key nếu không có biến môi trường
    if not os.environ.get("OPENAI_API_KEY"):
        api_key = st.text_input("API Key", type="password")
        if api_key: os.environ["OPENAI_API_KEY"] = api_key

# Giao diện chính
col1, col2 = st.columns([2, 1])

with col1:
    question = st.text_area("Nhập vấn đề cần giải quyết:", height=150)
    start_btn = st.button("🚀 KÍCH HOẠT HỆ THỐNG", use_container_width=True)

with col2:
    st.info("Trạng thái Server: ✅ Online")
    st.write(f"RAM khả dụng: Tự động tối ưu")

# Khu vực Log
log_container = st.container()

if start_btn and question:
    with st.spinner("Đang khởi động 100 luồng xử lý..."):
        # Chuyển đổi hàm chạy console sang hiển thị web
        # (Bạn cần sửa nhẹ class GrandCouncilPipeline trong core_logic.py để trả về text thay vì print)
        # Hoặc dùng st.write đè lên print
        
        pipeline = GrandCouncilPipeline()
        
        # Để đơn giản hóa việc deploy, ta chạy pipeline và hiển thị kết quả cuối
        # Muốn hiển thị realtime trên web cần dùng st.empty() như hướng dẫn trước
        asyncio.run(pipeline.run(question)) 
        
        st.success("Đã hoàn thành tác vụ!")