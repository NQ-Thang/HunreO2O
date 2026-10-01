"""
HUNRE E-COMMERCE - LOCAL UNIFIED API GATEWAY & MICROSERVICES RUNNER
Cổng: 8000
Hỗ trợ chạy trực tiếp toàn bộ các API Microservices (Auth, Products CRUD, Escrow Saga, Hub Logistics, AI Proxy)
kèm phục vụ tĩnh toàn bộ Frontend (Student Portal & Hub Staff Scanner).
Lưu trữ dữ liệu bền vững (JSON File Persistence) tại data/hunre_db.json.
"""

from fastapi import FastAPI, HTTPException, Request, Response, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import time
import hmac
import hashlib
import requests
from datetime import datetime

app = FastAPI(
    title="HUNRE E-Commerce Unified Gateway & Services",
    description="Cổng API Gateway tập trung & Đầy đủ 5 Microservices cho sinh viên HUNRE",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đường dẫn file CSDL JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "hunre_db.json")

# Dữ liệu khởi tạo chuẩn
DEFAULT_DB = {
    "users": [
        {"id": 1, "student_code": "20211001", "full_name": "Nguyễn Văn An", "email": "an.nv@hunre.edu.vn", "trust_score": 520, "campus": "CS1_HA_NOI", "wallet_balance": 500000.0, "role": "STUDENT", "faculty": "Công nghệ Thông tin"},
        {"id": 2, "student_code": "20211002", "full_name": "Trần Thị Bích", "email": "bich.tt@hunre.edu.vn", "trust_score": 480, "campus": "CS1_HA_NOI", "wallet_balance": 250000.0, "role": "STUDENT", "faculty": "Môi trường"},
        {"id": 3, "student_code": "20211003", "full_name": "Lê Hoàng Cường", "email": "cuong.lh@hunre.edu.vn", "trust_score": 390, "campus": "CS1_HA_NOI", "wallet_balance": 120000.0, "role": "STUDENT", "faculty": "Khí tượng Thủy văn"},
        {"id": 4, "student_code": "HUB001", "full_name": "Cộng Tác Viên Trạm Hub", "email": "hub.cs1@hunre.edu.vn", "trust_score": 999, "campus": "CS1_HA_NOI", "wallet_balance": 0.0, "role": "HUB_STAFF", "faculty": "Đoàn Thanh Niên"}
    ],
    "products": [
        {
            "id": 1,
            "seller_id": 1,
            "seller_name": "Nguyễn Văn An",
            "category_id": "BOOKS",
            "category_name": "Giáo Trình & Tài Liệu",
            "title": "Giáo trình Cơ Sở Dữ Liệu & SQL (HUNRE)",
            "description": "Giáo trình dùng cho sinh viên K11, K12 CNTT. Trang sạch, không quăn mép, có ghi chú bài tập.",
            "original_price": 80000.0,
            "current_price": 75000.0,
            "floor_price": 60000.0,
            "condition_grade": "GRADE_A",
            "ai_defect_score": 0.035,
            "ai_inspection_summary": "Độ mới 94%, không rách, mép trang sạch, chữ ký dHash xác thực",
            "is_barter_eligible": 1,
            "desired_exchange_items": "Máy tính Casio FX 580VN",
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop",
            "status": "ACTIVE",
            "created_at": "2026-09-15 08:30:00"
        },
        {
            "id": 2,
            "seller_id": 2,
            "seller_name": "Trần Thị Bích",
            "category_id": "TECH",
            "category_name": "Dụng Cụ Học Tập",
            "title": "Máy tính Casio FX 580VN X (Like New)",
            "description": "Máy tính chính hãng thi tốt nghiệp và đại học, nguyên tem Bộ GD&ĐT, màn hình LCD sắc nét.",
            "original_price": 350000.0,
            "current_price": 320000.0,
            "floor_price": 280000.0,
            "condition_grade": "GRADE_S",
            "ai_defect_score": 0.012,
            "ai_inspection_summary": "Độ mới 98%, màn hình LCD nét không xước, phím nảy nhạy",
            "is_barter_eligible": 1,
            "desired_exchange_items": "Bàn phím cơ DareU hoặc Balo",
            "image_url": "https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=600&auto=format&fit=crop",
            "status": "ACTIVE",
            "created_at": "2026-09-15 09:15:00"
        },
        {
            "id": 3,
            "seller_id": 3,
            "seller_name": "Lê Hoàng Cường",
            "category_id": "TECH",
            "category_name": "Thiết Bị Điện Tử",
            "title": "Bàn phím cơ DareU EK87 Blue Switch",
            "description": "Bàn phím cơ dây cắm Type-C, switch nhận 100%, gõ nảy tốt, led trắng đơn sắc.",
            "original_price": 280000.0,
            "current_price": 250000.0,
            "floor_price": 200000.0,
            "condition_grade": "GRADE_B",
            "ai_defect_score": 0.098,
            "ai_inspection_summary": "Độ mới 88%, hơi xước góc trái vỏ, các switch hoạt động 100%",
            "is_barter_eligible": 1,
            "desired_exchange_items": "Giáo trình CSDL hoặc Sách Tiếng Anh",
            "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop",
            "status": "ACTIVE",
            "created_at": "2026-09-15 10:00:00"
        }
    ],
    "lockers": [
        {"id": 1, "hub_id": 1, "locker_code": "LOCKER-S-01", "size_type": "SMALL", "description": "Cỡ Nhỏ (Giáo trình & Sách)", "status": "EMPTY", "current_order": None},
        {"id": 2, "hub_id": 1, "locker_code": "LOCKER-M-01", "size_type": "MEDIUM", "description": "Cỡ Vừa (Bàn phím DareU)", "status": "OCCUPIED", "current_order": "ORD-HUNRE-98471"},
        {"id": 3, "hub_id": 1, "locker_code": "LOCKER-M-02", "size_type": "MEDIUM", "description": "Cỡ Vừa (Laptop / Casio)", "status": "EMPTY", "current_order": None},
        {"id": 4, "hub_id": 1, "locker_code": "LOCKER-L-01", "size_type": "LARGE", "description": "Cỡ Lớn (Màn hình / Case)", "status": "EMPTY", "current_order": None}
    ],
    "escrow_orders": {
        "ORD-HUNRE-98471": {
            "order_code": "ORD-HUNRE-98471",
            "buyer_id": 1,
            "buyer_name": "Nguyễn Văn An",
            "seller_id": 3,
            "seller_name": "Lê Hoàng Cường",
            "product_id": 3,
            "product_title": "Bàn phím cơ DareU EK87 Blue Switch",
            "hub_id": 1,
            "hub_name": "Trạm Hub CS1 (Nhà A - Văn Phòng Đoàn Trường)",
            "locker_code": "LOCKER-M-01",
            "escrow_amount": 250000.0,
            "saga_step": 4,
            "status": "STORED_AT_HUB",
            "deadline": "17:30 ngày 18/09/2026",
            "created_at": "2026-09-16 11:00:00"
        }
    }
}

