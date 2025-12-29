# cortex.py
import asyncio
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from litellm import acompletion
from neuron import NeuronAgent # Gọi Noron
from settings import CONFIG      # Gọi Cấu hình

class CortexProcessor:
    def __init__(self):
        pass

    async def process_signal(self, user_input, st_status, st_progress, st_logs):
        # 1. KÍCH HOẠT MẠNG LƯỚI NORON
        concurrency = 10 
        sem = asyncio.Semaphore(concurrency)
        neurons = [NeuronAgent(i) for i in range(CONFIG["TOTAL_AGENTS"])]
        
        tasks = [n.activate(user_input, sem) for n in neurons]
        
        results = []
        completed = 0
        
        for f in asyncio.as_completed(tasks):
            res = await f
            results.append(res)
            completed += 1
            if st_progress: st_progress.progress(int((completed / CONFIG["TOTAL_AGENTS"]) * 70))
            if st_logs and completed <= 5: # Log vài tín hiệu mẫu
                st_logs[0].write(f"⚡ **{res.get('role')}**: {res.get('content')[:100]}...")

        valid_data = [r for r in results if r["status"] == "SUCCESS"]
        if not valid_data: return "Mất kết nối hệ thần kinh (Lỗi API).", None

        # 2. XỬ LÝ GOM NHÓM (CLUSTERING)
        if st_logs: st_logs[1].info("Đang phân loại các luồng tư tưởng...")
        vectors = np.array([item['vector'] for item in valid_data])
        
        kmeans = KMeans(n_clusters=min(CONFIG["FILTER_KEEP"], len(valid_data)), n_init=10)
        kmeans.fit(vectors)
        
        representatives = []
        df_chart = []
        seen = set()
        
        for i, label in enumerate(kmeans.labels_):
            item = valid_data[i]
            # Lưu dữ liệu vẽ biểu đồ não
            df_chart.append({
                "Role": item['role'], "Cluster": str(label), 
                "Content": item['content'][:50], 
                "x": vectors[i][0], "y": vectors[i][1]
            })
            if label not in seen:
                representatives.append(item)
                seen.add(label)
                if st_logs: st_logs[1].markdown(f"- **Luồng tư tưởng {label+1}**: {item['role']}")

        # 3. TỔNG HỢP (SYNTHESIS)
        if st_logs: st_logs[2].info("Vỏ não đang ra quyết định cuối cùng...")
        final_decision = await self.final_synthesis(representatives, user_input)
        
        if st_progress: st_progress.progress(100)
        return final_decision, pd.DataFrame(df_chart)

    async def final_synthesis(self, reps, inp):
        context = "\n".join([f"- {r['role']}: {r['content']}" for r in reps])
        
        if CONFIG["SIMULATION_MODE"]:
            return f"**KẾT QUẢ MÔ PHỎNG:**\n{context}"
        else:
            prompt = f"""
            Bạn là Bộ não trung tâm (CEO). Dưới đây là các xung đột từ các bộ phận về vấn đề: "{inp}"
            {context}
            YÊU CẦU: Tổng hợp xung đột, đưa ra quyết định tối ưu lợi nhuận và lập bảng kế hoạch hành động.
            """
            try:
                response = await acompletion(model=CONFIG["REAL_MODEL"], messages=[{"role": "user", "content": prompt}])
                return response.choices[0].message.content
            except: return "Lỗi xử lý trung tâm."
