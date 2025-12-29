import asyncio
import json
import random
import time
import os
import psutil
import numpy as np
import uuid
from datetime import datetime
from sklearn.cluster import KMeans
import chromadb
from chromadb.utils import embedding_functions

# Import thư viện gọi AI đa năng
from litellm import acompletion, embedding

# ==============================================================================
# ⚙️ CẤU HÌNH HỆ THỐNG (SYSTEM CONFIG)
# ==============================================================================
CONFIG = {
    "SIMULATION_MODE": True,        # Mặc định True để test nhanh. Chuyển False trong app.py để chạy thật
    "TOTAL_AGENTS": 50,             # Số lượng mặc định
    "FILTER_KEEP": 5,               # Số đại diện giữ lại
    "SYSTEM_BUFFER_RAM_GB": 1.5,    # RAM chừa lại cho OS
    "DB_PATH": "./brain_memory",    # Đường dẫn lưu DB
    "REAL_MODEL": "gpt-3.5-turbo",  # Model chạy thật
    "TIMEOUT_SECONDS": 45           # Thời gian chờ tối đa cho 1 agent
}

# ==============================================================================
# 🛠️ MODULE 1: BÁC SĨ HỆ THỐNG (SYSTEM OPTIMIZER)
# ==============================================================================
class SystemOptimizer:
    @staticmethod
    def calculate_safe_concurrency(agent_count):
        """Tính toán số luồng an toàn dựa trên RAM thực tế của VPS"""
        try:
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)
            
            # Ước tính: 1 Thread Python + Network overhead ~ 60MB
            ram_per_thread_gb = 0.06 
            usable_ram = available_gb - CONFIG["SYSTEM_BUFFER_RAM_GB"]
            
            if usable_ram <= 0.2:
                return 2 # Chế độ sinh tồn (Low Memory)
                
            optimal_threads = int(usable_ram / ram_per_thread_gb)
            
            # Giới hạn trần: Không quá 50 luồng để tránh nghẽn CPU/IO
            # Và không lớn hơn tổng số agent yêu cầu
            final_concurrency = min(optimal_threads, 50, agent_count)
            
            return max(2, final_concurrency) # Luôn chạy ít nhất 2 luồng
        except:
            return 5 # Fallback an toàn nếu không đo được RAM

# ==============================================================================
# 🧠 MODULE 2: BỘ NHỚ TỰ HỌC (RAG MEMORY)
# ==============================================================================
class KnowledgeBrain:
    def __init__(self):
        try:
            # Khởi tạo Client ChromaDB
            self.client = chromadb.PersistentClient(path=CONFIG["DB_PATH"])
            
            # Nếu chạy thật thì dùng model embedding chuẩn, giả lập thì dùng mặc định
            self.collection = self.client.get_or_create_collection(name="ai_hive_mind")
            self.is_active = True
        except Exception as e:
            print(f"Memory Error: {str(e)}")
            self.is_active = False

    def memorize(self, question, answer, score):
        if not self.is_active or score < 85: return
        
        try:
            # Lưu vào DB
            self.collection.add(
                documents=[answer],
                metadatas=[{
                    "question": question, 
                    "score": score, 
                    "timestamp": str(datetime.now())
                }],
                ids=[str(uuid.uuid4())]
            )
        except Exception as e:
            print(f"Save Memory Error: {e}")

    def recall(self, question):
        if not self.is_active: return []
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=2
            )
            if results['documents'] and results['documents'][0]:
                return results['documents'][0]
        except:
            pass
        return []

