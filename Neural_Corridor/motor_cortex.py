class MotorCortex:
    async def execute_command(self, decision):
        actions = []
        if "mail" in decision.lower(): actions.append("📧 SOẠN EMAIL")
        if "dừng" in decision.lower(): actions.append("🛑 DỪNG MÁY KHẨN CẤP")
        if "lưu" in decision.lower(): actions.append("💾 LƯU LOG")
        if "gọi" in decision.lower(): actions.append("📞 GỌI ĐIỆN")
        return " + ".join(actions) if actions else "💤 (Không hành động)"