def load_db():
    if not os.path.exists(DB_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DB, f, ensure_ascii=False, indent=2)
        return DEFAULT_DB
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_DB

def save_db(db):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# =============================================================
# 1. AUTH SERVICE APIS (/api/v1/auth)
# =============================================================

@app.get("/api/v1/auth/users")
def get_all_users():
    db = load_db()
    return {"success": True, "users": db["users"]}

@app.get("/api/v1/auth/users/trust-score")
def get_trust_score_query(user_id: int = Query(1)):
    return calculate_trust_score(user_id)

@app.get("/api/v1/auth/trust-score/{user_id}")
def get_trust_score_path(user_id: int):
    return calculate_trust_score(user_id)

def calculate_trust_score(user_id: int):
    db = load_db()
    user = next((u for u in db["users"] if u["id"] == user_id), None)
    if not user:
        # Fallback user mặc định
        user = db["users"][0]
    score = user["trust_score"]
    if score >= 800:
        tier = "KIM CƯƠNG (Miễn cọc 100% & Ưu tiên Barter)"
    elif score >= 600:
        tier = "VÀNG (Ưu tiên Barter & Giảm 50% cọc)"
    elif score >= 400:
        tier = "BẠC (Sinh viên uy tín tiêu chuẩn)"
    else:
        tier = "ĐỒNG (Cần tích lũy thêm giao dịch)"
    return {
        "success": True,
        "data": {
            "user_id": user["id"],
            "full_name": user["full_name"],
            "student_code": user["student_code"],
            "trust_score": score,
            "tier": tier,
            "wallet_balance": user.get("wallet_balance", 0.0),
            "campus": user.get("campus", "CS1_HA_NOI")
        }
    }

