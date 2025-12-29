class AuditoryCortex:
    def listen(self, t): return "👂 [THÍNH GIÁC] Ồn > 90dB" if "kêu" in t.lower() or "ồn" in t.lower() else None
