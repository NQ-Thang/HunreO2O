"""
HUNRE E-COMMERCE AI ENGINE
Module: Dynamic Price Negotiator & Reverse Auction Agent
Tính toán giá giảm tự động theo thời gian (Time-decay Pricing) và đàm phán giá theo Điểm Uy Tín
"""

import math
from typing import Dict, Any

class PriceNegotiatorAgent:
    @staticmethod
    def calculate_decay_price(
        original_price: float,
        floor_price: float,
        hours_elapsed: float,
        decay_half_life_hours: float = 72.0
    ) -> Dict[str, Any]:
        """
        Tính toán giá giảm tự động theo hàm phân rã thời gian (Exponential Decay Curve):
        P(t) = P_floor + (P_original - P_floor) * e^(-lambda * t)
        Đảm bảo giá không bao giờ giảm xuống dưới Giá Sàn (Floor Price).
        """
        decay_constant = math.log(2) / decay_half_life_hours
        decayed_excess = (original_price - floor_price) * math.exp(-decay_constant * hours_elapsed)
        current_price = round(max(floor_price, floor_price + decayed_excess), -3) # Làm tròn tới nghìn đồng

        discount_percentage = round((1 - current_price / original_price) * 100, 1) if original_price > 0 else 0

        return {
            "original_price": original_price,
            "floor_price": floor_price,
            "hours_elapsed": hours_elapsed,
            "current_decayed_price": current_price,
            "discount_percentage": discount_percentage,
            "is_at_floor": current_price <= floor_price
        }

    @staticmethod
    def negotiate_offer(
        item_current_price: float,
        item_floor_price: float,
        buyer_offer_price: float,
        buyer_trust_score: int
    ) -> Dict[str, Any]:
        """
        AI Agent đóng vai trò Trợ lý bán hàng tự động thương lượng giá:
        Dựa trên:
        - Khoảng cách giữa giá trả và giá sàn
        - Điểm uy tín của người mua (Trust Score từ 100 đến 1000)
        """
        # Nếu người mua trả giá cao hơn hoặc bằng giá niêm yết
        if buyer_offer_price >= item_current_price:
            return {
                "decision": "ACCEPT",
                "final_price": buyer_offer_price,
                "message": "Giá trả hợp lý, giao dịch được phê duyệt ngay lập tức!"
            }

        # Nếu người mua trả dưới giá sàn tuyệt đối của người bán
        if buyer_offer_price < item_floor_price:
            # Nếu người mua có điểm uy tín rất cao (>600), AI đưa ra mức thỏa hiệp gần giá sàn
            if buyer_trust_score >= 600:
                counter_offer = round(item_floor_price * 1.03, -3) # Giá sàn + 3%
                return {
                    "decision": "COUNTER_OFFER",
                    "counter_offer_price": counter_offer,
                    "message": f"Mức giá bạn đưa ra dưới giá sàn của bạn bán. Tuy nhiên nhờ điểm uy tín HUNRE cao ({buyer_trust_score} điểm), hệ thống đề xuất giá ưu đãi: {int(counter_offer):,}đ."
                }
            else:
                return {
                    "decision": "REJECT",
                    "floor_price_hint": item_floor_price,
                    "message": "Giá đề xuất quá thấp so với giá sàn người bán đặt ra."
                }

        # Người mua trả trong khoảng [Floor Price, Current Price]
        # Hệ thống tính điểm chấp nhận dựa vào Trust Score
        acceptance_threshold = 0.5 - (buyer_trust_score / 2000.0) # Trust score càng cao, ngưỡng chấp nhận càng dễ
        price_ratio = (buyer_offer_price - item_floor_price) / (item_current_price - item_floor_price + 1e-5)

        if price_ratio >= acceptance_threshold:
            return {
                "decision": "ACCEPT",
                "final_price": buyer_offer_price,
                "message": f"Thương lượng thành công! Giá chốt: {int(buyer_offer_price):,}đ."
            }
        else:
            # Đưa ra giá đàm phán trung gian
            mid_price = round((buyer_offer_price + item_current_price) / 2, -3)
            return {
                "decision": "COUNTER_OFFER",
                "counter_offer_price": mid_price,
                "message": f"Bạn bán chưa thể chốt ở giá này. Mức giá thương lượng AI đề xuất là: {int(mid_price):,}đ."
            }
