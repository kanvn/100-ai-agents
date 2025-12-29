import asyncio, random
from .settings import CONFIG

class NeuronAgent:
    def __init__(self, agent_id, region, roles):
        self.id = f"{region}_{agent_id}"
        self.role = random.choice(roles)
    
    async def activate(self, signal, semaphore):
        async with semaphore:
            if CONFIG["SIMULATION_MODE"]:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                return {"role": self.role, "content": f"[{self.role}] Phân tích tín hiệu: {signal[:30]}...", "status": "SUCCESS"}
            return {"role": self.role, "content": "API Placeholder", "status": "SUCCESS"}