class RegisterDTO(BaseModel):
    student_code: str
    full_name: str
    email: str
    password: Optional[str] = "123456"
    faculty: Optional[str] = "Công nghệ Thông tin"
    campus: Optional[str] = "CS1_HA_NOI"

@app.post("/api/v1/auth/register")
def register(dto: RegisterDTO):
    if not dto.student_code.strip() or not dto.full_name.strip():
        raise HTTPException(status_code=422, detail="Mã sinh viên và họ tên không được để trống!")
    if not dto.email.lower().endswith("@hunre.edu.vn"):
        raise HTTPException(status_code=422, detail="KYC Failed: Bắt buộc sử dụng email sinh viên trường (@hunre.edu.vn)!")

    db = load_db()
    # Kiểm tra trùng email
    if any(u["email"].lower() == dto.email.lower() for u in db["users"]):
        raise HTTPException(status_code=409, detail="Email sinh viên này đã được đăng ký trong hệ thống!")

    new_user = {
        "id": len(db["users"]) + 1,
        "student_code": dto.student_code.strip(),
        "full_name": dto.full_name.strip(),
        "email": dto.email.lower().strip(),
        "trust_score": 500,
        "campus": dto.campus,
        "wallet_balance": 200000.0,
        "role": "STUDENT",
        "faculty": dto.faculty
    }
    db["users"].append(new_user)
    save_db(db)
    return {"success": True, "message": "Đăng ký thành công!", "user": new_user}

# =============================================================
# 2. PRODUCT SERVICE APIS (/api/v1/products - FULL CRUD)
# =============================================================

@app.get("/api/v1/products")
def get_products(category: Optional[str] = None, keyword: Optional[str] = None):
    db = load_db()
    items = db["products"]
    if category and category != "ALL":
        items = [p for p in items if p.get("category_id") == category or p.get("category_name") == category]
    if keyword:
        kw = keyword.lower()
        items = [p for p in items if kw in p.get("title", "").lower() or kw in p.get("description", "").lower() or kw in p.get("desired_exchange_items", "").lower()]
    return {"success": True, "count": len(items), "data": items}

