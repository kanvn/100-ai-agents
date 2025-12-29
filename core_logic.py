import asyncio
import random
import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from litellm import acompletion, embedding
import plotly.express as px

# --- CẤU HÌNH ---
CONFIG = {
    "SIMULATION_MODE": False,     # Mặc định tắt giả lập để nhắc bạn nhập Key
    "TOTAL_AGENTS": 10,           # 10 chuyên gia là đủ để ra quyết định sâu sắc
    "FILTER_KEEP": 3,             # Giữ lại 3 luồng ý kiến chính
    "REAL_MODEL": "gpt-4o-mini",  # Model thông minh và rẻ
    "TIMEOUT": 60
}

# --- DANH SÁCH VAI DIỄN CHUYÊN BIỆT CHO NHÀ MÁY ---
# Đã xóa Bác sĩ/Hacker, thay bằng đội ngũ quản trị doanh nghiệp
ROLES_DB = [
    "Giám đốc Tài chính (CFO)", 
    "Giám đốc Sản xuất (Factory Manager)", 
    "Trưởng phòng Quản lý Chất lượng (QC Manager)", 
    "Giám đốc Kinh doanh (Sales Director)", 
    "Kế toán trưởng", 
    "Kỹ sư Quy trình (Process Engineer)",
    "Chuyên gia Chuỗi cung ứng",
    "Luật sư Thương mại"
]

class AIAgent:
    def __init__(self, agent_id):
        self.id = f"Agent_{agent_id:03d}"
        self.role = random.choice(ROLES_DB)
        
    async def process(self, user_question, semaphore):
        async with semaphore:
            try:
                # --- CHẾ ĐỘ GIẢ LẬP (Mẫu trả lời về Bavia) ---
                if CONFIG["SIMULATION_MODE"]:
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    if "CFO" in self.role or "Tài chính" in self.role:
                        content = f"[{self.role}] Về mặt tài chính, lô hàng Bavia này nên HỦY. Chi phí sửa chữa (Rework) tốn 15% margin, rủi ro khách trả hàng cao gấp đôi."
                    elif "Sản xuất" in self.role:
                        content = f"[{self.role}] Tôi đề xuất sửa lại khuôn ngay lập tức. Cho công nhân tăng ca xử lý lô này để kịp tiến độ."
                    else:
                        content = f"[{self.role}] Cần xem lại hợp đồng với khách hàng về tiêu chuẩn chấp nhận lỗi ngoại quan."
                    
                    vector = np.random.rand(1536).tolist()
                    return {"id": self.id, "role": self.role, "content": content, "vector": vector, "status": "SUCCESS"}

                # --- CHẾ ĐỘ THỰC CHIẾN (GỌI API) ---
                else:
                    # Prompt chuyên sâu cho vai diễn
                    prompt = f"""
                    Bạn đang đóng vai: {self.role} tại một nhà máy sản xuất lớn.
                    Vấn đề đang được thảo luận: "{user_question}"
                    
                    NHIỆM VỤ:
                    1. Phân tích vấn đề dựa trên LỢI ÍCH CỐT LÕI của vị trí bạn nắm giữ (Ví dụ: CFO chỉ quan tâm dòng tiền/lợi nhuận, QC quan tâm uy tín).
                    2. Đưa ra con số giả định hoặc quy trình cụ thể.
                    3. Quyết định dứt khoát: Sửa (Rework) hay Hủy (Scrap)?
                    """
                    
                    response = await acompletion(
                        model=CONFIG["REAL_MODEL"],
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    content_text = response.choices[0].message.content

                    emb_res = await embedding(
                        model="text-embedding-3-small",
                        input=[content_text]
                    )
                    vector_data = emb_res.data[0]['embedding']

                    return {"id": self.id, "role": self.role, "content": content_text, "vector": vector_data, "status": "SUCCESS"}

            except Exception as e:
                return {"id": self.id, "status": "ERROR", "error": str(e)}

class GrandCouncilPipeline:
    def __init__(self):
        pass

    async def run(self, user_question, st_status, st_progress, st_logs):
        concurrency = 5 
        sem = asyncio.Semaphore(concurrency)
        
        # Tạo Agent
        agents = [AIAgent(i) for i in range(CONFIG["TOTAL_AGENTS"])]
        tasks = [agent.process(user_question, sem) for agent in agents]
        
        results = []
        completed = 0
        
        for f in asyncio.as_completed(tasks):
            res = await f
            results.append(res)
            completed += 1
            if st_progress: st_progress.progress(int((completed / CONFIG["TOTAL_AGENTS"]) * 70))
            if st_logs and completed <= 3:
                st_logs[0].write(f"👤 **{res.get('role')}**: {res.get('content')[:150]}...")

        valid_data = [r for r in results if r["status"] == "SUCCESS"]
        if not valid_data: return "Lỗi kết nối API. Hãy kiểm tra Key.", None

        # Phân cụm
        if st_logs: st_logs[1].info("Đang phân tích mâu thuẫn giữa các phòng ban...")
        vectors = np.array([item['vector'] for item in valid_data])
        
        kmeans = KMeans(n_clusters=min(CONFIG["FILTER_KEEP"], len(valid_data)), n_init=10)
        kmeans.fit(vectors)
        
        representatives = []
        df_for_chart = []
        
        seen = set()
        for i, label in enumerate(kmeans.labels_):
            item = valid_data[i]
            df_for_chart.append({
                "Role": item['role'], "Cluster": str(label), 
                "Content": item['content'][:100], 
                "x": vectors[i][0], "y": vectors[i][1]
            })
            
            if label not in seen:
                representatives.append(item)
                seen.add(label)
                if st_logs: st_logs[1].write(f"- Quan điểm {label+1}: {item['role']}")

        # Tổng hợp
        if st_logs: st_logs[2].info("CFO và Giám đốc nhà máy đang chốt phương án...")
        final_ans = await self.final_synthesis(representatives, user_question)
        
        if st_progress: st_progress.progress(100)
        return final_ans, pd.DataFrame(df_for_chart)

    async def final_synthesis(self, reps, q):
        context = "\n".join([f"- {r['role']} đề xuất: {r['content']}" for r in reps])
        
        if CONFIG["SIMULATION_MODE"]:
            return f"**TỔNG HỢP GIẢ LẬP:**\n{context}"
        else:
            prompt = f"""
            Bạn là Tổng Giám Đốc (CEO). Dưới đây là tranh luận giữa các trưởng phòng về vấn đề: "{q}"
            
            {context}
            
            YÊU CẦU:
            1. Tóm tắt xung đột chính (Ví dụ: Tài chính muốn hủy để cắt lỗ, nhưng Sản xuất muốn sửa để kịp giao hàng).
            2. Đưa ra QUYẾT ĐỊNH CUỐI CÙNG (Final Verdict) dựa trên tối ưu hóa lợi nhuận.
            3. Lập bảng so sánh ngắn gọn.
            """
            try:
                response = await acompletion(
                    model=CONFIG["REAL_MODEL"],
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            except:
                return "Lỗi tổng hợp."
