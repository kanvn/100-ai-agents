# app.py
import streamlit as st
import asyncio
import os
import plotly.express as px
from cortex import CortexProcessor 
from settings import CONFIG

st.set_page_config(page_title="AI Neural Hive", page_icon="🧠", layout="wide")
st.title("🧠 HỆ THỐNG MẠNG LƯỚI 100 AI (NEURAL HIVE)")

# --- SIDEBAR (Cấu hình) ---
with st.sidebar:
    st.header("⚙️ Cấu hình Neural")
    mode = st.radio("Chế độ:", ["Giả lập (Simulation)", "Thực chiến (Live Brain)"])
    
    if mode == "Thực chiến (Live Brain)":
        CONFIG["SIMULATION_MODE"] = False
        api_key = st.text_input("OpenAI Key:", type="password")
        if api_key: os.environ["OPENAI_API_KEY"] = api_key
    else:
        CONFIG["SIMULATION_MODE"] = True
        
    CONFIG["TOTAL_AGENTS"] = st.slider("Số lượng Noron kích hoạt", 10, 100, 50)

# --- MAIN UI ---
user_input = st.text_area("Nhập tín hiệu đầu vào (Vấn đề):", height=100)

if st.button("⚡ KÍCH HOẠT HỆ THẦN KINH", type="primary"):
    if not user_input:
        st.warning("Chưa có tín hiệu đầu vào!")
    else:
        # Khởi tạo bộ não
        brain = CortexProcessor()
        
        status = st.empty()
        bar = st.progress(0)
        c1, c2, c3 = st.columns(3)
        with c1: 
            with st.expander("GĐ 1: Kích hoạt Noron", expanded=True): log1 = st.empty()
        with c2: 
            with st.expander("GĐ 2: Phân vùng não bộ", expanded=True): log2 = st.empty()
        with c3: 
            with st.expander("GĐ 3: Quyết định", expanded=True): log3 = st.empty()

        # Chạy
        try:
            result, df = asyncio.run(brain.process_signal(user_input, status, bar, [log1, log2, log3]))
            
            st.success("✅ ĐÃ CÓ PHẢN XẠ THẦN KINH!")
            st.markdown(result)
            
            if df is not None and not df.empty:
                st.markdown("---")
                st.markdown("### 🌌 BẢN ĐỒ HOẠT ĐỘNG NÃO BỘ")
                fig = px.scatter(df, x="x", y="y", color="Cluster", hover_data=["Role", "Content"], title="Sự phân bố các luồng suy nghĩ")
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Lỗi hệ thần kinh: {e}")
