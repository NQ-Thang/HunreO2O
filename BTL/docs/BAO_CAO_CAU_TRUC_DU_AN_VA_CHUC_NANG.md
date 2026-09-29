# BÁO CÁO CẤU TRÚC DỰ ÁN & MÔ TẢ CHI TIẾT CÁC MODULE
## Đề Tài: Sàn Giao Dịch & Trao Đổi Đồ Dùng Học Tập Sinh Viên HUNRE (Mô Hình O2O & AI)
**Trường Đại học Tài nguyên và Môi trường Hà Nội (HUNRE)**  
**Đơn vị thực hiện:** Khoa Công Nghệ Thông Tin  

---

## 1. TỔNG QUAN HỆ THỐNG (SYSTEM OVERVIEW)

### 1.1. Vấn đề thực tế của sinh viên HUNRE
- **Mua bán đồ dùng học tập cũ (giáo trình, máy tính Casio, bàn phím, laptop, balo):** Sinh viên thường giao dịch tự phát trên các nhóm Facebook, Zalo, đối mặt với các rủi ro:
  1. **Bom hàng, bùng hẹn:** Người mua/bán không đến điểm hẹn.
  2. **Lừa đảo tiền cọc:** Chuyển khoản trước rồi bị chặn liên lạc.
  3. **Hàng không đúng mô tả:** Dùng ảnh mạng lung linh nhưng khi giao hàng là đồ nát, hỏng.
  4. **Nhu cầu trao đổi chéo (Barter Trading):** Bạn A có sách CSDL muốn đổi Casio, bạn B có Casio muốn đổi Bàn phím, bạn C có Bàn phím muốn đổi sách CSDL. Trước đây không có hệ thống nào tự động kết nối được nhu cầu này.

### 1.2. Giải pháp đột phá của dự án
Dự án xây dựng nền tảng thương mại điện tử thế hệ mới kết hợp **O2O (Online-to-Offline)** và **AI (Trí Tuệ Nhân Tạo)**:
- **Trạm Hub Trung Gian O2O:** Đặt tại Văn phòng Đoàn Thanh niên (Nhà A - CS1 và CS2). Mọi hàng hóa đều gửi - nhận tại Trạm Hub thông qua hệ thống tủ Locker bảo mật.
- **Ký Quỹ Thông Minh (Smart Escrow):** Tiền cọc được đóng băng an toàn trong ví trung gian. Chỉ khi người mua đến Hub kiểm tra tận tay, bấm xác nhận hài lòng thì tiền mới được giải ngân cho người bán.
- **Dynamic QR TOTP (30s):** Mã QR xác thực nhận hàng xoay vòng mỗi 30 giây bằng thuật toán mã hóa HMAC-SHA256, chống tuyệt đối việc chụp trộm màn hình để lấy trộm đồ.
- **AI Computer Vision & Anti-Fraud:** Thị giác máy tính tự động đánh giá độ mòn, trầy xước của đồ cũ, dán nhãn phân hạng chất lượng (Grade S/A/B) và đối chiếu mã băm thị giác (dHash) để ngăn chặn việc lấy ảnh mạng đăng bài.
- **AI Barter Graph 2.0:** Thuật toán đồ thị có hướng (Directed Cycle Detection) tự động tìm kiếm chu trình đổi đồ 3 chiều ($A \to B \to C \to A$) kèm ma trận bù trừ tiền mặt tự động bảo toàn số dư (Zero-sum Conservation).

---

## 2. KIẾN TRÚC TỔNG THỂ HỆ THỐNG (ARCHITECTURE OVERVIEW)

Hệ thống được thiết kế theo kiến trúc **Microservices chuẩn Enterprise**, đóng gói hoàn toàn bằng **Docker & Docker Compose**:

