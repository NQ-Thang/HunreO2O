# Course Registration System (CRS) - Microservices Architecture

**Người thực hiện:** Nguyễn Văn Chiến (NVC)

Hệ thống đăng ký môn học CRS (Course Registration System) là một ứng dụng Fullstack được xây dựng hoàn toàn dựa trên kiến trúc Microservices hiện đại, kết hợp với giao diện Frontend ReactJS. 

Dự án cung cấp luồng quy trình khép kín từ xác thực người dùng tập trung, định tuyến bảo mật cho tới giao tiếp liên dịch vụ (Inter-service Communication).

---

## 🚀 Cấu trúc hệ thống & Chức năng chính (Features)

Dự án bao gồm 5 module chính (4 Backend Services + 1 Frontend):

### 1. 🛡️ API Gateway (`api-gateway` - Cổng 8080)
- **Định tuyến (Routing)**: Chịu trách nhiệm làm "cửa ngõ" duy nhất, nhận mọi luồng request từ Frontend/Client và định tuyến (RewritePath) tới chính xác các service bên trong.
- **Bảo mật & CORS**: Cấu hình Global CORS cấp quyền truy cập cho Frontend (`http://localhost:5173`).
- **Global Filters**:
  - `AuthHeaderFilter`: Kiểm tra chặn bắt buộc phải có `Authorization: Bearer` trước khi cho phép đi sâu vào các service nghiệp vụ (trừ các public routes).
  - `ApiKeyFilter`: Xác thực API Key (`X-API-KEY`) dành riêng cho các đối tác thứ ba khi gọi các public endpoint.

### 2. 🔐 Authentication Service (`auth-service` - Cổng 8081)
- **Quản lý tài khoản**: Chứa bảng `app_user` lưu trữ thông tin đăng nhập và Role (`ADMIN`, `STUDENT`) với mật khẩu mã hóa an toàn bằng BCrypt.
- **Cấp phát JWT**: Sử dụng thư viện `JJWT 0.12.6` thế hệ mới nhất để mã hóa và cấp phát Token an toàn.
- **Data Seeder tự động**: Tự động sinh sẵn tài khoản mẫu để test hệ thống (`admin/admin123`, `student1/student123`).

### 3. 📚 Course Service (`course-service` - Cổng 8082)
- **Quản lý Môn học (CRUD)**: Đầy đủ các tác vụ lấy danh sách, thêm, sửa, xóa môn học.
- **Inter-service API**: Cung cấp endpoint nội bộ (`/internal/courses/`) để `registration-service` gọi sang trừ số chỗ, trả lại chỗ.
- **Bảo vệ bằng Spring Security**: Cấu hình Role-based Access Control (RBAC). Các thao tác thêm, sửa, xóa bắt buộc phải là quyền `ADMIN`.

### 4. 📝 Registration Service (`registration-service` - Cổng 8083)
- **Nghiệp vụ Đăng ký**: Sinh viên đăng ký hoặc hủy đăng ký lớp học. Hệ thống tự động kiểm tra xem sinh viên đã đăng ký môn đó chưa.
- **Giao tiếp liên dịch vụ (Inter-Service)**: Sử dụng `RestTemplate` (đã nâng cấp với `httpclient5` để hỗ trợ method `PATCH`) để gọi sang `course-service` nhằm cập nhật số lượng chỗ ngồi (còn lại) theo thời gian thực một cách an toàn.
- **Xử lý lỗi (Global Exception Handling)**: Bắt lỗi 400 Bad Request, 404 Not Found, 409 Conflict trả về mã lỗi JSON đồng bộ, đẹp mắt.

