"""
HUNRE E-COMMERCE - LOCAL UNIFIED API GATEWAY & MICROSERVICES RUNNER
Cổng: 8000
Hỗ trợ chạy trực tiếp toàn bộ các API Microservices (Auth, Products, Escrow, Hub, AI Proxy)
giúp sinh viên có thể demo trơn tru 100% ngay trên máy cục bộ mà không phụ thuộc Docker.
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import hmac
import hashlib
import requests

app = FastAPI(
    title="HUNRE E-Commerce Unified Gateway & Services",
    description="Cổng API Gateway tập trung & giả lập phân tán các Microservices cho sinh viên HUNRE",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# IN-MEMORY MOCK DATABASE (Khởi tạo sẵn dữ liệu sinh viên HUNRE)
# -------------------------------------------------------------
DB_USERS = [
    {"id": 1, "student_code": "20211001", "full_name": "Nguyễn Văn An", "email": "an.nv@hunre.edu.vn", "trust_score": 520, "campus": "CS1_HA_NOI", "wallet_balance": 500000.0, "role": "STUDENT"},
    {"id": 2, "student_code": "20211002", "full_name": "Trần Thị Bích", "email": "bich.tt@hunre.edu.vn", "trust_score": 480, "campus": "CS1_HA_NOI", "wallet_balance": 250000.0, "role": "STUDENT"},
    {"id": 3, "student_code": "20211003", "full_name": "Lê Hoàng Cường", "email": "cuong.lh@hunre.edu.vn", "trust_score": 390, "campus": "CS1_HA_NOI", "wallet_balance": 120000.0, "role": "STUDENT"},
    {"id": 4, "student_code": "HUB001", "full_name": "Cộng Tác Viên Trạm Hub", "email": "hub.cs1@hunre.edu.vn", "trust_score": 999, "campus": "CS1_HA_NOI", "wallet_balance": 0.0, "role": "HUB_STAFF"}
]

DB_PRODUCTS = [
    {
        "id": 1, "seller_id": 1, "seller_name": "Nguyễn Văn An", "category_id": 1, "category_name": "Giáo Trình & Tài Liệu",
        "title": "Giáo trình Cơ Sở Dữ Liệu & SQL (HUNRE)", "description": "Sách bảo quản tốt, không quăn mép, có ghi chú bài tập.",
        "original_price": 80000.0, "current_price": 75000.0, "floor_price": 60000.0, "condition_grade": "GRADE_A",
        "ai_inspection_summary": "Độ mới 94%, không rách, mép trang sạch", "is_barter_eligible": 1,
        "desired_exchange_items": "Máy tính Casio FX 580VN", "status": "ACTIVE"
    },
    {
        "id": 2, "seller_id": 2, "seller_name": "Trần Thị Bích", "category_id": 2, "category_name": "Dụng Cụ Học Tập",
        "title": "Máy tính Casio FX 580VN X (Like New)", "description": "Dùng tốt cho môn Toán cao cấp và Khí tượng, nguyên tem bảo hành.",
        "original_price": 350000.0, "current_price": 320000.0, "floor_price": 280000.0, "condition_grade": "GRADE_S",
        "ai_inspection_summary": "Độ mới 98%, màn hình LCD sắc nét, phím nảy nhạy", "is_barter_eligible": 1,
        "desired_exchange_items": "Bàn phím cơ DareU hoặc Balo", "status": "ACTIVE"
    },
    {
        "id": 3, "seller_id": 3, "seller_name": "Lê Hoàng Cường", "category_id": 2, "category_name": "Thiết Bị Điện Tử",
        "title": "Bàn phím cơ DareU EK87 Blue Switch", "description": "Phím gõ nảy tốt, led trắng đơn sắc, dọn trọ cần đổi giáo trình.",
        "original_price": 280000.0, "current_price": 250000.0, "floor_price": 200000.0, "condition_grade": "GRADE_B",
        "ai_inspection_summary": "Độ mới 88%, hơi xước góc trái, các switch hoạt động 100%", "is_barter_eligible": 1,
        "desired_exchange_items": "Giáo trình CSDL hoặc Sách Tiếng Anh", "status": "ACTIVE"
    }
]

DB_LOCKERS = [
    {"id": 1, "hub_id": 1, "locker_code": "LOCKER-S-01", "size_type": "SMALL", "status": "EMPTY"},
    {"id": 2, "hub_id": 1, "locker_code": "LOCKER-M-01", "size_type": "MEDIUM", "status": "OCCUPIED", "current_order": "ORD-HUNRE-98471"},
    {"id": 3, "hub_id": 1, "locker_code": "LOCKER-M-02", "size_type": "MEDIUM", "status": "EMPTY"},
    {"id": 4, "hub_id": 1, "locker_code": "LOCKER-L-01", "size_type": "LARGE", "status": "EMPTY"}
]

DB_ESCROW_ORDERS = {
    "ORD-HUNRE-98471": {
        "order_code": "ORD-HUNRE-98471",
        "buyer_id": 1,
        "buyer_name": "Nguyễn Văn An",
        "seller_id": 3,
        "seller_name": "Lê Hoàng Cường",
        "product_id": 3,
        "product_title": "Bàn phím cơ DareU EK87 Blue Switch",
        "hub_id": 1,
        "hub_name": "Trạm Hub CS1 (Nhà A - Phòng Đoàn Trường)",
        "locker_code": "LOCKER-M-01",
        "escrow_amount": 250000.0,
        "status": "STORED_AT_HUB"
    }
}

# -------------------------------------------------------------
# 1. AUTH SERVICE APIS (Port 8000 /api/v1/auth)
# -------------------------------------------------------------
class RegisterDTO(BaseModel):
    student_code: str
    full_name: str
    email: str
    password: str
    faculty: Optional[str] = "Công nghệ Thông tin"
    campus: Optional[str] = "CS1_HA_NOI"

@app.post("/api/v1/auth/register")
def register(dto: RegisterDTO):
    if not dto.email.endswith("@hunre.edu.vn"):
        raise HTTPException(status_code=422, detail="KYC Failed: Phải dùng email định danh @hunre.edu.vn của sinh viên trường!")
    new_user = {
        "id": len(DB_USERS) + 1,
        "student_code": dto.student_code,
        "full_name": dto.full_name,
        "email": dto.email.lower(),
        "trust_score": 100,
        "campus": dto.campus,
        "wallet_balance": 0.0,
        "role": "STUDENT"
    }
    DB_USERS.append(new_user)
    return {"success": True, "message": "Đăng ký thành công!", "user": new_user}

@app.get("/api/v1/auth/trust-score/{user_id}")
def get_trust_score(user_id: int):
    user = next((u for u in DB_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên.")
    score = user["trust_score"]
    tier = "VÀNG (Ưu tiên ghép Barter Graph & Giảm 50% cọc)" if score >= 600 else ("BẠC (Sinh viên uy tín tiêu chuẩn)" if score >= 400 else "ĐỒNG")
    return {"success": True, "data": {"user_id": user_id, "full_name": user["full_name"], "trust_score": score, "tier": tier}}

# -------------------------------------------------------------
# 2. PRODUCT SERVICE APIS (Port 8000 /api/v1/products)
# -------------------------------------------------------------
@app.get("/api/v1/products")
def get_products():
    return {"success": True, "count": len(DB_PRODUCTS), "data": DB_PRODUCTS}

@app.get("/api/v1/products/{product_id}")
def get_product_detail(product_id: int):
    product = next((p for p in DB_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    return {"success": True, "data": product}

# -------------------------------------------------------------
# 3. ESCROW SERVICE APIS (Port 8000 /api/v1/escrow)
# -------------------------------------------------------------
@app.get("/api/v1/escrow/orders/{order_code}")
def get_escrow_order(order_code: str):
    order = DB_ESCROW_ORDERS.get(order_code)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng ký quỹ.")
    return {"success": True, "order": order}

@app.post("/api/v1/escrow/orders/{order_code}/release")
def release_escrow(order_code: str):
    order = DB_ESCROW_ORDERS.get(order_code)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")
    order["status"] = "RELEASED"
    return {
        "success": True,
        "message": f"Đã giải ngân thành công {int(order['escrow_amount']):,}đ cho người bán {order['seller_name']}!",
        "new_state": "RELEASED"
    }

# -------------------------------------------------------------
# 4. HUB SERVICE APIS (Port 8000 /api/v1/hub)
# -------------------------------------------------------------
@app.get("/api/v1/hub/orders/{order_code}/dynamic-qr")
def generate_dynamic_qr(order_code: str, user_id: int = 1, role: str = "BUYER"):
    time_window = int(time.time() // 30)
    payload = f"{order_code}|{user_id}|{role}|{time_window}"
    token = hmac.new(b"HUNRE_SECRET_2026", payload.encode(), hashlib.sha256).hexdigest()[:16].upper()
    seconds_left = 30 - int(time.time() % 30)
    return {
        "success": True,
        "data": {
            "order_code": order_code,
            "role": role,
            "token": token,
            "expires_in_seconds": seconds_left,
            "qr_payload": f"HUNRE:{order_code}:{user_id}:{role}:{token}"
        }
    }

# -------------------------------------------------------------
# 5. REVERSE PROXY ĐẾN AI SERVICE (Port 8005)
# -------------------------------------------------------------
@app.api_route("/api/v1/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_ai_engine(path: str, request: Request):
    ai_url = f"http://localhost:8005/api/v1/ai/{path}"
    headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}
    body = await request.body()
    try:
        resp = requests.request(
            method=request.method,
            url=ai_url,
            headers=headers,
            data=body,
            timeout=10
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        # Fallback nếu AI engine chưa bật
        return {
            "success": False,
            "message": f"Không thể kết nối đến AI Service (cổng 8005): {str(e)}",
            "hint": "Vui lòng khởi động AI Service bằng lệnh uvicorn app.main:app --port 8005"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
