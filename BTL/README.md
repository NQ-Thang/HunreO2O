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

## 🤝 HƯỚNG DẪN LÀM VIỆC NHÓM AN TOÀN (TEAM COLLABORATION GUIDELINES)
> **Dành cho tất cả thành viên trong nhóm:** Cách sửa code, cập nhật tính năng mà **không làm ảnh hưởng hoặc làm hỏng dự án**.

### 1. 📌 Lịch sử Commit & Đồng bộ gần nhất
- **Branch chính**: `master`
- **Remote**: `https://github.com/Ngvanchien205/crs-microservices.git`
- **Commit mới nhất**: `e6ce410` (*feat: integrate BTL HUNRE O2O microservices, update frontend & clean build artifacts*)
- **Nội dung commit**:
  - Tích hợp toàn bộ hệ thống nền tảng BTL HUNRE O2O & AI Engine (`BTL/`).
  - Toàn bộ tài liệu toán học, thuật toán và báo cáo PDF (`BTL/tailieu/`, `BTL/docs/`).
  - Cập nhật UI & Custom Hook cho `crs-frontend` (`CourseList.tsx`, `useCourses.ts`,...).
  - Dọn dẹp các thư mục rác/build nhị phân (`registration-service/target/`, log files) và thiết lập file cấu hình `.gitignore` chuẩn hóa toàn dự án.
- **Trạng thái**: Đồng bộ 100% với Git remote (`working tree clean`).

---

### 2. 🛡️ Bản quy tắc 5 bước khi sửa code dự án

Dự án là hệ thống phân tán đa dịch vụ (gồm cả **CRS Java Spring Boot** và **BTL Microservices PHP/Python/Docker**). Để tránh xung đột mã nguồn và không làm gián đoạn người khác, mọi thành viên **bắt buộc tuân thủ 5 quy tắc** sau:

#### 📌 QUY TẮC 1: Không bao giờ sửa và push trực tiếp trên nhánh `master`
Mỗi thành viên khi làm chức năng hoặc sửa lỗi bắt buộc phải tạo nhánh riêng:

```bash
# 1. Chuyển về master và kéo mã nguồn mới nhất về
git checkout master
git pull origin master

# 2. Tạo một nhánh mới mang tên mình và tính năng cần làm
# Cú pháp: git checkout -b feature/<tên-thành-viên>-<chức-năng>
git checkout -b feature/tuan-sua-giao-dien-san-pham

# 3. Tiến hành sửa code, test chạy ok trên máy cá nhân...

# 4. Khi hoàn thành, chỉ add các file mình sửa
git add <đường_dẫn_file_đã_sửa>
git commit -m "feat(product): them bo loc danh muc theo gia"

# 5. Push nhánh riêng lên GitHub
git push origin feature/tuan-sua-giao-dien-san-pham
```
> **Lợi ích:** Dù bạn có làm lỗi code thì nhánh `master` của dự án vẫn hoàn toàn bình thường, không làm gián đoạn người khác. Sau đó người phụ trách repo chỉ cần kiểm tra rồi Merge vào `master`.

---

#### 📌 QUY TẮC 2: Giữ nguyên "Hợp đồng API" (API Contract) giữa các Microservices
Hệ thống gồm nhiều service gọi chéo nhau (Gateway $\to$ Auth $\to$ Product $\to$ Escrow $\to$ AI Engine hoặc Gateway $\to$ Registration $\to$ Course):

1. **Tuyệt đối KHÔNG tự ý đổi tên các trường (field) trong JSON Response:**
   - *Ví dụ:* Nếu API đang trả về `{ "product_id": 10, "current_price": 50000 }`, **không được** đổi thành `{ "id": 10, "price": 50000 }` vì Frontend và các service khác đang đọc `product_id` sẽ lập tức bị lỗi `undefined` hoặc crash hệ thống.
2. **Nếu cần thêm dữ liệu:** Hãy bổ sung thêm trường mới (additive change) thay vì sửa hay xóa trường cũ:
   - *Đúng:* Thêm `{ "product_id": 10, "current_price": 50000, "category_name": "Sách" }`.