@app.get("/api/v1/products/{product_id}")
def get_product_detail(product_id: int):
    db = load_db()
    product = next((p for p in db["products"] if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    return {"success": True, "data": product}

class ProductCreateDTO(BaseModel):
    title: str
    description: Optional[str] = ""
    category_id: Optional[str] = "BOOKS"
    category_name: Optional[str] = "Giáo Trình & Tài Liệu"
    original_price: float
    current_price: float
    floor_price: Optional[float] = None
    condition_grade: Optional[str] = "GRADE_A"
    ai_defect_score: Optional[float] = 0.05
    ai_inspection_summary: Optional[str] = "Đã được AI thẩm định"
    is_barter_eligible: Optional[int] = 1
    desired_exchange_items: Optional[str] = "Trao đổi linh hoạt"
    image_url: Optional[str] = None
    seller_id: Optional[int] = 1

@app.post("/api/v1/products")
def create_product(dto: ProductCreateDTO):
    if not dto.title or not dto.title.strip():
        raise HTTPException(status_code=400, detail="Tiêu đề sản phẩm không được để trống!")
    if dto.current_price <= 0:
        raise HTTPException(status_code=400, detail="Giá bán sản phẩm phải lớn hơn 0 VNĐ!")
    if dto.floor_price is not None and dto.floor_price > dto.current_price:
        raise HTTPException(status_code=400, detail="Giá sàn không được lớn hơn giá bán hiện tại!")

    db = load_db()
    seller = next((u for u in db["users"] if u["id"] == dto.seller_id), db["users"][0])
    floor_price = dto.floor_price if dto.floor_price is not None else (dto.current_price * 0.8)
    
    # Map category name
    cat_names = {
        "BOOKS": "Giáo Trình & Tài Liệu",
        "TECH": "Thiết Bị Điện Tử",
        "STATIONERY": "Dụng Cụ Học Tập",
        "OTHER": "Đồ Dùng Khác"
    }
    category_name = dto.category_name or cat_names.get(dto.category_id, "Đồ Dùng Học Tập")

    new_id = max([p["id"] for p in db["products"]] + [0]) + 1
    new_product = {
        "id": new_id,
        "seller_id": seller["id"],
        "seller_name": seller["full_name"],
        "category_id": dto.category_id,
        "category_name": category_name,
        "title": dto.title.strip(),
        "description": dto.description or "Sản phẩm chính chủ sinh viên HUNRE.",
        "original_price": dto.original_price or dto.current_price,
        "current_price": dto.current_price,
        "floor_price": floor_price,
        "condition_grade": dto.condition_grade or "GRADE_A",
        "ai_defect_score": dto.ai_defect_score or 0.05,
        "ai_inspection_summary": dto.ai_inspection_summary or "Đã xác thực ảnh thực tế",
        "is_barter_eligible": dto.is_barter_eligible if dto.is_barter_eligible is not None else 1,
        "desired_exchange_items": dto.desired_exchange_items or "Không có",
        "image_url": dto.image_url or "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop",
        "status": "ACTIVE",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db["products"].insert(0, new_product)
    save_db(db)
    return {"success": True, "message": "Đăng bán sản phẩm lên Chợ Sinh Viên thành công!", "data": new_product}

class ProductUpdateDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    current_price: Optional[float] = None
    floor_price: Optional[float] = None
    desired_exchange_items: Optional[str] = None
    status: Optional[str] = None

@app.put("/api/v1/products/{product_id}")
def update_product(product_id: int, dto: ProductUpdateDTO):
    db = load_db()
    product = next((p for p in db["products"] if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")

    if dto.title is not None:
        if not dto.title.strip():
            raise HTTPException(status_code=400, detail="Tiêu đề cập nhật không được để trống!")
        product["title"] = dto.title.strip()

    if dto.current_price is not None:
        if dto.current_price <= 0:
            raise HTTPException(status_code=400, detail="Giá bán cập nhật phải lớn hơn 0 VNĐ!")
        product["current_price"] = dto.current_price

    target_current = dto.current_price if dto.current_price is not None else product["current_price"]
    if dto.floor_price is not None:
        if dto.floor_price > target_current:
            raise HTTPException(status_code=400, detail="Giá sàn không được lớn hơn giá bán!")
        product["floor_price"] = dto.floor_price
    if dto.description is not None: product["description"] = dto.description
    if dto.category_id is not None: product["category_id"] = dto.category_id
    if dto.current_price is not None: product["current_price"] = dto.current_price
    if dto.floor_price is not None: product["floor_price"] = dto.floor_price
    if dto.desired_exchange_items is not None: product["desired_exchange_items"] = dto.desired_exchange_items
    if dto.status is not None: product["status"] = dto.status
    product["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_db(db)
    return {"success": True, "message": "Cập nhật sản phẩm thành công!", "data": product}

@app.delete("/api/v1/products/{product_id}")
def delete_product(product_id: int):
    db = load_db()
    initial_len = len(db["products"])
    db["products"] = [p for p in db["products"] if p["id"] != product_id]
    if len(db["products"]) == initial_len:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    save_db(db)
    return {"success": True, "message": f"Đã gỡ sản phẩm #{product_id} khỏi sàn giao dịch."}

# =============================================================
# 3. ESCROW SERVICE APIS (/api/v1/escrow)
# =============================================================

@app.get("/api/v1/escrow/orders")
def get_all_escrow_orders():
    db = load_db()
    return {"success": True, "orders": list(db["escrow_orders"].values())}

@app.get("/api/v1/escrow/orders/{order_code}")
def get_escrow_order(order_code: str):
    db = load_db()
    order = db["escrow_orders"].get(order_code)
    if not order:
        # Fallback thử lấy đơn đầu tiên nếu demo
        if db["escrow_orders"]:
            order = list(db["escrow_orders"].values())[0]
        else:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng ký quỹ.")
    return {"success": True, "order": order}

class CreateOrderDTO(BaseModel):
    product_id: int
    buyer_id: Optional[int] = 1
    agreed_price: Optional[float] = None

@app.post("/api/v1/escrow/orders")
def create_escrow_order(dto: CreateOrderDTO):
    db = load_db()
    product = next((p for p in db["products"] if p["id"] == dto.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm để tạo đơn.")
    
    buyer = next((u for u in db["users"] if u["id"] == dto.buyer_id), db["users"][0])
    seller = next((u for u in db["users"] if u["id"] == product["seller_id"]), db["users"][2])
    
    order_code = f"ORD-HUNRE-{int(time.time()) % 100000:05d}"
    amount = dto.agreed_price if dto.agreed_price is not None else product["current_price"]

    new_order = {
        "order_code": order_code,
        "buyer_id": buyer["id"],
        "buyer_name": buyer["full_name"],
        "seller_id": seller["id"],
        "seller_name": seller["full_name"],
        "product_id": product["id"],
        "product_title": product["title"],
        "hub_id": 1,
        "hub_name": "Trạm Hub CS1 (Nhà A - Văn Phòng Đoàn Trường)",
        "locker_code": "LOCKER-M-02",
        "escrow_amount": amount,
        "saga_step": 2, # Đã đặt hàng và khóa cọc
        "status": "DEPOSITED",
        "deadline": "17:30 ngày mai",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db["escrow_orders"][order_code] = new_order
    save_db(db)
    return {"success": True, "message": "Tạo đơn hàng và khóa tiền ký quỹ thành công!", "order": new_order}

class SagaAdvanceDTO(BaseModel):
    order_code: str
    action: str  # CHECKIN, CHECKOUT, SATISFIED, DISPUTE

@app.post("/api/v1/escrow/saga/advance")
def advance_saga(dto: SagaAdvanceDTO):
    if dto.action not in ["CHECKIN", "CHECKOUT", "SATISFIED", "DISPUTE"]:
        raise HTTPException(status_code=400, detail=f"Hành động Saga '{dto.action}' không hợp lệ! Chỉ chấp nhận: CHECKIN, CHECKOUT, SATISFIED, DISPUTE.")

    db = load_db()
    order = db["escrow_orders"].get(dto.order_code)
    if not order:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng ký quỹ '{dto.order_code}'.")

    if dto.action == "CHECKIN":
        order["saga_step"] = 4
        order["status"] = "STORED_AT_HUB"
        msg = "Người bán đã gửi đồ vào Trạm Hub. Đồ đã lưu an toàn trong tủ Locker."
    elif dto.action == "CHECKOUT":
        order["saga_step"] = 5
        order["status"] = "BUYER_CHECKOUT"
        msg = "Người mua đã mở tủ nhận đồ và đang kiểm tra tại bàn Trạm Hub."
    elif dto.action == "SATISFIED":
        order["saga_step"] = 7
        order["status"] = "RELEASED"
        # Cộng điểm uy tín +5 cho cả 2 bên
        for u in db["users"]:
            if u["id"] in [order["buyer_id"], order["seller_id"]]:
                u["trust_score"] = min(1000, u["trust_score"] + 5)
        msg = f"Người mua xác nhận hài lòng! Đã giải ngân {int(order['escrow_amount']):,}đ cho người bán {order['seller_name']}. Cả 2 được cộng +5 Điểm Uy Tín!"
    elif dto.action == "DISPUTE":
        order["saga_step"] = 7
        order["status"] = "DISPUTED"
        msg = "Đã tiếp nhận khiếu nại! Tiền ký quỹ bị đóng băng để Trạm Hub hoàn cọc 100%."

    save_db(db)
    return {"success": True, "message": msg, "order": order}

@app.post("/api/v1/escrow/orders/{order_code}/release")
def release_escrow(order_code: str):
    return advance_saga(SagaAdvanceDTO(order_code=order_code, action="SATISFIED"))

@app.post("/api/v1/escrow/orders/{order_code}/dispute")
def dispute_escrow(order_code: str):
    return advance_saga(SagaAdvanceDTO(order_code=order_code, action="DISPUTE"))

# =============================================================
# 4. HUB SERVICE APIS (/api/v1/hub)
# =============================================================

@app.get("/api/v1/hub/lockers")
def get_lockers():
    db = load_db()
    return {"success": True, "lockers": db["lockers"]}

class HubScanDTO(BaseModel):
    order_code: str
    scan_type: str # CHECKIN hoặc CHECKOUT

@app.post("/api/v1/hub/checkin")
def hub_checkin(dto: HubScanDTO):
    db = load_db()
    # Tìm locker trống
    empty_locker = next((l for l in db["lockers"] if l["status"] == "EMPTY"), None)
    if not empty_locker:
        raise HTTPException(status_code=409, detail="Toàn bộ ô tủ Locker tại Trạm Hub CS1 đang bận! Vui lòng chờ giải phóng ô tủ.")
    
    empty_locker["status"] = "OCCUPIED"
    empty_locker["current_order"] = dto.order_code

    if dto.order_code in db["escrow_orders"]:
        db["escrow_orders"][dto.order_code]["status"] = "STORED_AT_HUB"
        db["escrow_orders"][dto.order_code]["saga_step"] = 4
        db["escrow_orders"][dto.order_code]["locker_code"] = empty_locker["locker_code"]

    save_db(db)
    return {
        "success": True,
        "message": f"Quét nhận hàng thành công! Đã cấp phát ô tủ {empty_locker['locker_code']} ({empty_locker['description']}).",
        "locker": empty_locker
    }

@app.post("/api/v1/hub/checkout")
def hub_checkout(dto: HubScanDTO):
    db = load_db()
    # Tìm locker của order này
    locker = next((l for l in db["lockers"] if l.get("current_order") == dto.order_code), None)
    if not locker:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy ô tủ Locker đang chứa đơn hàng '{dto.order_code}'!")
    
    locker["status"] = "EMPTY"
    locker["current_order"] = None

    if dto.order_code in db["escrow_orders"]:
        db["escrow_orders"][dto.order_code]["status"] = "BUYER_CHECKOUT"
        db["escrow_orders"][dto.order_code]["saga_step"] = 5

    save_db(db)
    return {
        "success": True,
        "message": f"Xác thực mã QR thành công! Đã mở khóa ô tủ {locker['locker_code']}. Người mua đang nhận hàng kiểm tra.",
        "locker": locker
    }

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
            "qr_payload": f"HUNRE:{order_code}:{user_id}:{role}:{token}",
            "qr_image_url": f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=HUNRE:{order_code}:{user_id}:{role}:{token}"
        }
    }

# =============================================================
# 5. REVERSE PROXY ĐẾN AI SERVICE (Port 8005) & FALLBACK
# =============================================================

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
        # Fallback thông minh nếu AI Service đang khởi động
        if "negotiate" in path:
            try:
                data = json.loads(body)
                offer = data.get("buyer_offer_price", 0)
                floor = data.get("item_floor_price", 0)
                curr = data.get("item_current_price", 0)
                if offer >= curr:
                    return {"decision": "ACCEPT", "message": "Giá đề xuất bằng hoặc cao hơn giá niêm yết. Chấp nhận ngay!"}
                elif offer >= floor:
                    return {"decision": "ACCEPT", "message": f"Mức giá {int(offer):,}đ hợp lý, trên giá sàn. Trợ lý AI đồng ý phê duyệt!"}
                else:
                    return {"decision": "COUNTER_OFFER", "counter_offer_price": floor + 5000, "message": f"Mức giá bạn đưa ra dưới giá sàn. Đề xuất giá tốt nhất: {int(floor + 5000):,}đ."}
            except Exception:
                pass
        return {
            "success": False,
            "message": f"Không thể kết nối đến AI Service (cổng 8005): {str(e)}",
            "hint": "Khởi động AI Engine bằng lệnh: python -m uvicorn app.main:app --port 8005 tại BTL/services/ai-engine"
        }

# =============================================================
# 6. PHỤC VỤ STATIC FILES CHO FRONTEND
# =============================================================

FRONTEND_STUDENT_DIR = os.path.join(BASE_DIR, "..", "frontend", "student-portal")
FRONTEND_STAFF_DIR = os.path.join(BASE_DIR, "..", "frontend", "hub-staff-portal")

if os.path.exists(FRONTEND_STAFF_DIR):
    @app.get("/staff")
    def redirect_staff():
        return RedirectResponse(url="/staff/")
    app.mount("/staff", StaticFiles(directory=FRONTEND_STAFF_DIR, html=True), name="hub-staff")

if os.path.exists(FRONTEND_STUDENT_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_STUDENT_DIR, html=True), name="student-portal")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("local_api_server:app", host="0.0.0.0", port=8000, reload=True)
