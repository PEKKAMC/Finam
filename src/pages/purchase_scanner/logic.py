# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os

import requests

from src.database import db
from src.logger import Logger

BACKEND_URL = "https://finam-backend.vercel.app/"
APP_SECRET_TOKEN = os.environ.get("APP_SECRET_TOKEN")


class LogicController:
    def __init__(self, username: str = "Admin"):
        self.current_user = username or "Admin"

    @staticmethod
    def analyze_purchase(name: str, price: str, reason: str, trigger: str, time: str):
        try:
            price = float(price.strip()) if price and str(price).strip() else 0.0
        except (ValueError, AttributeError):
            price = 0.0

        trigger_texts = {
            "need": "nhu cầu thật sự",
            "social": "áp lực bạn bè",
            "tiktok": "nội dung social media",
            "sale": "flash sale/giảm giá",
            "emotion": "cảm xúc nhất thời",
        }
        trigger_display = trigger_texts.get(trigger, "yếu tố bên ngoài")

        local_risk = 15
        if price > 500000:
            local_risk += 15
        if price > 1000000:
            local_risk += 15

        if trigger == "social":
            local_risk += 22
        elif trigger == "tiktok":
            local_risk += 25
        elif trigger == "sale":
            local_risk += 20
        elif trigger == "emotion":
            local_risk += 25

        thinking_lower = (time or "").lower()
        try:
            parts = thinking_lower.split()
            val = float(parts[0]) if parts and parts[0].replace(".", "", 1).isdigit() else 1.0
            unit = parts[1] if len(parts) > 1 else "hour"

            total_hours = val
            if "day" in unit:
                total_hours = val * 24
            elif "week" in unit:
                total_hours = val * 24 * 7
            elif "minute" in unit:
                total_hours = val / 60.0
            elif "month" in unit:
                total_hours = val * 24 * 30

            if total_hours < 1:
                local_risk += 25
            elif total_hours < 24:
                local_risk += 18
            elif total_hours < 72:
                local_risk += 10
            else:
                local_risk += 2
        except Exception:
            if "minute" in thinking_lower or "hour" in thinking_lower:
                local_risk += 22
            elif "day" in thinking_lower or "tuần" in thinking_lower:
                local_risk += 10

        keywords = [
            "sale",
            "trend",
            "tiktok",
            "bạn bè",
            "sợ hết",
            "hot",
            "review",
            "chán",
            "buồn",
            "stress",
            "fomo",
        ]
        reason_lower = (reason or "").lower()
        for keyword in keywords:
            if keyword in reason_lower:
                local_risk += 5

        local_risk = min(100, local_risk)

        risk = None
        ai_advice = ""

        try:
            endpoint = f"{BACKEND_URL.rstrip('/')}/api/v1/purchase-advice"
            payload = {
                "item_name": name or "Sản phẩm",
                "price": price if price > 0 else 1.0,
                "currency": "VND",
                "category": trigger_display,
                "monthly_budget_remaining": 5000000.0,
                "user_notes": f"Lý do: {reason or 'Không có'}. Thời gian suy nghĩ: {time}.",
            }
            headers = {
                "Content-Type": "application/json",
                "X-App-Token": APP_SECRET_TOKEN or "",
            }

            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                raw_risk = data.get("risk")
                risk = int(raw_risk) if raw_risk is not None else None
                ai_advice = data.get("advice", "")
            else:
                raise RuntimeError(f"Server status {response.status_code}: {response.text}")

        except Exception as ex:
            risk = local_risk
            ai_advice = "Đang sử dụng bộ phân tích cục bộ (Không thể kết nối tới server AI)."
            Logger.warn(f"AI analysis failed: {ex}. Using local fallback. Risk: {risk}")

        if risk is None:
            ai_advice = ai_advice or "Đầu vào bị đánh dấu là nội dung troll hoặc không hợp lệ để phân tích."

        return risk, trigger_display, price, ai_advice

    def save_scan_result(self, item_name: str, price: float, trigger: str, reason: str, thinking_time: str, risk_score: int | None, trigger_display: str, ai_advice: str) -> bool:
        if risk_score is None:
            return False
        return db.scanner_history.add_scan_result(self.current_user, item_name, price, trigger, reason, thinking_time, risk_score, trigger_display, ai_advice)

    def get_scan_history(self):
        return db.scanner_history.get_user_scan_history(self.current_user)

    def delete_scan_result(self, scan_id: int | None) -> bool:
        if scan_id is None:
            return False
        return db.scanner_history.delete_scan_result(self.current_user, scan_id)

    def clear_scan_history(self) -> bool:
        return db.scanner_history.clear_user_scan_history(self.current_user)
