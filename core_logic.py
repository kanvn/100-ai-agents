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
    # Nếu False: Chạy thật (Tốn tiền API). Nếu True: Chạy giả lập (Miễn phí)
    "SIMULATION_MODE": False, 
    "TOTAL_AGENTS": 20,           # Chạy thật nên giảm xuống 20-30 con cho đỡ tốn tiền
    "FILTER_KEEP": 5,
    "REAL_MODEL": "gpt-4o-mini",  # Hoặc "gemini/gemini-1.5-flash" (Rẻ & Nhanh)
    "TIMEOUT": 60
}

# --- CÁC VAI TRÒ CHUYÊN GIA ---
ROLES_DB = [
    "Kỹ sư An ninh mạng (Cyber Security)", "Giám đốc Tài chính (CFO)", 
    "Nhà Xã hội học", "Luật sư Quốc tế", "Hacker Mũ trắng", 
    "Chuyên gia Tâm lý hành vi", "Nhà đầu tư mạo hiểm", "Bác sĩ",
    "Nhà hoạt động môi trường", "Chuyên gia Marketing"
]

class AIAgent:
    def __init__(self, agent_id):
        self.id = f"Agent_{agent_id:03d}"
        self.role = random.choice(ROLES_DB)
        
    async def process(self, user_question, semaphore):
        async with semaphore:
            try:
                # --- LOGIC GIẢ LẬP (ĐỂ TEST) ---
                if CONFIG["SIMULATION_MODE"]:
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    content = f"[{self.role}] Theo tôi, vấn đề '{user_question[:10]}...' cần giải quyết bằng quy trình chuẩn hóa số {random.randint(100,999)}."
                    # Vector giả 1536 chiều (giống OpenAI)
                    vector = np.random.rand(1536).tolist()
                    return {"id": self.id, "role": self.role, "content": content, "vector": vector, "status": "SUCCESS"}

                # --- LOGIC CHẠY THẬT (GỌI API) ---
                else:
                    # 1. Sinh câu trả lời
                    prompt = f"""
                    Bạn là một {self.role} xuất sắc hàng đầu thế giới.
                    Hãy phân tích vấn đề sau dưới góc nhìn chuyên môn của bạn: "{user_question}"
                    Yêu cầu: Ngắn gọn (dưới 100 từ), súc tích, đi thẳng vào trọng tâm chuyên ngành.
                    """
                    
                    response = await acompletion(
                        model=CONFIG["REAL_MODEL"],
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    content_text = response.choices[0].message.content

                    # 2. Tạo Vector (Embedding) để phân loại
                    # Dùng model text-embedding-3-small (Rất rẻ)
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
        self.agents = []

    async def run(self, user_question, st_status, st_progress, st_logs):
        # 1. KÍCH HOẠT ĐÁM ĐÔNG
        concurrency = 10 # Số luồng chạy song song
        sem = asyncio.Semaphore(concurrency)
        agents = [AIAgent(i) for i in range(CONFIG["TOTAL_AGENTS"])]
        
        tasks = [agent.process(user_question, sem) for agent in agents]
        
        results = []
        completed = 0
        
        # Chạy và update tiến độ
        for f in asyncio.as_completed(tasks):
            res = await f
            results.append(res)
            completed += 1
            progress = int((completed / CONFIG["TOTAL_AGENTS"]) * 60)
            if st_progress: st_progress.progress(progress)
            
            # Hiện log thời gian thực cho 3 con đầu tiên
            if st_logs and completed <= 3:
                st_logs[0].markdown(f"**{res.get('role', 'System')}**: {res.get('content', 'Error')[:100]}...")

        valid_data = [r for r in results if r["status"] == "SUCCESS"]
        if not valid_data: return "❌ Lỗi: Không có phản hồi từ AI (Kiểm tra API Key)", None

        # 2. PHÂN CỤM Ý TƯỞNG (CLUSTERING)
        if st_logs: st_logs[1].info("Đang dùng thuật toán K-Means phân tích Vector...")
        
        vectors = np.array([item['vector'] for item in valid_data])
        n_clusters = min(CONFIG["FILTER_KEEP"], len(valid_data))
        
        kmeans = KMeans(n_clusters=n_clusters, n_init=10)
        kmeans.fit(vectors)
        
        # Gom nhóm và chọn đại diện
        representatives = []
        df_for_chart = [] # Dữ liệu để vẽ biểu đồ
        
        seen_clusters = set()
        for i, label in enumerate(kmeans.labels_):
            item = valid_data[i]
            # Lưu dữ liệu để vẽ
            df_for_chart.append({
                "Role": item['role'],
                "Cluster": str(label),
                "Content": item['content'][:50] + "...",
                "x": vectors[i][0], # Lấy chiều thứ 1 làm tọa độ giả
                "y": vectors[i][1]  # Lấy chiều thứ 2 làm tọa độ giả
            })
            
            if label not in seen_clusters:
                representatives.append(item)
                seen_clusters.add(label)
                if st_logs: st_logs[1].markdown(f"- **Nhóm quan điểm {label+1}**: Đại diện bởi *{item['role']}*")

        # 3. TỔNG HỢP CUỐI CÙNG (FINAL JUDGE)
        if st_logs: st_logs[2].info("Đang tổng hợp câu trả lời tối ưu...")
        final_ans = await self.final_synthesis(representatives, user_question)
        
        if st_progress: st_progress.progress(100)
        return final_ans, pd.DataFrame(df_for_chart)

    async def final_synthesis(self, reps, q):
        # Tổng hợp ý kiến
        context = "\n".join([f"- {r['role']}: {r['content']}" for r in reps])
        
        if CONFIG["SIMULATION_MODE"]:
            return f"**TỔNG HỢP GIẢ LẬP:**\n{context}"
        else:
            prompt = f"""
            Bạn là Chủ tịch Hội đồng Tối cao. Dưới đây là ý kiến của các nhóm chuyên gia về vấn đề: "{q}"
            
            {context}
            
            NHIỆM VỤ:
            Tổng hợp thành một câu trả lời hoàn chỉnh, giải quyết mâu thuẫn và đưa ra lời khuyên hành động cụ thể.
            """
            try:
                response = await acompletion(
                    model=CONFIG["REAL_MODEL"],
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            except:
                return "Lỗi tổng hợp."