```
                              [ BROWSER / CLIENT ]
                                        │
                         HTTP / Port 8000 (Cổng Chính)
                                        │
                                        ▼
                   ┌─────────────────────────────────────────┐
                   │        API GATEWAY (Nginx Alpine)       │
                   │  - Cung cấp Student Portal (HTML/CSS/JS)│
                   │  - Cung cấp Hub Staff Scanner Portal    │
                   │  - Định tuyến Reverse Proxy & CORS      │
                   └────┬─────┬──────┬──────┬──────┬─────────┘
                        │     │      │      │      │
      ┌─────────────────┘     │      │      │      └─────────────────┐
      │                       │      │      │                        │
      ▼                       ▼      ▼      ▼                        ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ AUTH SERVICE│ │ PRODUCT SVC │ │ ESCROW SVC  │ │   HUB SVC   │ │  AI ENGINE  │
│  Port 8001  │ │  Port 8002  │ │  Port 8003  │ │  Port 8004  │ │  Port 8005  │
│  (PHP/REST) │ │  (PHP/CRUD) │ │  (PHP/Saga) │ │ (PHP/TOTP)  │ │(FastAPI/CV) │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │               │
       └───────────────┼───────────────┴───────────────┘               │
                       │                                               │
                       ▼                                               ▼
          ┌─────────────────────────┐                     ┌─────────────────────────┐
          │  MySQL 8.0 (Port 3307)  │                     │  PyTorch / OpenCV / PIL │
          │  Lưu trữ dữ liệu chính  │                     │  NetworkX Graph Solver  │
          └─────────────────────────┘                     └─────────────────────────┘
                       ▲
                       │
          ┌─────────────────────────┐
          │   Redis 7 (Port 6379)   │
          │   Cache & Quản lý TOTP  │
          └─────────────────────────┘
```

---

## 3. CẤU TRÚC CÁC THƯ MỤC & MODULE CHI TIẾT

```
BTL/
├── docker-compose.yml              # Cấu hình khởi chạy 8 container đồng bộ
├── gateway/                        # Cổng API Gateway & Reverse Proxy
│   └── nginx.conf                  # Cấu hình định tuyến, MIME types & CORS
├── shared/                         # Dữ liệu dùng chung
│   └── database-init/
│       └── init-schema.sql         # Khởi tạo CSDL MySQL 8.0 & dữ liệu mẫu
├── frontend/                       # Giao diện người dùng thuần HTML/CSS/JS (Be Vietnam Pro)
│   ├── student-portal/             # Sàn giao dịch dành cho sinh viên HUNRE
│   │   ├── index.html              # Trang chủ: Danh mục hàng, Thẩm định AI, Trả giá AI
│   │   ├── css/style.css           # Design System giao diện hiện đại, chuẩn tiếng Việt
│   │   ├── js/app.js               # Logic gọi API microservices qua Gateway
│   │   └── pages/
│   │       ├── barter-graph.html   # Giao diện trực quan hóa Đồ thị trao đổi đồ 3 chiều
│   │       └── escrow-order.html   # Giao diện theo dõi 7 bước Ký quỹ & Dynamic QR TOTP
│   └── hub-staff-portal/           # Web App dành cho nhân viên Đoàn Trường trực Trạm Hub
│       ├── index.html              # Quét mã QR Check-in/Check-out, quản lý ô tủ locker
│       └── css/style.css           # Bộ style độc lập cho Trạm Hub
├── services/                       # 5 Dịch vụ Microservices độc lập
│   ├── auth-service/               # Quản lý định danh, tài khoản sinh viên & Điểm Uy Tín
│   ├── product-service/            # Quản lý danh mục hàng hóa & ĐĂNG BÁN - THÊM / SỬA / XÓA (CRUD)
│   ├── escrow-service/             # Điều phối Saga phân tán, bảo vệ tiền ký quỹ
│   ├── hub-service/                # Quản lý Trạm Hub O2O, sinh mã Dynamic QR TOTP HMAC
│   └── ai-engine/                  # Bộ não AI: FastAPI, NetworkX, OpenCV, dHash
└── docs/                           # Tài liệu kiến trúc, toán học thuật toán & kiểm thử
```

---

## 4. MÔ TẢ CHI TIẾT CÁC MODULE CHỨC NĂNG

