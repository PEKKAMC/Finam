#Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
import json
from google import genai
from google.genai import types

from src.logger import Logger

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_purchase(name: str, price_val: float, reason: str, trigger_display: str, time: str) -> tuple[int, str]:
    """Sends user input details to Gemini AI to get a structured risk score and personalized advice."""

    prompt = f"""
    Bạn là một chuyên gia tài chính cá nhân tâm lý học. Hãy phân tích quyết định mua sắm sau đây và đánh giá mức độ bốc đồng/rủi ro tài chính:
    - Món hàng: {name}
    - Giá tiền: {price_val} VND
    - Lý do: {reason}
    - Nguồn kích thích chính: {trigger_display}
    - Thời gian suy nghĩ: {time}

    Trả về kết quả CHỈ bằng định dạng JSON với các trường sau (không kèm markdown):
    {{
        "risk": <số nguyên từ 0 đến 100 thể hiện phần trăm rủi ro mua sắm bốc đồng>,
        "advice": "<Một câu nhận xét hoặc lời khuyên sắc bén, đồng cảm và cá nhân hóa cho món hàng này>"
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        ai_data = json.loads(str(response.text))
        risk = int(ai_data.get("risk", 50))
        ai_advice = ai_data.get("advice", "Hãy cân nhắc kỹ lưỡng trước khi mua.")
        return risk, ai_advice

    except Exception as e:
        Logger.error(f"Gemini API Error: {e}")
        raise e