3. **Nếu sửa API Endpoint:** Phải cập nhật đồng bộ ở cả Gateway cấu hình route và Frontend/Client gọi đến.

---

#### 📌 QUY TẮC 3: Tuyệt đối không thay đổi Port và cấu hình Docker dùng chung
File `BTL/docker-compose.yml` quy định các cổng mặc định:
- `3307`: MySQL Database BTL (hoặc `3306` cho CRS)
- `6379`: Redis
- `8000`: API Gateway BTL (Cổng `8080` cho Gateway CRS)
- `8001 - 8005`: Các Service (Auth, Product, Escrow, Hub, AI)

**Lưu ý:**
- Thành viên không tự ý đổi cổng các service này trong file gốc. Nếu máy cá nhân bị trùng port (ví dụ cổng 3306 đã có MySQL khác), hãy dùng cổng `3307` đã được cấu hình sẵn cho BTL.
- Khi chỉ sửa **1 service** (ví dụ `product-service`), chỉ cần restart service đó thay vì restart toàn bộ hệ thống:
  ```bash
  docker compose restart product-service
  ```

---

#### 📌 QUY TẮC 4: Quy tắc sửa Database an toàn (Không làm mất dữ liệu)
- **Cấm tuyệt đối:** Không chạy lệnh `DROP TABLE` hoặc `TRUNCATE TABLE` trên cơ sở dữ liệu dùng chung.
- **Khi cần thêm bảng hoặc thêm cột mới:**
  - Không sửa trực tiếp đè vào dữ liệu đang có.
  - Viết 1 file script migration riêng (ví dụ: `BTL/shared/database-init/02_update_user_profile.sql`) với cú pháp an toàn:
    ```sql
    ALTER TABLE users ADD COLUMN phone_number VARCHAR(15) NULL;
    ```
  - Cách làm này đảm bảo code của người khác chạy lại không bị lỗi thiếu bảng hoặc mất sạch dữ liệu test.

---

#### 📌 QUY TẮC 5: Checklist kiểm tra trước khi commit lên Git
Trước khi gõ `git add .` và `git commit`, yêu cầu thành viên chạy:
```bash
git status
```
Và kiểm tra 3 điều:
1. **Có file rác không? Tuyệt đối không commit:**
   - Thư mục thư viện: `node_modules/`, `vendor/`, `.venv/`
   - File build & cache: `target/`, `*.class`, `__pycache__/`, `.pytest_cache/`
   - File cấu hình mật khẩu cá nhân: `.env`
   - File nhật ký: `*.log`
2. **Code có chạy được ở local không?** Tự kiểm tra xem trang web hay service mình vừa sửa có bị crash hay không trước khi đẩy lên.
3. **Commit message có ý nghĩa:** Ghi rõ mình sửa cái gì (ví dụ: `fix(auth): sua loi token het han` thay vì chỉ ghi `update`, `fix bug`, `abc`).

---

### 💬 Tin nhắn mẫu gửi cho nhóm

> *"Code mới nhất đã được commit và push lên nhánh `master`. Mọi người trước khi làm việc nhớ gõ `git checkout master` và `git pull origin master`. Khi code tính năng mới, vui lòng tạo nhánh riêng (`git checkout -b feature/<tên-bạn>`), không sửa đè trực tiếp trên master, không đổi cấu hình port trong docker-compose và không đổi tên các trường API cũ để tránh làm lỗi các service khác nhé!"*

---

## 🤖 HƯỚNG DẪN DÀNH CHO AI ASSISTANT (CURSOR / COPILOT / CHATGPT / CLAUDE / GEMINI)

> **CRITICAL INSTRUCTIONS FOR AI AGENTS & CODING ASSISTANTS:**  
> Nếu bạn là một Trợ lý AI (Cursor Agent, GitHub Copilot, Claude, ChatGPT, Gemini, v.v.) đang đọc repository này để hỗ trợ lập trình viên, bạn **BẮT BUỘC PHẢI TUÂN THỦ NGHIÊM NGẶT (STRICT CONSTRAINTS)** các quy tắc kiến trúc sau:

