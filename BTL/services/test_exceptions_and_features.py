"""
HUNRE E-COMMERCE - COMPREHENSIVE FEATURE & EXCEPTION TEST SUITE
Kiểm thử toàn diện cả chức năng thành công (Happy Path) VÀ các trường hợp ngoại lệ (Exceptions & Edge Cases)
cho 5 Microservices:
- Auth & Trust Score
- Product Catalog CRUD
- Escrow Saga & Dispute
- Hub Logistics & TOTP QR
- AI Pricing & Negotiation
"""

import sys
import os
import json
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from local_api_server import app, DEFAULT_DB, save_db

client = TestClient(app)

def run_tests():
    # Đặt lại CSDL sạch ban đầu
    save_db(DEFAULT_DB)

    passed_tests = 0
    failed_tests = 0
    results = []

    def check(test_id, category, name, condition, details=""):
        nonlocal passed_tests, failed_tests
        if condition:
            passed_tests += 1
            status = "PASS"
        else:
            failed_tests += 1
            status = "FAIL"
        results.append({
            "id": test_id,
            "category": category,
            "name": name,
            "status": status,
            "details": details
        })
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {icon} [{category}] {name} {details}")

    print("\n" + "=" * 70)
    print("BAT DAU KIEM THU TOAN DIEN CHUC NANG & NGOAI LE (FEATURE & EXCEPTION TESTS)")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. AUTH SERVICE: CHUC NANG & NGOAI LE
    # -------------------------------------------------------------
    print("\n--- 1. AUTH SERVICE & TRUST SCORE ENGINE ---")
    
    # 1.1 Happy: Lấy trust score hợp lệ
    res = client.get("/api/v1/auth/users/trust-score?user_id=1")
    check("AUTH-01", "AUTH", "Happy Path: Lay Trust Score cua SV An", 
          res.status_code == 200 and res.json()["data"]["trust_score"] == 520,
          f"Status: {res.status_code}")

    # 1.2 Ngoại lệ: Đăng ký bằng email KHÔNG PHẢI @hunre.edu.vn (KYC Failed)
    res = client.post("/api/v1/auth/register", json={
        "student_code": "20218888",
        "full_name": "Nguyen Van Gia Mao",
        "email": "giamao@gmail.com"  # Ngoại lệ: Không phải email trường
    })
    check("AUTH-EX-01", "AUTH", "Ngoai Le 1: Tu choi email ngoai truong (@gmail.com)", 
          res.status_code == 422 and "KYC Failed" in res.json().get("detail", ""),
          f"Status: {res.status_code} - Detail: {res.json().get('detail', '')}")

    # 1.3 Ngoại lệ: Đăng ký thiếu Mã SV hoặc Họ tên
    res = client.post("/api/v1/auth/register", json={
        "student_code": "   ",
        "full_name": "",
        "email": "sinhvienmoi@hunre.edu.vn"
    })
    check("AUTH-EX-02", "AUTH", "Ngoai Le 2: Tu choi thieu Ma SV hoac Ho ten", 
          res.status_code == 422,
          f"Status: {res.status_code}")

    # 1.4 Ngoại lệ: Đăng ký trùng email đã có trong hệ thống
    res = client.post("/api/v1/auth/register", json={
        "student_code": "20211001",
        "full_name": "Trung Email",
        "email": "an.nv@hunre.edu.vn"  # Trùng với SV 1
    })
    check("AUTH-EX-03", "AUTH", "Ngoai Le 3: Tu choi trung email da ton tai (409 Conflict)", 
          res.status_code == 409,
          f"Status: {res.status_code}")

    # -------------------------------------------------------------
    # 2. PRODUCT SERVICE: CRUD & NGOAI LE
    # -------------------------------------------------------------
    print("\n--- 2. PRODUCT SERVICE (CRUD ENGINE & VALIDATION) ---")

    # 2.1 Happy: Thêm mới sản phẩm hợp lệ
    res = client.post("/api/v1/products", json={
        "title": "Giao trinh Toan Cao Cap A1 (Chuan HUNRE)",
        "category_id": "BOOKS",
        "original_price": 70000.0,
        "current_price": 60000.0,
        "floor_price": 50000.0,
        "desired_exchange_items": "Casio 580",
        "seller_id": 1
    })
    created_id = res.json()["data"]["id"] if res.status_code == 200 else None
    check("PROD-01", "PRODUCT", "Happy Path: Dang ban san pham moi thanh cong", 
          res.status_code == 200 and created_id is not None,
          f"New Product ID: {created_id}")

    # 2.2 Ngoại lệ: Đăng bán với tiêu đề rỗng
    res = client.post("/api/v1/products", json={
        "title": "   ",  # Tiêu đề rỗng
        "current_price": 50000.0,
        "original_price": 50000.0
    })
    check("PROD-EX-01", "PRODUCT", "Ngoai Le 1: Tu choi tieu de rong (400 Bad Request)", 
          res.status_code == 400 and "không được để trống" in res.json().get("detail", ""),
          f"Status: {res.status_code}")

    # 2.3 Ngoại lệ: Đăng bán với giá bán <= 0 (Giá âm hoặc 0đ)
    res = client.post("/api/v1/products", json={
        "title": "Sach gia 0 dong hoac am",
        "current_price": -20000.0,
        "original_price": 50000.0
    })
    check("PROD-EX-02", "PRODUCT", "Ngoai Le 2: Tu choi gia ban <= 0", 
          res.status_code == 400 and "lớn hơn 0" in res.json().get("detail", ""),
          f"Status: {res.status_code}")

    # 2.4 Ngoại lệ: Giá sàn lớn hơn giá bán (floor_price > current_price)
    res = client.post("/api/v1/products", json={
        "title": "Sach loi gia san vo ly",
        "current_price": 50000.0,
        "original_price": 50000.0,
        "floor_price": 80000.0  # Giá sàn 80k > Giá bán 50k
    })
    check("PROD-EX-03", "PRODUCT", "Ngoai Le 3: Tu choi gia san lon hon gia ban", 
          res.status_code == 400 and "Giá sàn" in res.json().get("detail", ""),
          f"Status: {res.status_code}")

    # 2.5 Ngoại lệ: Xem chi tiết sản phẩm không tồn tại (ID 99999)
    res = client.get("/api/v1/products/99999")
    check("PROD-EX-04", "PRODUCT", "Ngoai Le 4: Xem san pham khong ton tai (404 Not Found)", 
          res.status_code == 404,
          f"Status: {res.status_code}")

    # 2.6 Ngoại lệ: Cập nhật sản phẩm không tồn tại
    res = client.put("/api/v1/products/99999", json={"title": "Sua san pham ma"})
    check("PROD-EX-05", "PRODUCT", "Ngoai Le 5: Sua san pham khong ton tai (404)", 
          res.status_code == 404,
          f"Status: {res.status_code}")

    # 2.7 Ngoại lệ: Xóa sản phẩm không tồn tại
    res = client.delete("/api/v1/products/99999")
    check("PROD-EX-06", "PRODUCT", "Ngoai Le 6: Xoa san pham khong ton tai (404)", 
          res.status_code == 404,
          f"Status: {res.status_code}")

    # 2.8 Happy & Edge: Tìm kiếm với từ khóa không khớp
    res = client.get("/api/v1/products?keyword=khong_co_mon_do_nay_tren_doi_98765")
    check("PROD-02", "PRODUCT", "Edge Case: Tim kiem tu khoa khong ton tai tra ve mang rong []", 
          res.status_code == 200 and len(res.json().get("data", [])) == 0,
          f"Count: {res.json().get('count')}")

    # -------------------------------------------------------------
    # 3. ESCROW SERVICE: SAGA, DISPUTE & NGOAI LE
    # -------------------------------------------------------------
    print("\n--- 3. ESCROW SERVICE (SAGA FLOW & DISPUTE HANDLING) ---")

    # 3.1 Happy: Tạo đơn ký quỹ hợp lệ
    res = client.post("/api/v1/escrow/orders", json={
        "product_id": 1,
        "buyer_id": 2,
        "agreed_price": 70000.0
    })
    order_code = res.json()["order"]["order_code"] if res.status_code == 200 else None
    check("ESCROW-01", "ESCROW", "Happy Path: Tao don ky quy Smart Escrow thanh cong", 
          res.status_code == 200 and order_code is not None,
          f"Order Code: {order_code}")

    # 3.2 Ngoại lệ: Tạo đơn ký quỹ cho sản phẩm không tồn tại
    res = client.post("/api/v1/escrow/orders", json={
        "product_id": 88888,
        "buyer_id": 1
    })
    check("ESCROW-EX-01", "ESCROW", "Ngoai Le 1: Tu choi tao don voi product_id khong ton tai (404)", 
          res.status_code == 404,
          f"Status: {res.status_code}")

    # 3.3 Ngoại lệ: Gửi hành động Saga bất hợp lệ (Action không hỗ trợ)
    res = client.post("/api/v1/escrow/saga/advance", json={
        "order_code": order_code,
        "action": "HACK_RUT_TIEN_TRAI_PHEP"
    })
    check("ESCROW-EX-02", "ESCROW", "Ngoai Le 2: Tu choi hanh dong Saga khong hop le (400 Bad Request)", 
          res.status_code == 400 and "không hợp lệ" in res.json().get("detail", ""),
          f"Status: {res.status_code}")

    # 3.4 Ngoại lệ: Gửi thao tác trên đơn hàng không tồn tại
    res = client.post("/api/v1/escrow/saga/advance", json={
        "order_code": "ORD-KHONG-CO-TRONG-CSDL",
        "action": "CHECKIN"
    })
    check("ESCROW-EX-03", "ESCROW", "Ngoai Le 3: Thao tac tren ma don khong ton tai (404)", 
          res.status_code == 404,
          f"Status: {res.status_code}")

    # 3.5 Happy & Exception Handling: Khiếu nại đơn hàng (DISPUTE)
    res = client.post(f"/api/v1/escrow/orders/{order_code}/dispute")
    check("ESCROW-02", "ESCROW", "Xu Ly Khieu Nai: Chuyen trang thai sang DISPUTED, dong bang tien", 
          res.status_code == 200 and res.json()["order"]["status"] == "DISPUTED",
          f"New Status: {res.json()['order']['status']}")

    # -------------------------------------------------------------
    # 4. HUB LOGISTICS: LOCKER ALLOCATION & NGOAI LE
    # -------------------------------------------------------------
    print("\n--- 4. HUB LOGISTICS SERVICE (LOCKER & TOTP QR) ---")

    # 4.1 Happy: Quét Check-in nhận đồ cấp phát ô tủ
    res = client.post("/api/v1/hub/checkin", json={
        "order_code": "ORD-HUNRE-TEST-01",
        "scan_type": "CHECKIN"
    })
    check("HUB-01", "HUB", "Happy Path: Quet Check-in cap phat o tu Locker OCCUPIED", 
          res.status_code == 200 and res.json()["locker"]["status"] == "OCCUPIED",
          f"Locker: {res.json()['locker']['locker_code']}")

    # 4.2 Happy: Quét Check-out giải phóng ô tủ
    res = client.post("/api/v1/hub/checkout", json={
        "order_code": "ORD-HUNRE-TEST-01",
        "scan_type": "CHECKOUT"
    })
    check("HUB-02", "HUB", "Happy Path: Quet Check-out ban giao va giai phong tu EMPTY", 
          res.status_code == 200 and res.json()["locker"]["status"] == "EMPTY",
          f"Locker: {res.json()['locker']['locker_code']}")

    # 4.3 Ngoại lệ: Check-out một đơn hàng không nằm trong ô tủ nào
    res = client.post("/api/v1/hub/checkout", json={
        "order_code": "ORD-KHONG-CO-TRONG-TU-NAO",
        "scan_type": "CHECKOUT"
    })
    check("HUB-EX-01", "HUB", "Ngoai Le 1: Check-out don hang khong co trong Locker bao loi 404", 
          res.status_code == 404,
          f"Status: {res.status_code} - Detail: {res.json().get('detail')}")

    # 4.4 Happy: Kiểm tra mã Dynamic QR TOTP xoay 30 giây
    res = client.get("/api/v1/hub/orders/ORD-HUNRE-98471/dynamic-qr")
    token1 = res.json()["data"]["token"]
    expires1 = res.json()["data"]["expires_in_seconds"]
    check("HUB-03", "HUB", "Happy Path: Sinh Dynamic QR HMAC-SHA256 16 ky tu xoay 30s", 
          res.status_code == 200 and len(token1) == 16 and 0 <= expires1 <= 30,
          f"Token: {token1} - Expires in: {expires1}s")

    # -------------------------------------------------------------
    # 5. AI ENGINE PROXY & NEGOTIATION LOGIC
    # -------------------------------------------------------------
    print("\n--- 5. AI PRICING AGENT & NEGOTIATION ---")

    # 5.1 Happy: Giá đề xuất hợp lý (>= giá sàn)
    res = client.post("/api/v1/ai/pricing/negotiate", json={
        "item_current_price": 75000,
        "item_floor_price": 60000,
        "buyer_offer_price": 65000,
        "buyer_trust_score": 520
    })
    check("AI-01", "AI", "Happy Path: Tra gia hop ly (65k >= 60k san) duoc AI ACCEPT", 
          res.status_code == 200 and res.json().get("decision") == "ACCEPT",
          f"Decision: {res.json().get('decision')}")

    # 5.2 Ngoại lệ: Giá đề xuất quá thấp so với giá sàn (< 60.000đ và SV bậc Bạc) -> AI từ chối REJECT
    res = client.post("/api/v1/ai/pricing/negotiate", json={
        "item_current_price": 75000,
        "item_floor_price": 60000,
        "buyer_offer_price": 40000,  # 40k < 60k giá sàn
        "buyer_trust_score": 520
    })
    check("AI-EX-01", "AI", "Ngoai Le 1: Tra gia duoi gia san bi AI REJECT tu choi", 
          res.status_code == 200 and res.json().get("decision") == "REJECT",
          f"Decision: {res.json().get('decision')} - Message: {res.json().get('message')}")

    # 5.3 Ngoại lệ & Thương lượng: Sinh viên uy tín cao (Trust Score >= 600) được ưu đãi COUNTER_OFFER
    res = client.post("/api/v1/ai/pricing/negotiate", json={
        "item_current_price": 75000,
        "item_floor_price": 60000,
        "buyer_offer_price": 55000,  # Dưới sàn nhưng SV uy tín cao
        "buyer_trust_score": 750    # Sinh viên hạng Vàng
    })
    check("AI-EX-02", "AI", "Ngoai Le 2: SV uy tin cao (Trust Score 750) duoc de xuat COUNTER_OFFER", 
          res.status_code == 200 and res.json().get("decision") == "COUNTER_OFFER",
          f"Decision: {res.json().get('decision')} - Counter Price: {res.json().get('counter_offer_price')}đ")

    # -------------------------------------------------------------
    # TONG KET KET QUA
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"TONG KET KIEM THU: {passed_tests}/{passed_tests + failed_tests} TESTS PASSED")
    print(f"TY LE THANH CONG: {(passed_tests / (passed_tests + failed_tests)) * 100:.1f}%")
    print("=" * 70 + "\n")

    return passed_tests, failed_tests, results

if __name__ == "__main__":
    run_tests()
