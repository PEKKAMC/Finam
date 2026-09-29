# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
import requests
from src.logger import Logger

BACKEND_URL = "https://finam-backend.vercel.app/"
APP_SECRET_TOKEN = os.environ.get("APP_SECRET_TOKEN")


class LogicController:
    def __init__(self):
        pass

    @staticmethod
    def analyze_purchase(name: str, price: str, reason: str, trigger: str, time: str):
        try:
            price = float(price.strip()) if price and str(price).strip() else 0.0
        except (ValueError, AttributeError):
            price = 0.0

        trigger_texts = {
            'need': 'nhu cầu thật sự',
            'social': 'áp lực bạn bè',
            'tiktok': 'nội dung social media',
            'sale': 'flash sale/giảm giá',
            'emotion': 'cảm xúc nhất thời'
        }
        trigger_display = trigger_texts.get(trigger, 'yếu tố bên ngoài')

        # Local fallback risk calculation
        local_risk = 15
        if price > 500000: local_risk += 15
        if price > 1000000: local_risk += 15

        if trigger == 'social': local_risk += 22
        elif trigger == 'tiktok': local_risk += 25
        elif trigger == 'sale': local_risk += 20
        elif trigger == 'emotion': local_risk += 25

        if time == 'short': local_risk += 22
        elif time == 'medium': local_risk += 10

        keywords = ['sale', 'trend', 'tiktok', 'bạn bè', 'sợ hết', 'hot', 'review', 'chán', 'buồn', 'stress', 'fomo']
        reason_lower = (reason or "").lower()
        for k in keywords:
            if k in reason_lower:
                local_risk += 5

        local_risk = min(100, local_risk)

        # Call AI backend proxy
        try:
            endpoint = f"{BACKEND_URL.rstrip('/')}/api/v1/purchase-advice"
            payload = {
                "item_name": name or "Sản phẩm",
                "price": price if price > 0 else 1.0,
                "currency": "VND",
                "category": trigger_display,
                "monthly_budget_remaining": 5000000.0,
                "user_notes": f"Lý do: {reason or 'Không có'}. Thời gian suy nghĩ: {time}."
            }
            headers = {
                "Content-Type": "application/json",
                "X-App-Token": APP_SECRET_TOKEN
            }

            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                risk = int(data.get("risk", local_risk))
                ai_advice = data.get("advice", "")
            else:
                raise RuntimeError(f"Server status {response.status_code}: {response.text}")

        except Exception as e:
            risk = local_risk
            ai_advice = "Đang sử dụng bộ phân tích cục bộ (Không thể kết nối tới server AI)."
            Logger.warn(f"AI analysis failed: {e}. Using local fallback. Risk: {risk}")

        return risk, trigger_display, price, ai_advice