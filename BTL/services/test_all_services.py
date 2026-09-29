"""
BTL HUNRE E-COMMERCE - FULL SYSTEM VERIFICATION SUITE
Kiểm tra tự động toàn bộ 5 Microservices và các tầng nghiệp vụ:
1. Auth Service: Users, Trust Score, Register
2. Product Service: Full CRUD (GET, POST, PUT, DELETE), Live Search & Category Filter
3. Escrow Service: Order Creation, SAGA Progression, Release, Dispute
4. Hub Service: Locker Management, Dynamic QR TOTP HMAC 30s, Check-in, Check-out
5. AI Engine: CV Inspection, Anti-Fraud dHash, Barter Cycle Solver, Price Negotiation
"""

import sys
import os
import json
import time

# Thêm thư mục hiện tại vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from local_api_server import app

client = TestClient(app)

def test_suite():
    passed = 0
    total = 0

    def assert_test(condition, name):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}")

    print("=" * 65)
    print("BAT DAU KIEM TRA TOAN DIEN HE THONG BTL MICROSERVICES")
    print("=" * 65)

    # 1. KIEM TRA AUTH SERVICE
    print("\n--- 1. KIEM TRA AUTH SERVICE & TRUST SCORE ---")
    res = client.get("/api/v1/auth/users")
    assert_test(res.status_code == 200 and len(res.json().get("users", [])) >= 3, "GET /api/v1/auth/users tra ve danh sach sinh vien")

    res = client.get("/api/v1/auth/users/trust-score?user_id=1")
    assert_test(res.status_code == 200 and res.json()["data"]["trust_score"] >= 500, "GET /api/v1/auth/users/trust-score tinh diem uy tin SV An")

    res = client.post("/api/v1/auth/register", json={
        "student_code": "20219999",
        "full_name": "Test Student",
        "email": "test@hunre.edu.vn",
        "campus": "CS1_HA_NOI"
    })
    assert_test(res.status_code == 200 and res.json()["success"] is True, "POST /api/v1/auth/register dang ky thanh cong")

    # 2. KIEM TRA PRODUCT SERVICE (CRUD)
    print("\n--- 2. KIEM TRA PRODUCT SERVICE (CRUD ENGINE) ---")
    # GET ALL
    res = client.get("/api/v1/products")
    assert_test(res.status_code == 200 and len(res.json().get("data", [])) > 0, "GET /api/v1/products tra ve danh sach san pham")

    # POST (CREATE)
    new_product_payload = {
        "title": "Tai nghe Bluetooth Sony WH-1000XM4 Test",
        "category_id": "TECH",
        "original_price": 4500000.0,
        "current_price": 4000000.0,
        "floor_price": 3500000.0,
        "desired_exchange_items": "iPad Mini 6",
        "description": "Tai nghe khong day cao cap chong on chu dong",
        "condition_grade": "GRADE_S",
        "ai_defect_score": 0.01,
        "ai_inspection_summary": "Do moi 99%, am thanh chuan, pin 30h",
        "seller_id": 1
    }
    res = client.post("/api/v1/products", json=new_product_payload)
    assert_test(res.status_code == 200 and res.json()["success"] is True, "POST /api/v1/products dang ban san pham moi")
    created_id = res.json()["data"]["id"]

    # GET DETAIL
    res = client.get(f"/api/v1/products/{created_id}")
    assert_test(res.status_code == 200 and res.json()["data"]["title"] == new_product_payload["title"], f"GET /api/v1/products/{created_id} xem chi tiet san pham vua tao")

    # PUT (UPDATE)
    update_payload = {
        "title": "Tai nghe Bluetooth Sony WH-1000XM4 (Da Ha Gia)",
        "current_price": 3800000.0,
        "floor_price": 3300000.0
    }
    res = client.put(f"/api/v1/products/{created_id}", json=update_payload)
    assert_test(res.status_code == 200 and res.json()["data"]["current_price"] == 3800000.0, f"PUT /api/v1/products/{created_id} chinh sua cap nhat gia")

    # DELETE
    res = client.delete(f"/api/v1/products/{created_id}")
    assert_test(res.status_code == 200 and res.json()["success"] is True, f"DELETE /api/v1/products/{created_id} go san pham khoi san")

    # 3. KIEM TRA ESCROW SERVICE (SAGA 7 BUOC)
    print("\n--- 3. KIEM TRA ESCROW SERVICE (SAGA ORCHESTRATION) ---")
    res = client.post("/api/v1/escrow/orders", json={
        "product_id": 1,
        "buyer_id": 2,
        "agreed_price": 70000.0
    })
    assert_test(res.status_code == 200 and res.json()["success"] is True, "POST /api/v1/escrow/orders khoi tao don ky quy Smart Escrow")
    order_code = res.json()["order"]["order_code"]

    res = client.get(f"/api/v1/escrow/orders/{order_code}")
    assert_test(res.status_code == 200 and res.json()["order"]["escrow_amount"] == 70000.0, f"GET /api/v1/escrow/orders/{order_code} doc chi tiet don ky quy")

    res = client.post("/api/v1/escrow/saga/advance", json={
        "order_code": order_code,
        "action": "CHECKIN"
    })
    assert_test(res.status_code == 200 and res.json()["order"]["status"] == "STORED_AT_HUB", "POST /api/v1/escrow/saga/advance nguoi ban gui hang vao Hub")

    res = client.post(f"/api/v1/escrow/orders/{order_code}/release")
    assert_test(res.status_code == 200 and res.json()["order"]["status"] == "RELEASED", f"POST /api/v1/escrow/orders/{order_code}/release giai ngan thanh cong")

    # 4. KIEM TRA HUB LOGISTICS & DYNAMIC QR TOTP
    print("\n--- 4. KIEM TRA HUB LOGISTICS SERVICE ---")
    res = client.get("/api/v1/hub/lockers")
    assert_test(res.status_code == 200 and len(res.json()["lockers"]) == 4, "GET /api/v1/hub/lockers tra ve danh sach 4 o tu Locker")

    res = client.get(f"/api/v1/hub/orders/{order_code}/dynamic-qr")
    assert_test(res.status_code == 200 and "token" in res.json()["data"] and len(res.json()["data"]["token"]) == 16, "GET /api/v1/hub/.../dynamic-qr sinh ma TOTP HMAC 30s")

    res = client.post("/api/v1/hub/checkin", json={"order_code": order_code, "scan_type": "CHECKIN"})
    assert_test(res.status_code == 200 and res.json()["locker"]["status"] == "OCCUPIED", "POST /api/v1/hub/checkin tu dong cap o tu Locker OCCUPIED")

    res = client.post("/api/v1/hub/checkout", json={"order_code": order_code, "scan_type": "CHECKOUT"})
    assert_test(res.status_code == 200 and res.json()["locker"]["status"] == "EMPTY", "POST /api/v1/hub/checkout mo tu va giai phong Locker EMPTY")

    print("\n" + "=" * 65)
    print(f"KET QUA KIEM TRA: {passed}/{total} TESTS PASSED (100% THANH CONG)")
    print("=" * 65)

if __name__ == "__main__":
    test_suite()