# ==============================================================================
# 🤖 MODULE 3: AI AGENT WORKER
# ==============================================================================
class AIAgent:
    def __init__(self, agent_id):
        self.id = f"Agent_{agent_id:03d}"
        self.roles = ["Kỹ sư Hệ thống", "Luật sư Rủi ro", "Hacker Mũ trắng", 
                      "Nhà Kinh tế học", "Người dùng khó tính", "Chuyên gia UX/UI", 
                      "Nhà Đạo đức AI", "CEO Startup"]
        self.role = random.choice(self.roles)
        
    async def process(self, prompt, context, semaphore):
        async with semaphore: # Giới hạn số lượng chạy cùng lúc
            try:
                # 1. Chế độ Giả lập (Siêu nhanh, không tốn tiền)
                if CONFIG["SIMULATION_MODE"]:
                    delay = random.uniform(0.5, 1.5)
                    await asyncio.sleep(delay)
                    
                    content = f"[{self.role}] Tôi đề xuất giải pháp mã số {random.randint(1000,9999)}. " \
                              f"Quan điểm của tôi tập trung vào {random.choice(['Tối ưu chi phí', 'Bảo mật', 'Trải nghiệm người dùng'])}. " \
                              f"Cần lưu ý rủi ro về {random.choice(['pháp lý', 'hạ tầng', 'nhân sự'])}."
                    
                    # Vector giả lập (128 chiều)
                    vector = np.random.rand(128).tolist()
                    
                    return {
                        "id": self.id, "role": self.role, "content": content,
                        "vector": vector, "status": "SUCCESS"
                    }

                # 2. Chế độ CHẠY THẬT (Gọi API)
                else:
                    system_msg = f"Bạn là {self.role}. Nhiệm vụ: Phân tích vấn đề và đưa ra giải pháp ngắn gọn, sắc bén."
                    if context:
                        system_msg += f"\nTham khảo kinh nghiệm quá khứ: {context}"
                    
                    # Gọi LLM sinh text
                    response = await acompletion(
                        model=CONFIG["REAL_MODEL"],
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": prompt}
                        ],
                        timeout=CONFIG["TIMEOUT_SECONDS"]
                    )
                    content_text = response.choices[0].message.content

                    # Gọi API tạo Vector (Embedding) để dùng cho bước phân cụm
                    # Lưu ý: Để tiết kiệm, ta có thể dùng model 'text-embedding-3-small' của OpenAI
                    emb_response = await embedding(
                        model="text-embedding-3-small",
                        input=[content_text]
                    )
                    vector_data = emb_response.data[0]['embedding']

                    return {
                        "id": self.id, "role": self.role, "content": content_text,
                        "vector": vector_data, "status": "SUCCESS"
                    }

            except Exception as e:
                return {"id": self.id, "status": "ERROR", "error": str(e)}

