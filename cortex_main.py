import asyncio
# 1. Import Tài nguyên từ Hành lang
from Neural_Corridor.neuron import NeuronAgent
from Neural_Corridor.motor_cortex import MotorCortex
# Import 7 Giác quan
from Neural_Corridor.occipital import OccipitalLobe
from Neural_Corridor.auditory import AuditoryCortex
from Neural_Corridor.olfactory import OlfactoryBulb
from Neural_Corridor.gustatory import GustatoryCortex
from Neural_Corridor.somatosensory import SomatosensoryCortex
from Neural_Corridor.vestibular import VestibularSystem
from Neural_Corridor.intuition import Intuition

# 2. Import 4 Bộ Não con
import Brain_Strategy.prefrontal_cortex as Strat_PFC
import Brain_Strategy.amygdala as Strat_Amygdala
import Brain_Strategy.broca as Strat_Broca

import Brain_Operation.prefrontal_cortex as Oper_PFC
import Brain_Operation.amygdala as Oper_Amygdala
import Brain_Operation.broca as Oper_Broca

import Brain_Risk_QC.prefrontal_cortex as Risk_PFC
import Brain_Risk_QC.amygdala as Risk_Amygdala
import Brain_Risk_QC.broca as Risk_Broca

import Brain_Market.prefrontal_cortex as Mark_PFC
import Brain_Market.amygdala as Mark_Amygdala
import Brain_Market.broca as Mark_Broca

class CortexMain:
    def __init__(self):
        self.hand = MotorCortex()
        # Khởi tạo 7 giác quan
        self.senses = {
            "eye": OccipitalLobe(), "ear": AuditoryCortex(),
            "nose": OlfactoryBulb(), "tongue": GustatoryCortex(),
            "skin": SomatosensoryCortex(), "balance": VestibularSystem(),
            "spirit": Intuition()
        }

    async def gather_sensory_data(self, text):
        """Quét 7 giác quan"""
        reports = []
        r1 = self.senses["eye"].analyze(text)
        r2 = self.senses["ear"].listen(text)
        r3 = self.senses["nose"].smell(text)
        r4 = self.senses["tongue"].taste(text)
        r5 = self.senses["skin"].feel(text)
        r6 = self.senses["balance"].balance(text)
        r7 = self.senses["spirit"].predict(text)
        
        for r in [r1, r2, r3, r4, r5, r6, r7]:
            if r: reports.append(r)
        return "\n".join(reports) if reports else "Không phát hiện tín hiệu đặc biệt."

    async def activate_organ(self, organ_mod, context, semaphore):
        """Kích hoạt 1 cơ quan cụ thể (VD: Amygdala)"""
        agents = [NeuronAgent(i, organ_mod.NAME, organ_mod.ROLES) for i in range(1)] # Dùng 1 agent đại diện cho nhanh
        tasks = [a.activate(f"NV: {organ_mod.MISSION}\nCONTEXT: {context}", semaphore) for a in agents]
        return await asyncio.gather(*tasks)

    async def run_full_brain_process(self, brain_package, user_input, ui_placeholder):
        sem = asyncio.Semaphore(10)
        (mod_pfc, mod_amygdala, mod_broca) = brain_package
        
        with ui_placeholder.container():
            # BƯỚC 1: GIÁC QUAN (Senses)
            senses_report = await self.gather_sensory_data(user_input)
            ui_placeholder.info(f"📡 GIÁC QUAN:\n{senses_report}")
            
            # BƯỚC 2: AMYGDALA (Sợ hãi)
            res_amy = await self.activate_organ(mod_amygdala, user_input + "\n" + senses_report, sem)
            risk_text = res_amy[0]['content']
            
            # BƯỚC 3: PFC (Lý trí)
            pfc_input = f"INPUT: {user_input}\nRỦI RO: {risk_text}"
            res_pfc = await self.activate_organ(mod_pfc, pfc_input, sem)
            decision_text = res_pfc[0]['content']
            
            # BƯỚC 4: MOTOR (Hành động)
            action_text = await self.hand.execute_command(decision_text)
            if action_text != "💤 (Không hành động)":
                ui_placeholder.warning(f"⚙️ {action_text}")

            # BƯỚC 5: BROCA (Lời nói)
            broca_input = f"QUYẾT ĐỊNH: {decision_text}\nHÀNH ĐỘNG: {action_text}"
            res_bro = await self.activate_organ(mod_broca, broca_input, sem)
            
            # Hiển thị kết quả cuối cùng
            ui_placeholder.success(f"🗣️ {res_bro[0]['content']}")

    async def process_hive_mind(self, user_input, ui_map):
        tasks = []
        brains = {
            "STRATEGY": (Strat_PFC, Strat_Amygdala, Strat_Broca),
            "OPERATION": (Oper_PFC, Oper_Amygdala, Oper_Broca),
            "RISK": (Risk_PFC, Risk_Amygdala, Risk_Broca),
            "MARKET": (Mark_PFC, Mark_Amygdala, Mark_Broca)
        }
        
        for key, package in brains.items():
            if key in ui_map:
                tasks.append(self.run_full_brain_process(package, user_input, ui_map[key]))
        
        await asyncio.gather(*tasks)