### 4.1. Module API Gateway (`gateway/`)
- **Công nghệ:** Nginx Alpine trên Port `8000`.
- **Nhiệm vụ:**
  - Là điểm truy cập duy nhất (Single Point of Entry) cho toàn bộ sinh viên và cán bộ quản lý.
  - Phục vụ tĩnh giao diện Web (`student-portal` tại `/`, `hub-staff-portal` tại `/staff`).
  - Định tuyến trong suốt (Reverse Proxy) các cuộc gọi API từ trình duyệt tới 5 microservices backend mà không để lộ cổng nội bộ.
  - Xử lý CORS Header, nén Gzip tăng tốc độ tải trang và áp dụng MIME type chuẩn (`text/css`, `application/javascript`).

### 4.2. Module Xác Thực & Điểm Uy Tín (`services/auth-service/`)
- **Cổng nội bộ:** `8001` (qua Gateway: `/api/v1/auth`).
- **Chức năng chính:**
  1. **Xác thực sinh viên:** Quản lý tài khoản gắn liền với Mã Sinh Viên HUNRE (ví dụ: `20211001`).
  2. **Hệ thống Điểm Uy Tín (Trust Score Engine):**
     - Mỗi sinh viên khởi điểm có 500 điểm.
     - Hoàn tất 1 giao dịch đúng hẹn tại Trạm Hub: **+5 điểm**.
     - Có hành vi gian lận hoặc bom hàng: **-50 điểm**.
     - Phân cấp bậc sinh viên: Đồng (< 400), Bạc (400 - 600), Vàng (600 - 800), Kim Cương (> 800).
  3. **Ưu đãi theo điểm:** Sinh viên có điểm uy tín cao được miễn giảm tiền cọc ký quỹ và được AI ưu tiên chấp nhận trả giá khi mua đồ.

---

### ⭐ 4.3. MODULE ĐĂNG BÁN & QUẢN LÝ SẢN PHẨM: THÊM - XEM - SỬA - XÓA (CRUD ENGINE)

> [!IMPORTANT]
> **Đây là phân hệ cốt lõi quản lý vòng đời tin đăng của sinh viên**, cho phép sinh viên đăng bán đồ cũ, cập nhật giá, chỉnh sửa mô tả và gỡ bỏ sản phẩm khi đã bán xong.

#### 4.3.1. Vị trí mã nguồn trong dự án (Nằm ở đâu?)