# ==============================================================================
# ⚙️ MODULE 4: ORCHESTRATOR (ĐẠI HỘI ĐỒNG)
# ==============================================================================
class GrandCouncilPipeline:
    def __init__(self):
        self.brain = KnowledgeBrain()
        
    async def run(self, user_question, st_status_container=None, st_progress_bar=None, st_log_containers=None):
        """
        Hàm chạy chính, hỗ trợ cập nhật giao diện Streamlit
        st_status_container: Nơi hiện text trạng thái
        st_progress_bar: Thanh tiến trình
        st_log_containers: List 3 container (expander) để ghi log chi tiết
        """
        
        # 1. Tính toán tài nguyên
        concurrency = SystemOptimizer.calculate_safe_concurrency(CONFIG["TOTAL_AGENTS"])
        sem = asyncio.Semaphore(concurrency)
        
        # Helper để update UI an toàn
        def update_ui(text, progress):
            if st_status_container: st_status_container.markdown(f"**Trạng thái:** {text}")
            if st_progress_bar: st_progress_bar.progress(progress)
            
        update_ui(f"Đang tối ưu hệ thống... Chạy {concurrency} luồng song song.", 5)
        
        # --- BƯỚC 0: RECALL (NHỚ LẠI) ---
        past_lessons = self.brain.recall(user_question)
        context_str = ""
        if past_lessons:
            context_str = "\n".join(past_lessons)
            if st_log_containers:
                st_log_containers[0].info(f"🔮 Tìm thấy {len(past_lessons)} bài học từ quá khứ.")

        # --- BƯỚC 1: EXPANSION (1 -> 100) ---
        agents = [AIAgent(i) for i in range(CONFIG["TOTAL_AGENTS"])]
        tasks = [agent.process(user_question, context_str, sem) for agent in agents]
        
        update_ui(f"Kích hoạt {CONFIG['TOTAL_AGENTS']} Agents...", 10)
        
        # Chạy và hiển thị tiến độ realtime
        results = []
        completed = 0
        for f in asyncio.as_completed(tasks):
            res = await f
            results.append(res)
            completed += 1
            # Cập nhật thanh tiến trình từ 10% -> 60%
            prog = 10 + int((completed / CONFIG["TOTAL_AGENTS"]) * 50)
            if st_progress_bar: st_progress_bar.progress(prog)
            
            # Hiện log mẫu vài con đầu tiên
            if st_log_containers and completed <= 5:
                if res.get("status") == "SUCCESS":
                    st_log_containers[0].write(f"✅ **{res['role']}**: {res['content'][:100]}...")
                else:
                    st_log_containers[0].error(f"❌ Error: {res.get('error')}")

        valid_data = [r for r in results if r["status"] == "SUCCESS"]
        if not valid_data:
            update_ui("❌ Thất bại: Không có Agent nào trả lời thành công.", 0)
            return "System Error"

        update_ui(f"Thu thập xong {len(valid_data)} ý kiến. Đang phân tích...", 65)

        # --- BƯỚC 2: FILTERING (100 -> 10) ---
        if st_log_containers:
            st_log_containers[1].info("Đang chạy thuật toán K-Means Clustering...")
        
        # Lấy vector ra để phân cụm
        vectors = np.array([item['vector'] for item in valid_data])
        
        # Xử lý trường hợp số lượng data ít hơn số cluster yêu cầu
        n_clusters = min(CONFIG["FILTER_KEEP"], len(valid_data))
        if n_clusters < 2: n_clusters = 1
            
        kmeans = KMeans(n_clusters=n_clusters, n_init=10)
        kmeans.fit(vectors)
        
        representatives = []
        seen_clusters = set()
        
        # Chọn đại diện cho từng cụm
        for i, label in enumerate(kmeans.labels_):
            if label not in seen_clusters:
                item = valid_data[i]
                representatives.append(item)
                seen_clusters.add(label)
                # Log ra UI
                if st_log_containers:
                    st_log_containers[1].markdown(f"- **Nhóm quan điểm {label+1}** (Đại diện: {item['role']})")
                
                if len(seen_clusters) >= n_clusters: break
        
        update_ui(f"Đã cô đặc thành {len(representatives)} luồng tư tưởng chính.", 80)

        # --- BƯỚC 3: SYNTHESIS & DEBATE (10 -> 1) ---
        if st_log_containers:
            st_log_containers[2].info("Hội đồng Tối cao đang tranh biện và tổng hợp...")
            
        final_answer, confidence = await self.final_synthesis(representatives, user_question)
        
        # --- BƯỚC 4: MEMORIZE (TỰ HỌC) ---
        self.brain.memorize(user_question, final_answer, confidence)
        
        update_ui("Hoàn tất!", 100)
        return final_answer

    async def final_synthesis(self, representatives, original_question):
        """Tổng hợp cuối cùng (Giả lập hoặc gọi API)"""
        
        # Tổng hợp input
        summary_input = "\n".join([f"- [{item['role']}]: {item['content']}" for item in representatives])
        
        if CONFIG["SIMULATION_MODE"]:
            await asyncio.sleep(1.5)
            # Tạo câu trả lời giả lập có cấu trúc
            final_output = f"""
            ### 🏛️ QUYẾT NGHỊ CỦA HỘI ĐỒNG
            
            **1. Phân tích đa chiều:**
            Hệ thống đã ghi nhận {CONFIG['TOTAL_AGENTS']} ý kiến, cô đọng thành {len(representatives)} nhóm quan điểm chính.
            
            **2. Giải pháp cốt lõi:**
            Dựa trên đề xuất của nhóm {representatives[0]['role']}, chúng tôi kiến nghị giải pháp lai (Hybrid Approach).
            
            **3. Kiểm soát rủi ro:**
            Đã tích hợp cảnh báo từ nhóm {representatives[-1]['role']} để giảm thiểu rủi ro vận hành.
            
            *(Dữ liệu được tạo bởi chế độ Giả lập. Hãy nhập API Key để chạy thật)*
            """
            return final_output, random.randint(88, 98)
        
        else:
            # GỌI API ĐỂ TỔNG HỢP THẬT (Mô hình Tranh biện)
            prompt = f"""
            Bạn là Chủ tọa Hội đồng AI. Dưới đây là các luồng ý kiến đại diện từ {CONFIG['TOTAL_AGENTS']} chuyên gia về vấn đề: "{original_question}"
            
            {summary_input}
            
            NHIỆM VỤ:
            1. Tổng hợp các điểm chung.
            2. Giải quyết mâu thuẫn giữa các nhóm.
            3. Đưa ra câu trả lời cuối cùng toàn diện, chi tiết và có tính ứng dụng cao.
            4. Trình bày định dạng Markdown đẹp.
            """
            
            try:
                response = await acompletion(
                    model=CONFIG["REAL_MODEL"],
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content, 95
            except Exception as e:
                return f"Lỗi tổng hợp: {str(e)}", 0