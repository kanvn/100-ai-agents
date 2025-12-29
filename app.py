import streamlit as st
import asyncio
from cortex_main import CortexMain

st.set_page_config(layout="wide", page_title="AI BIO-BRAIN", page_icon="🧠")

st.markdown("<h1 style='text-align: center;'>🧠 SIÊU BỘ NÃO: 7 GIÁC QUAN & 4 BÁN CẦU</h1>", unsafe_allow_html=True)
st.caption("Quy trình sinh học: Giác quan -> Amygdala (Sợ hãi) -> PFC (Lý trí) -> Motor (Hành động) -> Broca (Lời nói)")

# Khu vực nhập liệu
user_input = st.text_area("Nhập tín hiệu đầu vào (VD: Máy ép số 1 kêu to, rung lắc, có mùi khét...):", height=80)

if st.button("🚀 KÍCH HOẠT HỆ THẦN KINH", type="primary"):
    if not user_input:
        st.warning("Vui lòng nhập dữ liệu đầu vào!")
    else:
        brain = CortexMain()
        
        # Chia giao diện thành 4 cột cho 4 não
        col1, col2, col3, col4 = st.columns(4)
        ui_map = {
            "STRATEGY": col1,
            "OPERATION": col2,
            "RISK": col3,
            "MARKET": col4
        }
        
        # Tiêu đề cột
        col1.subheader("💰 Chiến Lược")
        col2.subheader("⚙️ Vận Hành")
        col3.subheader("🛡️ Rủi Ro")
        col4.subheader("📢 Thị Trường")

        # Chạy xử lý bất đồng bộ
        asyncio.run(brain.process_hive_mind(user_input, ui_map))
        st.success("✅ ĐÃ HOÀN TẤT QUY TRÌNH XỬ LÝ SINH HỌC")
