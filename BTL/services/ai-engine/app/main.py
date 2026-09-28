"""
HUNRE E-COMMERCE - AI INTELLIGENCE MICROSERVICE
Port: 8005
FastAPI + Uvicorn + NetworkX + OpenCV/PIL
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.services.graph_solver import BarterGraphSolver
from app.services.cv_service import CVInspectionService
from app.services.anti_fraud import AntiFraudImageDetector
from app.services.price_agent import PriceNegotiatorAgent

app = FastAPI(
    title="HUNRE E-Commerce AI Engine",
    description="Microservice AI thẩm định ảnh đồ cũ, phát hiện chu trình đồ thị Barter Graph & đàm phán giá động",
    version="2.0.0"
)

# Kích hoạt CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# PYDANTIC SCHEMAS
# -------------------------------------------------------------
class BarterItemDTO(BaseModel):
    id: int
    seller_id: int
    seller_name: Optional[str] = None
    title: str
    category_name: Optional[str] = None
    current_price: float
    desired_category_or_title: str
    accept_any_match: Optional[bool] = False

class BarterRequestDTO(BaseModel):
    items: List[BarterItemDTO]
    max_cycle_length: Optional[int] = Field(default=3, ge=2, le=5)

class TimeDecayRequestDTO(BaseModel):
    original_price: float
    floor_price: float
    hours_elapsed: float
    decay_half_life_hours: Optional[float] = 72.0

class NegotiationRequestDTO(BaseModel):
    item_current_price: float
    item_floor_price: float
    buyer_offer_price: float
    buyer_trust_score: int

# -------------------------------------------------------------
# API ROUTES
# -------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "HUNRE E-Commerce AI Microservice",
        "version": "2.0.0",
        "status": "HEALTHY",
        "endpoints": [
            "/api/v1/ai/cv/inspect",
            "/api/v1/ai/barter/solve-cycles",
            "/api/v1/ai/pricing/decay",
            "/api/v1/ai/pricing/negotiate",
            "/api/v1/ai/anti-fraud/check"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "UP", "engine": "FastAPI + PyTorch/NetworkX"}

# 1. THẨM ĐỊNH TÌNH TRẠNG ĐỒ CŨ QUA ẢNH (COMPUTER VISION)
@app.post("/api/v1/ai/cv/inspect")
async def inspect_product_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Tệp tải lên phải là định dạng hình ảnh (JPEG, PNG, WEBP).")
    
    contents = await file.read()
    inspection_result = CVInspectionService.inspect_image_bytes(contents)
    anti_fraud_result = AntiFraudImageDetector.verify_authenticity(contents)

    return {
        "filename": file.filename,
        "inspection": inspection_result,
        "anti_fraud": anti_fraud_result
    }

# 2. TÌM CHU TRÌNH TRAO ĐỔI ĐỒ (AI BARTER GRAPH SOLVER)
@app.post("/api/v1/ai/barter/solve-cycles")
def solve_barter_cycles(payload: BarterRequestDTO):
    raw_items = [item.model_dump() for item in payload.items]
    cycles = BarterGraphSolver.detect_and_balance_cycles(raw_items, payload.max_cycle_length)
    return {
        "total_items_analyzed": len(raw_items),
        "cycles_found_count": len(cycles),
        "cycles": cycles
    }

# 3. HẠ GIÁ THEO THỜI GIAN (DUTCH AUCTION / TIME-DECAY PRICING)
@app.post("/api/v1/ai/pricing/decay")
def calculate_time_decay(payload: TimeDecayRequestDTO):
    return PriceNegotiatorAgent.calculate_decay_price(
        original_price=payload.original_price,
        floor_price=payload.floor_price,
        hours_elapsed=payload.hours_elapsed,
        decay_half_life_hours=payload.decay_half_life_hours
    )

# 4. TRỢ LÝ ĐÀM PHÁN GIÁ THÔNG MINH
@app.post("/api/v1/ai/pricing/negotiate")
def negotiate_price(payload: NegotiationRequestDTO):
    return PriceNegotiatorAgent.negotiate_offer(
        item_current_price=payload.item_current_price,
        item_floor_price=payload.item_floor_price,
        buyer_offer_price=payload.buyer_offer_price,
        buyer_trust_score=payload.buyer_trust_score
    )

# 5. PHÁT HIỆN ẢNH MẠNG / TRÙNG LẶP (ANTI-FRAUD)
@app.post("/api/v1/ai/anti-fraud/check")
async def check_image_fraud(file: UploadFile = File(...)):
    contents = await file.read()
    return AntiFraudImageDetector.verify_authenticity(contents)
