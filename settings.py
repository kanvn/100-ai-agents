# settings.py
import os

# Cấu hình hệ thống
CONFIG = {
    "SIMULATION_MODE": False,     # False = Chạy thật, True = Chạy giả lập
    "TOTAL_AGENTS": 50,           # Số lượng Noron mặc định
    "FILTER_KEEP": 5,             # Số lượng ý tưởng cốt lõi giữ lại
    "REAL_MODEL": "gpt-4o-mini",  # Model AI sử dụng
    "TIMEOUT": 60
}

# Danh sách "Nhân cách" (Các chuyên gia trong nhà máy)
FACTORY_ROLES = [
    "Giám đốc Tài chính (CFO)", 
    "Giám đốc Sản xuất (Factory Manager)", 
    "Trưởng phòng Quản lý Chất lượng (QC Manager)", 
    "Giám đốc Kinh doanh (Sales Director)", 
    "Kỹ sư Quy trình (Process Engineer)",
    "Chuyên gia Chuỗi cung ứng",
    "Luật sư Thương mại",
    "Chuyên gia Phân tích Rủi ro"
]
