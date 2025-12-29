# neuron.py
import asyncio
import random
import numpy as np
from litellm import acompletion, embedding
from settings import CONFIG, FACTORY_ROLES # Gọi DNA vào

class NeuronAgent:
    def __init__(self, agent_id):
        self.id = f"Neuron_{agent_id:03d}"
        self.role = random.choice(FACTORY_ROLES)
        
    async def activate(self, signal_input, semaphore):
        """
        signal_input: Câu hỏi của người dùng
        semaphore: Để kiểm soát không cho quá nhiều noron bắn cùng lúc
        """
        async with semaphore:
            try:
                # --- TRƯỜNG HỢP GIẢ LẬP (Mô phỏng phản xạ) ---
                if CONFIG["SIMULATION_MODE"]:
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    # Kịch bản phản xạ có điều kiện (Bavia case)
                    if "bavia" in signal_input.lower() or "lỗi" in signal_input.lower():
                        if "Tài chính" in self.role:
                            output = f"[{self.role}] Dòng tiền quan trọng hơn. Chấp nhận rủi ro xuất hàng để thu tiền, xử lý đền bù sau."
                        elif "QC" in self.role:
                            output = f"[{self.role}] Tuyệt đối không xuất. Uy tín là tài sản lớn nhất. Giữ lại sửa 100%."
                        else:
                            output = f"[{self.role}] Cần giải pháp lai: Lọc 20% xấu nhất, xuất 80% còn lại."
                    else:
                        output = f"[{self.role}] Phân tích tín hiệu dựa trên quy trình chuẩn."
                    
                    # Vector ngẫu nhiên
                    vector = np.random.rand(1536).tolist()
                    return {"id": self.id, "role": self.role, "content": output, "vector": vector, "status": "SUCCESS"}

                # --- TRƯỜNG HỢP CHẠY THẬT (Kích hoạt trí tuệ) ---
                else:
                    prompt = f"""
                    Bạn là: {self.role}. 
                    Tín hiệu đầu vào: "{signal_input}"
                    Nhiệm vụ: Đưa ra quyết định dứt khoát dựa trên lợi ích cốt lõi của vị trí bạn nắm giữ.
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
                    return {"id": self.id, "role": self.role, "content": content_text, "vector": emb_res.data[0]['embedding'], "status": "SUCCESS"}

            except Exception as e:
                return {"id": self.id, "status": "ERROR", "error": str(e)}