1. **Giao diện người dùng (Frontend):**
   - File giao diện chính: [`frontend/student-portal/index.html`](file:///d:/Intel/Project/crs-microservices/BTL/frontend/student-portal/index.html)
     - Nút kích hoạt: Nút `<button class="btn btn-primary" onclick="openAiInspectModal()">` (nút **"Đăng Bán & Thẩm Định"** trên Navbar).
     - Khung hiển thị sản phẩm: `<div class="products-grid" id="productsGrid">` hiển thị danh sách sản phẩm theo thời gian thực kèm nhãn AI Grade.
     - Modal Thẩm Định & Đăng bán: `<div class="modal-overlay" id="aiInspectModal">`.
   - File xử lý JavaScript: [`frontend/student-portal/js/app.js`](file:///d:/Intel/Project/crs-microservices/BTL/frontend/student-portal/js/app.js)
     - Hàm mở/đóng modal: `openAiInspectModal()`, `closeAiInspectModal()`.
     - Hàm tải ảnh và gọi thẩm định AI: `handleImageSelected(event)`.
     - Hàm lọc danh mục sản phẩm: `filterProducts(category, btnElement)`.

2. **Cổng định tuyến (API Gateway Routing):**
   - File cấu hình: [`gateway/nginx.conf`](file:///d:/Intel/Project/crs-microservices/BTL/gateway/nginx.conf)
   - Khối định tuyến:
     ```nginx
     # Định tuyến toàn bộ yêu cầu sản phẩm sang Product Microservice (Port 8002)
     location /api/v1/products {
         proxy_pass http://product-service:8002;
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
     }
     ```

3. **Dịch vụ nghiệp vụ (Backend Microservice):**
   - Thư mục dịch vụ: [`services/product-service/`](file:///d:/Intel/Project/crs-microservices/BTL/services/product-service/)
   - File xử lý chính (Entrypoint): [`services/product-service/public/index.php`](file:///d:/Intel/Project/crs-microservices/BTL/services/product-service/public/index.php)
     - Xử lý các phương thức HTTP: `GET`, `POST`, `PUT`, `DELETE`.
     - Lưu trữ trạng thái và tự động phản hồi JSON theo chuẩn RESTful.
   - Controller kiến trúc MVC: [`services/product-service/app/Http/Controllers/ProductController.php`](file:///d:/Intel/Project/crs-microservices/BTL/services/product-service/app/Http/Controllers/ProductController.php)
     - Phương thức `index()`: Lấy danh sách sản phẩm kèm thông tin người bán và điểm uy tín.
     - Phương thức `show($id)`: Xem chi tiết 1 sản phẩm kèm báo cáo thẩm định AI.
     - Phương thức `store()`: Đăng bán sản phẩm mới, kiểm tra tính hợp lệ dữ liệu.
     - Phương thức `enableTimeDecay()`: Kích hoạt tự động hạ giá theo thời gian.
   - Định tuyến API Laravel/Lumen: [`services/product-service/routes/api.php`](file:///d:/Intel/Project/crs-microservices/BTL/services/product-service/routes/api.php)

4. **Cơ sở dữ liệu lưu trữ (MySQL 8.0 Database):**
   - File khởi tạo Schema: [`shared/database-init/init-schema.sql`](file:///d:/Intel/Project/crs-microservices/BTL/shared/database-init/init-schema.sql)
   - Bảng **`products`** (Dòng 40 - 61):
     - `id`: Khóa chính tự tăng (BIGINT).
     - `seller_id`: Khóa ngoại liên kết với bảng `users` (Mã sinh viên người bán).
     - `category_id`: Khóa ngoại liên kết bảng `categories` (Sách giáo trình, Thiết bị điện tử,...).
     - `title`: Tiêu đề sản phẩm (VARCHAR 255).
     - `original_price`: Giá niêm yết ban đầu.
     - `current_price`: Giá bán hiện tại (được cập nhật nếu có hạ giá tự động).
     - `floor_price`: Mức giá sàn tối thiểu người bán chấp nhận khi đàm phán AI.
     - `condition_grade`: Phân loại chất lượng AI (`GRADE_S`, `GRADE_A`, `GRADE_B`, `GRADE_C`).
     - `ai_defect_score`: Điểm tỷ lệ trầy xước/hao mòn do Computer Vision tính toán.
     - `is_barter_eligible`: Cờ cho phép tham gia vòng tròn đổi đồ 3 chiều (1 = Có, 0 = Không).
     - `desired_exchange_items`: Tên món đồ sinh viên mong muốn đổi lại.
     - `status`: Trạng thái tin đăng (`ACTIVE`, `STORED_IN_HUB`, `SOLD`, `CANCELLED`).

---

#### 4.3.2. Chi tiết 4 chức năng CRUD (Thêm - Xem - Sửa - Xóa)

| Thao tác | Phương thức HTTP | Endpoint API | Chức năng chi tiết & Dữ liệu truyền nhận |
| :--- | :---: | :--- | :--- |
| **1. ĐĂNG BÁN (Thêm mới)** | `POST` | `/api/v1/products` | **Đăng sản phẩm mới lên sàn:**<br>• Gửi kèm: `title`, `price`, `floor_price`, `category_id`, `condition_grade`, `desired_exchange_items`, `image_url`.<br>• Tự động kết nối sang AI Engine thẩm định ảnh trước khi kích hoạt.<br>• Phản hồi: HTTP `201 Created` kèm thông tin sản phẩm và mã ID mới. |
| **2. XEM DANH SÁCH** | `GET` | `/api/v1/products` | **Lấy toàn bộ sản phẩm đang hoạt động:**<br>• Hỗ trợ tham số lọc: `?category=BOOKS` hoặc `?category=TECH`.<br>• Trả về danh sách sản phẩm gồm ảnh, giá, nhãn chất lượng AI và món đồ cần đổi. |
| **3. XEM CHI TIẾT** | `GET` | `/api/v1/products/{id}` | **Lấy thông tin chi tiết 1 sản phẩm:**<br>• Trả về thông tin người bán, điểm uy tín HUNRE, mô tả khuyết tật do AI đánh giá và giá sàn. |
| **4. CHỈNH SỬA (Sửa)** | `PUT` | `/api/v1/products/{id}` | **Cập nhật thông tin món đồ:**<br>• Cho phép sửa: Giá bán hiện tại (`current_price`), giá sàn (`floor_price`), tiêu đề, mô tả, món đồ mong muốn đổi lại.<br>• Cập nhật thời gian `updated_at` trong CSDL. |
| **5. XÓA / GỠ TIN** | `DELETE` | `/api/v1/products/{id}` | **Gỡ sản phẩm khỏi sàn:**<br>• Khi sinh viên đã bán xong hoặc không còn nhu cầu giao dịch, sản phẩm được gỡ bỏ khỏi sàn hiển thị, đảm bảo dữ liệu luôn mới. |

---

#### 4.3.3. Quy trình nghiệp vụ khi Sinh viên Đăng Bán Hàng (Workflow)

```
[Sinh viên chọn "Đăng Bán & Thẩm Định"]
                │
                ▼
      [Tải ảnh đồ cũ lên UI]
                │
                ▼
[Gọi AI Service: POST /api/v1/ai/cv/inspect]
  ├─ 1. OpenCV: Đo độ trầy xước, ố vàng ➔ Gán nhãn GRADE A (94%)
  └─ 2. Anti-Fraud: Tính mã băm dHash ➔ Xác thực ảnh thực tế sinh viên
                │
                ▼
[Nhập: Tên đồ, Giá bán, Giá sàn, Món đồ muốn đổi]
                │
                ▼
[Gọi Product Service: POST /api/v1/products]
  ├─ 1. Kiểm tra tính hợp lệ dữ liệu (Validate)
  ├─ 2. Lưu vào bảng `products` với trạng thái `ACTIVE`
  └─ 3. Trả về thông báo thành công và hiển thị ngay lên Chợ Sinh Viên
```

---

### 4.4. Module Ký Quỹ Thông Minh (`services/escrow-service/`)
- **Cổng nội bộ:** `8003` (qua Gateway: `/api/v1/escrow`).
- **Chức năng chính:**
  1. **Điều phối giao dịch Saga 7 trạng thái (Distributed Saga Orchestration):**
     - **Bước 1 (INITIATED):** Người mua tạo đơn hàng.
     - **Bước 2 (DEPOSITED):** Người mua chuyển tiền vào tài khoản ký quỹ trung gian, tiền bị đóng băng an toàn.
     - **Bước 3 (SELLER_CHECKIN):** Người bán mang đồ đến Trạm Hub CS1 Nhà A quét mã gửi đồ vào tủ.
     - **Bước 4 (STORED_AT_HUB):** Hàng nằm an toàn trong ô tủ Locker tại Trạm Hub.
     - **Bước 5 (BUYER_CHECKOUT):** Người mua đến Hub quét mã nhận đồ và mở hộp kiểm tra trực tiếp.
     - **Bước 6 (COMPLETED / RELEASED):** Người mua xác nhận hài lòng, tiền ký quỹ tự động giải ngân cho người bán.
     - **Bước 7 (DISPUTED):** Nếu hàng vỡ hỏng, người mua bấm "Khiếu nại", tiền ký quỹ lập tức bị giữ lại để Trạm Hub hoàn cọc 100%.

### 4.5. Module Quản Lý Trạm Hub O2O (`services/hub-service/`)
- **Cổng nội bộ:** `8004` (qua Gateway: `/api/v1/hub`).
- **Chức năng chính:**
  1. **Quản lý hệ thống ô tủ Locker:** Phân bổ ô tủ theo kích cỡ: Cỡ S (sách vở), Cỡ M (phím chuột, máy tính Casio), Cỡ L (màn hình, case PC).
  2. **Động cơ Dynamic QR TOTP (Time-based One-Time Password):**
     - Sinh mã QR động bằng thuật toán HMAC-SHA256 kết hợp thời gian thực theo khung 30 giây.
     - Sau mỗi 30 giây, mã QR tự động đổi sang chữ ký mới. Ngăn chặn tuyệt đối việc người lạ chụp ảnh màn hình của sinh viên để đến nhận trộm đồ tại Trạm Hub.

### 4.6. Module Trí Tuệ Nhân Tạo AI Engine (`services/ai-engine/`)
- **Cổng nội bộ:** `8005` (qua Gateway: `/api/v1/ai`).
- **Công nghệ:** Python 3.11, FastAPI, Uvicorn, NetworkX, OpenCV, Pillow.
- **Chức năng chính:**
  1. **AI Computer Vision Thẩm định đồ cũ (`/api/v1/ai/cv/inspect`):**
     - Đo lường độ trầy xước viền, độ ố vàng của trang sách qua độ lệch chuẩn Laplacian và phân tích kênh màu HSV.
     - Tự động gán nhãn: **GRADE S** (Độ mới > 95%), **GRADE A** (Độ mới 90-95%), **GRADE B** (Độ mới 80-90%), **GRADE C** (< 80%).
  2. **Chống gian lận ảnh mạng Anti-Fraud (`/api/v1/ai/anti-fraud/check`):**
     - Sử dụng thuật toán băm thị giác chênh lệch Gradient (dHash - 64-bit fingerprint).
     - Đối chiếu với kho ảnh mạng thương mại, cảnh báo ngay nếu sinh viên tải ảnh từ Shopee/Tiki về đăng bán ảo.
  3. **AI Barter Graph Solver 2.0 (`/api/v1/ai/barter/solve-cycles`):**
     - Xây dựng đồ thị có hướng $G=(V, E)$, với đỉnh $V$ là sinh viên, cạnh $E$ là nguyện vọng đổi đồ.
     - Sử dụng thuật toán tìm chu trình cơ bản Johnson's Cycle Detection để phát hiện các vòng tròn trao đổi 3 người ($A \to B \to C \to A$).
     - Áp dụng Định luật bảo toàn số dư (Zero-Sum Conservation) tính toán ma trận bù trừ tiền mặt: Tổng tiền các bạn nộp bù vào ký quỹ luôn bằng tổng tiền các bạn nhận về từ ký quỹ ($\sum \Delta V = 0$).
  4. **Trợ lý AI Đàm phán giá (`/api/v1/ai/pricing/negotiate`):**
     - Đàm phán tự động dựa trên mức giá sàn của người bán và Điểm Uy Tín của người mua, đưa ra quyết định: Chấp nhận (ACCEPT), Đề xuất giá mới (COUNTER_OFFER) hoặc Từ chối (REJECT).

### 4.7. Giao Diện Người Dùng (Frontends)
- **Cổng truy cập:**
  - Sàn giao dịch sinh viên: `http://localhost:8000/`
  - Vòng tròn đổi đồ 3 chiều: `http://localhost:8000/pages/barter-graph.html`
  - Quản lý ký quỹ Escrow: `http://localhost:8000/pages/escrow-order.html`
  - Cổng nhân viên Trạm Hub: `http://localhost:8000/staff/`
- **Đặc điểm giao diện:**
  - Sử dụng typography tối ưu tiếng Việt hiện đại (`Be Vietnam Pro` kết hợp `Inter`).
  - Tone màu Slate Dark kết hợp Xanh ngọc HUNRE (`#10B981`) chuyên nghiệp, hài hòa.
  - Loại bỏ hoàn toàn cảm giác "AI máy móc", thiết kế giống một sàn e-commerce thực tế, thân thiện và trực quan cho sinh viên.

---

## 5. BẢNG TỔNG HỢP CÁC ENDPOINT API CỦA HỆ THỐNG

| Dịch vụ | Phương thức | Đường dẫn API | Mô tả chức năng |
| :--- | :---: | :--- | :--- |
| **Auth** | `GET` | `/api/v1/auth/users/trust-score?user_id=1` | Lấy điểm uy tín và phân cấp bậc sinh viên |
| **Product** | `GET` | `/api/v1/products` | Lấy danh sách sản phẩm niêm yết (có lọc danh mục) |
| **Product** | `GET` | `/api/v1/products/{id}` | Xem chi tiết 1 sản phẩm kèm báo cáo AI |
| **Product** | `POST` | `/api/v1/products` | **Đăng bán / Thêm mới sản phẩm lên sàn** |
| **Product** | `PUT` | `/api/v1/products/{id}` | **Chỉnh sửa thông tin, cập nhật giá sản phẩm** |
| **Product** | `DELETE` | `/api/v1/products/{id}` | **Xóa hoặc gỡ sản phẩm khỏi sàn giao dịch** |
| **Product** | `POST` | `/api/v1/products/{id}/enable-time-decay` | Bật chế độ tự động hạ giá theo giờ (Dutch Auction) |
| **Escrow** | `GET` | `/api/v1/escrow/transactions` | Xem trạng thái giao dịch ký quỹ đơn hàng |
| **Escrow** | `POST` | `/api/v1/escrow/saga/advance` | Chuyển bước trong tiến trình Saga ký quỹ |
| **Hub** | `GET` | `/api/v1/hub/lockers` | Lấy danh sách ô tủ locker & mã Dynamic QR |
| **AI Engine** | `POST` | `/api/v1/ai/cv/inspect` | Tải ảnh lên phân tích độ hao mòn & pHash |
| **AI Engine** | `POST` | `/api/v1/ai/barter/solve-cycles` | Giải thuật toán chu trình đổi đồ 3 chiều |
| **AI Engine** | `POST` | `/api/v1/ai/pricing/negotiate` | Trợ lý AI tự động đàm phán giá |
| **AI Engine** | `POST` | `/api/v1/ai/pricing/decay` | Tính toán hạ giá theo thời gian Dutch Auction |

---

## 6. HƯỚNG DẪN THAO TÁC TRÌNH DIỄN CHỨC NĂNG (DEMO GUIDE)

Để báo cáo trực quan cho Thầy Cô và Hội Đồng đánh giá, bạn có thể thực hiện theo các bước sau trực tiếp trên trình duyệt:

1. **Thao tác 1 - Xem Sàn Giao Dịch & Lọc Danh Mục:**
   - Mở trình duyệt truy cập: `http://localhost:8000/`
   - Bấm thử các nút lọc: **"Tất cả"**, **"Giáo trình"**, **"Thiết bị điện tử"**. Xem các thẻ sản phẩm hiển thị nhãn Grade A, Grade B, Grade S và điểm uy tín sinh viên ở góc phải.

2. **Thao tác 2 - Thẩm Định Ảnh & Đăng Bán Bằng Trí Tuệ Nhân Tạo:**
   - Trên thanh menu bấm nút **"Đăng Bán & Thẩm Định"** (nút màu xanh lá).
   - Chọn thử nhanh các ảnh mẫu: *Sách CSDL (94%)*, *Casio 580 (98%)* hoặc bấm tải ảnh bất kỳ từ máy tính của bạn.
   - Xem kết quả AI phân tích: Tỷ lệ trầy xước, dán nhãn Grade S/A/B và chữ ký dHash xác thực không phải ảnh mạng.

3. **Thao tác 3 - Tìm Kiếm, Sửa & Gỡ Tin Đăng (Quản Trị CRUD):**
   - **Tìm kiếm:** Gõ từ khóa vào ô tìm kiếm (ví dụ: `Casio`, `CSDL`, `DareU`), sàn sẽ lọc kết quả thời gian thực ngay lập tức.
   - **Chỉnh sửa (Sửa tin):** Bấm nút **"Sửa tin"** trên bất kỳ sản phẩm nào -> Modal mở ra cho phép cập nhật tiêu đề, giá bán hiện tại, giá sàn và mô tả -> Bấm **"Lưu Thay Đổi"** để cập nhật ngay lập tức.
   - **Gỡ tin (Xóa):** Bấm nút **"Xóa"** màu đỏ trên thẻ sản phẩm -> Xác nhận hộp thoại -> Sản phẩm được gỡ bỏ khỏi sàn giao dịch.

4. **Thao tác 4 - Đàm Phán Trả Giá Tự Động Với AI & Tạo Đơn Ký Quỹ:**
   - Tại bất kỳ sản phẩm nào (ví dụ Giáo trình CSDL 75.000đ), bấm nút **"Trả Giá AI"**.
   - Nhập mức giá đề xuất (ví dụ: `65000`), bấm **"Gửi Đề Xuất Giá"**.
   - AI Agent sẽ đối chiếu giá sàn và điểm uy tín để phản hồi chấp nhận hoặc đưa ra mức giá tốt nhất.
   - Khi được chấp nhận giá, bấm nút **"Đặt Cọc Ký Quỹ Đơn Này"**: Hệ thống tự động tạo mã đơn ký quỹ mới và dẫn thẳng sang trang Quản lý Ký Quỹ Escrow!

5. **Thao tác 5 - Xem Vòng Tròn Đổi Đồ 3 Chiều & Đăng Ký Nhu Cầu Mới:**
   - Bấm vào menu **"Trao Đổi Đồ AI"** (hoặc truy cập `http://localhost:8000/pages/barter-graph.html`).
   - Xem sơ đồ đồ thị 3 sinh viên trao đổi chéo xoay quanh Trạm Hub CS1.
   - Bấm **"Quét Lại Chu Trình AI"**: Hệ thống sẽ gọi trực tiếp sang FastAPI giải thuật toán Johnson và hiển thị bảng Ma Trận Bù Trừ Tiền Mặt với tổng chênh lệch cân bằng tuyệt đối = 0đ (Zero-Sum).
   - Bấm **"Đăng Ký Nhu Cầu Đổi Đồ Của Bạn"**: Nhập đồ đang có và đồ muốn nhận để nạp thêm cạnh vào đồ thị.

6. **Thao tác 6 - Xem Tiến Trình Ký Quỹ, Giải Ngân & Dynamic QR TOTP 30s:**
   - Bấm vào menu **"Đơn Ký Quỹ Escrow"** (hoặc truy cập `http://localhost:8000/pages/escrow-order.html`).
   - Quan sát Stepper 7 bước theo dõi dòng tiền đóng băng và vị trí lưu kho tại ô tủ `LOCKER-M-01`.
   - Xem đồng hồ đếm ngược và mã Dynamic QR tự động xoay mới mỗi 30 giây kèm mã băm bảo mật HMAC-SHA256.
   - Bấm nút **"Hài Lòng & Giải Ngân"**: Hệ thống chuyển bước sang Hoàn tất (RELEASED) và tự động cộng +5 Điểm Uy Tín cho cả người mua và người bán.

7. **Thao tác 7 - Xem Cổng Quản Lý Nhân Viên Trạm Hub Đoàn Trường:**
   - Bấm vào menu **"Trạm Hub Staff"** (hoặc truy cập `http://localhost:8000/staff/`).
   - Xem giao diện kiểm soát trạng thái các ngăn tủ Locker (LOCKER-S-01, LOCKER-M-01,...).
   - Thử bấm **"Người Bán Gửi Đồ (Check-in)"**: Hệ thống gán vào ô tủ trống và đổi trạng thái tủ sang màu đỏ `Đang chứa hàng` ngay lập tức.
   - Thử bấm **"Người Mua Nhận Đồ (Check-out)"**: Hệ thống mở tủ và giải phóng ô tủ về màu xanh `Đang trống`.
   - Có thể bật Camera WebRTC thật của thiết bị để quét mã QR thực tế.

8. **Thao tác 8 - Chuyển Đổi Tài Khoản Sinh Viên (Auth Context Switcher):**
   - Trên thanh Navbar, bấm vào thẻ thông tin sinh viên góc trên bên phải (ví dụ: `Nguyễn Văn An - 520 Điểm`).
   - Chọn chuyển đổi sang bạn *Trần Thị Bích* (480 điểm) hoặc *Lê Hoàng Cường* (390 điểm).
   - Giao diện lập tức đồng bộ lại điểm uy tín, số dư ví và quyền quản trị tương ứng.
