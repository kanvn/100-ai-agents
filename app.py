import streamlit as st
import asyncio
import os
import plotly.express as px
# Import code xử lý từ file core_logic
from core_logic import GrandCouncilPipeline, CONFIG 

# Cấu hình trang web
st.set_page_config(page_title="AI Hive Mind Pro", page_icon="🧠", layout="wide")

st.title("🧠 ĐẠI HỘI ĐỒNG 100 AI")
st.caption("Hệ thống trí tuệ bầy đàn thực chiến")

# --- THANH CẤU HÌNH BÊN TRÁI ---
with st.sidebar:
    st.header("⚙️ Cấu hình lõi")
    
    # Nút chuyển chế độ
    mode = st.radio("Chế độ hoạt động:", ["Giả lập (Miễn phí)", "Thực chiến (API)"])
    if mode == "Thực chiến (API)":
        CONFIG["SIMULATION_MODE"] = False
        api_key = st.text_input("Nhập OpenAI API Key:", type="password")
        if api_key: os.environ["OPENAI_API_KEY"] = api_key
    else:
        CONFIG["SIMULATION_MODE"] = True
        
    CONFIG["TOTAL_AGENTS"] = st.slider("Số lượng Chuyên gia", 5, 50, 20)

# --- GIAO DIỆN CHÍNH ---
question = st.text_area("Nhập vấn đề khó khăn của bạn:", height=100)

if st.button("🚀 KÍCH HOẠT HỆ THỐNG", type="primary"):
    if not question:
        st.warning("Vui lòng nhập câu hỏi!")
    else:
        pipeline = GrandCouncilPipeline()
        
        # Tạo các khu vực hiển thị
        status = st.empty()
        bar = st.progress(0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.expander("GĐ 1: Thu thập ý kiến", expanded=True): log1 = st.empty()
        with col2:
            with st.expander("GĐ 2: Phân tích & Gom nhóm", expanded=True): log2 = st.empty()
        with col3:
            with st.expander("GĐ 3: Tổng hợp", expanded=True): log3 = st.empty()

        # --- CHẠY LOGIC (KHẮC PHỤC LỖI TẠI DÒNG NÀY) ---
        # Truyền đủ 4 tham số: question, status, bar, logs
        try:
            result_text, df_chart = asyncio.run(pipeline.run(question, status, bar, [log1, log2, log3]))
            
            # Hiển thị kết quả
            st.success("✅ ĐÃ CÓ PHƯƠNG ÁN XỬ LÝ!")
            st.markdown("### 📝 KẾT QUẢ QUYẾT NGHỊ:")
            st.write(result_text)
            
            # Vẽ biểu đồ tư duy (Nếu có dữ liệu)
            if df_chart is not None and not df_chart.empty:
                st.markdown("---")
                st.markdown("### 📊 BẢN ĐỒ TƯ DUY CỦA CÁC AGENT")
                fig = px.scatter(
                    df_chart, x="x", y="y", 
                    color="Cluster", hover_data=["Role", "Content"],
                    title="Sự phân bố các luồng ý kiến"
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {str(e)}")
            st.info("Mẹo: Nếu dùng chế độ Thực chiến, hãy kiểm tra lại API Key.")
