class OlfactoryBulb:
    def smell(self, t): return "👃 [KHỨU GIÁC] Có mùi khét/Gas" if "khét" in t.lower() or "mùi" in t.lower() else None
