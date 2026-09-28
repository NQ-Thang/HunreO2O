# HUNRE E-COMMERCE: NỀN TẢNG GIAO DỊCH HÀNG HÓA O2O VÀ AI CHO SINH VIÊN
> **Đề tài Nghiên cứu Khoa học & Khóa luận Tốt nghiệp Công nghệ Thông tin**  
> **Trường Đại học Tài nguyên và Môi trường Hà Nội (HUNRE)**

---

## 🌟 GIỚI THIỆU TỔNG QUAN

**HUNRE E-Commerce** là giải pháp thương mại điện tử đột phá kết hợp mô hình **O2O (Online-to-Offline)** với **Trạm Giao Dịch Trung Gian (Physical Hub)** đặt tại khuôn viên trường, giải quyết triệt để các vấn nạn nhức nhối trong giao dịch sinh viên:
- ❌ **Tránh rủi ro lừa đảo & bom hàng:** Không còn tình trạng chuyển khoản trước rồi bị chặn liên lạc hay hẹn gặp giao dịch nguy hiểm ngoài cổng trường.
- 🛡️ **Ký quỹ Thông minh (Smart Escrow):** Tiền cọc hoặc tiền mua hàng được bảo vệ trong ví ký quỹ trung gian, chỉ giải ngân cho người bán khi người mua đã đến Trạm Hub kiểm tra và xác nhận hài lòng.
- 🤖 **Thẩm định đồ cũ bằng AI (Computer Vision):** Tự động phát hiện trầy xước, ố vàng, hỏng hóc từ ảnh chụp thực tế và dán nhãn Condition Grade (99%, 95%, 85%,...).
- 🔄 **Vòng tròn trao đổi đồ (AI Barter Graph):** Ứng dụng lý thuyết đồ thị phát hiện chu trình 2 chiều, 3 chiều hoặc N-chiều kèm thuật toán ma trận bù trừ tiền mặt, giúp sinh viên đổi đồ mà không cần có sẵn nhiều tiền.
- 📉 **Đấu giá ngược & Trợ lý đàm phán giá:** Tự động hạ giá theo hàm số thời gian (Time-decay pricing) cho các sản phẩm cần thanh lý gấp cuối kỳ.

---

## 🏛️ KIẾN TRÚC HỆ THỐNG PHÂN TÁN (MICROSERVICES ARCHITECTURE)

Dự án được xây dựng theo chuẩn kiến trúc **Domain-Driven Microservices** và **Event-Driven Architecture**:

```
BTL/
├── gateway/                 # API Gateway (Nginx Reverse Proxy & Security Filter - Port 8000)
├── services/
│   ├── auth-service/        # Identity & Reputation Service (HUNRE SSO, Trust Score - Port 8001)
│   ├── product-service/     # Catalog, Inventory & Time-decay Pricing Engine (Port 8002)
│   ├── escrow-service/      # Smart Escrow, VietQR Webhook, Ledger Kế toán kép (Port 8003)
│   ├── hub-service/         # O2O Logistics, Locker Grid, Dynamic TOTP QR Code (Port 8004)
│   └── ai-engine/           # Python FastAPI: CV Inspection, Barter Graph Solver (Port 8005)
├── frontend/
│   ├── student-portal/      # Giao diện Sinh viên HUNRE (Modern Glassmorphism UI - Port 3000)
│   └── hub-staff-portal/    # Ứng dụng PWA dành cho Thủ kho / Nhân viên Trạm Hub (Port 3001)
├── shared/
│   ├── database-init/       # Script SQL schema & Seed data ban đầu cho MySQL
│   └── postman/             # Bộ sưu tập API Postman hoàn chỉnh
├── docs/                    # Tài liệu báo cáo NCKH, thiết kế thuật toán & ERD Database
├── docker-compose.yml       # Điều phối toàn bộ container dịch vụ
└── run-dev.ps1              # Script khởi động nhanh môi trường phát triển cục bộ
```