### 1. Kiến trúc tổng quan (Architecture Overview)
- **Hệ thống gốc (`crs-microservices`):** Java 17 + Spring Boot (`api-gateway`: 8080, `auth-service`: 8081, `course-service`: 8082, `registration-service`: 8083, MySQL: 3306) + React TypeScript (`crs-frontend`: 5173).
- **Hệ thống BTL HUNRE (`/BTL`):** Microservices phân tán PHP Laravel + Python FastAPI (`gateway`: 8000, `auth`: 8001, `product`: 8002, `escrow`: 8003, `hub`: 8004, `ai-engine`: 8005, MySQL: 3307, Redis: 6379) + Frontend Vanilla JS/Glassmorphism.

### 2. Các quy tắc cấm kỵ dành cho AI (AI Constraints)
1. 🚫 **KHÔNG BAO GIỜ hướng dẫn commit/push thẳng lên `master`:** Luôn luôn chủ động nhắc lập trình viên kiểm tra nhánh hiện tại và tạo nhánh tính năng mới (`git checkout -b feature/<ten-tinh-nang>`).
2. 🚫 **KHÔNG ĐƯỢC PHÁ VỠ HỢP ĐỒNG API (API CONTRACTS):**
   - Tuyệt đối không xóa, không đổi kiểu, không đổi tên các trường dữ liệu JSON (keys) trong Request/Response DTO hiện có của các microservices.
   - Khi có tính năng mới: Luôn luôn triển khai theo phương thức **bổ sung thêm trường mới (Additive Only)** để đảm bảo tính tương thích ngược (Backwards Compatibility) cho các service gọi chéo và Frontend.
   - Nếu buộc phải đổi endpoint, AI phải cập nhật đồng bộ cả API Gateway ([`BTL/gateway/nginx.conf`](file:///d:/Intel/Project/crs-microservices/BTL/gateway/nginx.conf) hoặc Spring Cloud Gateway) và toàn bộ Frontend liên quan.
3. 🚫 **KHÔNG THAY ĐỔI CỔNG (PORTS) VÀ CẤU HÌNH DOCKER GỐC:**
   - Không tự ý sửa đổi mapping port trong [`BTL/docker-compose.yml`](file:///d:/Intel/Project/crs-microservices/BTL/docker-compose.yml) (`8000-8005`, `3307`, `6379`) hoặc cấu hình cổng Java (`8080-8083`, `3306`).
4. 🚫 **TUYỆT ĐỐI KHÔNG SINH CODE PHÁ HỦY DATABASE (DESTRUCTIVE MIGRATIONS):**
   - Cấm sinh lệnh `DROP TABLE`, `TRUNCATE` hoặc xóa cột trực tiếp.
   - Mọi thay đổi cấu trúc bảng phải tạo file script migration an toàn mới (ví dụ: `ALTER TABLE ... ADD COLUMN ... DEFAULT ...;`).
5. 🚫 **CẤM COMMIT FILE RÁC & DỮ LIỆU BUILD:**
   - Không được đề xuất hay chạy lệnh `git add` vào: `node_modules/`, `vendor/`, `target/`, `__pycache__/`, `*.class`, `*.log`, `.env`, `.venv/`. Luôn tuân thủ triệt để [`.gitignore`](file:///d:/Intel/Project/crs-microservices/.gitignore).
6. 🎯 **NGUYÊN TẮC ĐỘC LẬP DỊCH VỤ (SERVICE ISOLATION):**
   - Khi sửa đổi một dịch vụ (ví dụ `product-service` hay `ai-engine`), giữ cho phạm vi thay đổi nằm gọn trong thư mục của dịch vụ đó, không gây tác dụng phụ (side-effects) làm gãy các dịch vụ khác.

---
*© 2026 HUNRE E-Commerce Research Team. All rights reserved.*
