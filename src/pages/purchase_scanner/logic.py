# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

#from src.ai.advisor import analyze_purchase
from src.logger import Logger


class LogicController:
    def __init__(self):
        pass

    @staticmethod
    def analyze_purchase(name: str, price: str, reason: str, trigger: str, time: str):
        try:
            price_val = float(price) if price else 0
        except ValueError:
            price_val = 0

        trigger_texts = {
            'need': 'nhu cầu thật sự',
            'social': 'áp lực bạn bè',
            'tiktok': 'nội dung social media',
            'sale': 'flash sale/giảm giá',
            'emotion': 'cảm xúc nhất thời'
        }
        trigger_display = trigger_texts.get(trigger, 'yếu tố bên ngoài')

        try:
            risk, ai_advice = analyze_purchase(name, price_val, reason, trigger_display, time)
        except Exception as e:
            risk = 15
            if price_val > 500000: risk += 15
            if price_val > 1000000: risk += 15

            if trigger == 'social': risk += 22
            elif trigger == 'tiktok': risk += 25
            elif trigger == 'sale': risk += 20
            elif trigger == 'emotion': risk += 25

            if time == 'short': risk += 22
            elif time == 'medium': risk += 10

            keywords = ['sale', 'trend', 'tiktok', 'bạn bè', 'sợ hết', 'hot', 'review', 'chán', 'buồn', 'stress', 'fomo']
            reason_lower = (reason or "").lower()
            for k in keywords:
                if k in reason_lower:
                    risk += 5

            risk = min(100, risk)
            ai_advice = "Đang sử dụng bộ phân tích cục bộ (Không có kết nối AI)."

            Logger.warn(f"AI analysis failed: {e}. Using local risk calculation. Risk: {risk}, Advice: {ai_advice}")

        return risk, trigger_display, price_val, ai_advice