---

## 📊 DANH SÁCH CÁC CỔNG DỊCH VỤ (PORT ALLOCATION)

| Dịch vụ | Công nghệ | Cổng (Port) | Đường dẫn API Route |
| :--- | :--- | :---: | :--- |
| **API Gateway** | Nginx Reverse Proxy | `8000` | `http://localhost:8000/` |
| **Student Portal** | HTML5 / Glassmorphism / ES6+ | `3000` | `http://localhost:8000/` |
| **Hub Staff App** | Mobile-First Web PWA | `3001` | `http://localhost:8000/staff` |
| **Auth Service** | Laravel 11 / PHP 8.2+ | `8001` | `http://localhost:8000/api/v1/auth` |
| **Product Service** | Laravel 11 / PHP 8.2+ | `8002` | `http://localhost:8000/api/v1/products` |
| **Escrow Service** | Laravel 11 / PHP 8.2+ | `8003` | `http://localhost:8000/api/v1/escrow` |
| **Hub Service** | Laravel 11 / PHP 8.2+ | `8004` | `http://localhost:8000/api/v1/hub` |
| **AI Intelligence Engine** | Python 3.10+ / FastAPI / Uvicorn | `8005` | `http://localhost:8000/api/v1/ai` |
| **MySQL Database** | MySQL 8.0 | `3306` | `localhost:3306` (Database: `hunre_ecommerce`) |
| **Redis Cache / Broker** | Redis 7 | `6379` | `localhost:6379` |

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

### Cách 1: Khởi chạy bằng Docker Compose (Khuyên dùng khi demo / bảo vệ)
```powershell
cd d:\Intel\Project\crs-microservices\BTL
docker-compose up -d --build
```
Sau khi các container khởi động, truy cập:
- **Giao diện sinh viên:** `http://localhost:8000`
- **Giao diện nhân viên trạm Hub:** `http://localhost:8000/staff`
- **Tài liệu API Swagger (AI Service):** `http://localhost:8005/docs`

### Cách 2: Khởi chạy Cục Bộ (Local Development Runner)
Chạy script PowerShell tự động kiểm tra và khởi chạy các dịch vụ:
```powershell
cd d:\Intel\Project\crs-microservices\BTL
.\run-dev.ps1
```

---

## 🔬 ĐIỂM SÁNG NGHIÊN CỨU KHOA HỌC (KEY RESEARCH NOVELTIES)

1. **Thuật toán Phát hiện Chu trình Trao đổi Đồ Đa Chiều (Multi-Hop Barter Graph):**
   - Ứng dụng **Johnson's Cycle Finding Algorithm** trên đồ thị có hướng $G=(V, E)$.
   - Giải quyết bài toán không tương đương giá trị bằng **Ma trận Bù trừ Tiền mặt (Cash Compensation Matrix)** thông qua Smart Escrow.
2. **Thẩm định Đồ cũ & Chống Gian lận Hình ảnh (Computer Vision Pipeline):**
   - Phát hiện ảnh mạng (Stock photos) bằng thuật toán **Perceptual Hashing (pHash)** và so sánh vector **CLIP Cosine Similarity**.
   - Nhận diện khuyết tật bề mặt (trầy xước, ố màu sách giáo trình) bằng **OpenCV Edge Contour & YOLOv8**.
3. **Mã QR Động Bảo Mật (Dynamic TOTP QR Engine):**
   - Chống gian lận chuyển tiếp mã qua ảnh chụp màn hình nhờ cơ chế xoay mã **HMAC-SHA256** tự hủy mỗi 30 giây.
4. **Hệ thống Điểm Uy Tín Sinh Viên HUNRE (Trust Score Engine):**
   - Đánh giá tín nhiệm tự động dựa trên tần suất hoàn thành giao dịch O2O, phản hồi từ cộng tác viên trạm Hub và đánh giá 5 sao.

---
*© 2026 HUNRE E-Commerce Research Team. All rights reserved.*