### 5. 💻 Frontend App (`crs-frontend` - Cổng 5173)
- **Công nghệ**: ReactJS + TypeScript + Vite. Cấu trúc thư mục chuyên nghiệp (`api`, `components`, `types`, `pages`, `context`).
- **Axios Configuration**: Tích hợp biến môi trường (`.env`) và định tuyến toàn bộ API calls qua 1 endpoint duy nhất của Gateway (`http://localhost:8080/api`).
- **An toàn kiểu dữ liệu (Type-Safety)**: Map chuẩn xác hoàn toàn 1:1 các Interface (Course, LoginRequest, Registration...) với các DTO của Backend.

---

## 🛠️ Hướng dẫn khởi chạy

### Yêu cầu môi trường
- Java 17+ (JDK)
- Node.js & npm (Phiên bản mới nhất)
- MySQL Server đang chạy (port `3306`), tạo sẵn password là `123456` (Cấu hình thay đổi trong file `application.properties` của từng service).

### Bước 1: Khởi động hệ thống Backend
Mở Terminal ở thư mục gốc của project và chạy lần lượt 4 service:
```bash
# Gateway (Chạy đầu tiên hoặc cuối cùng đều được)
cd api-gateway && ./mvnw spring-boot:run

# Auth Service
cd auth-service && ./mvnw spring-boot:run

# Course Service
cd course-service && ./mvnw spring-boot:run

# Registration Service
cd registration-service && ./mvnw spring-boot:run
```

### Bước 2: Khởi động Frontend
Mở một cửa sổ Terminal mới:
```bash
cd crs-frontend
npm install
npm run dev
```

Sau khi chạy xong, truy cập **[http://localhost:5173](http://localhost:5173)** trên trình duyệt để kiểm tra kết nối hệ thống!

---

## 🧪 Kịch bản Test (Postman)

Để phục vụ báo cáo, hệ thống có cung cấp sẵn các Test Case thông qua Postman:

1. **Test Lấy Token**: Gọi `POST http://localhost:8080/api/auth/login` với body `{"username": "student1", "password": "student123"}` -> Lấy Token.
2. **Test Xem danh sách môn**: Gọi `GET http://localhost:8080/api/courses` qua Gateway (Truyền Token vào Authorization).
3. **Test Quyền ADMIN**: Lấy Token của Admin (`admin/admin123`) và test gọi `POST http://localhost:8080/api/courses` để tạo môn.
4. **Test Đăng ký học (Inter-service)**: Gọi `POST http://localhost:8080/api/registrations` với `{"studentId": 1, "courseId": 2}`. Hệ thống sẽ tạo đăng ký và gọi nội bộ sang Course Service để trừ đi 1 số chỗ ngồi.

---

## 🏢 Hệ thống BTL: HUNRE E-Commerce O2O & AI Platform (Thư mục `/BTL`)

Dự án tích hợp hệ thống thương mại điện tử O2O kết hợp Trạm Hub thực địa và trí tuệ nhân tạo (AI) dành cho sinh viên HUNRE:
- **API Gateway (Nginx)**: Cổng `8000` (định tuyến toàn bộ dịch vụ).
- **Auth & Trust Score Service**: Cổng `8001` (chấm điểm uy tín sinh viên).
- **Product & Time-Decay Pricing Service**: Cổng `8002` (đấu giá ngược theo hàm suy giảm thời gian).
- **Escrow & Ledger Service**: Cổng `8003` (ký quỹ SAGA, ví tiền an toàn).
- **Hub Logistics & TOTP QR Service**: Cổng `8004` (tạo mã QR động 30s lấy đồ tại tủ Locker).
- **AI Engine (FastAPI)**: Cổng `8005` (thẩm định thị giác máy tính CV, giải thuật toán chu trình Barter Graph).
- **Frontend Sinh viên & Hub Staff**: Thư mục `BTL/frontend/`.
- **Tài liệu toán & thuật toán (PDF/Markdown)**: Thư mục `BTL/tailieu/` và `BTL/docs/`.

> Chi tiết kiến trúc và cách chạy xem tại file: [BTL/README.md](file:///d:/Intel/Project/crs-microservices/BTL/README.md).

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
