# TÀI LIỆU KỸ THUẬT: MÔ HÌNH TOÁN HỌC & GIẢI THUẬT HỆ THỐNG
> **Hệ thống thương mại điện tử giao dịch & trao đổi hàng hóa sinh viên O2O & AI (HUNRE E-Commerce)**  
> **Khoa Công nghệ Thông tin — Trường Đại học Tài nguyên và Môi trường Hà Nội**  
> **Phiên bản:** 2.1.0 | **Phạm vi:** 5 Microservices cốt lõi, Gateway và Frontends

---

## 1. BÀI TOÁN GHÉP CẶP CHU TRÌNH TRAO ĐỔI ĐỒ 3 CHIỀU & BẢO TOÀN SỐ DƯ (AI BARTER GRAPH 2.0)

### 1.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `ai-engine` (FastAPI Microservice - Port 8005).
- **Tệp mã nguồn:** `services/ai-engine/app/services/graph_solver.py`.
- **API Endpoint:** `POST /api/v1/ai/barter/solve-cycles`.
- **Giao diện tương tác:** `frontend/student-portal/pages/barter-graph.html` (Canvas đồ thị chu trình 3 chiều và Bảng bù trừ tiền mặt Zero-sum).

### 1.2. Đặt bài toán khoa học
Trong kinh tế chia sẻ tại trường đại học, một sinh viên sở hữu vật phẩm $u$ muốn đổi lấy vật phẩm $v$, nhưng người giữ $v$ không có nhu cầu với $u$ mà lại cần vật phẩm $w$ của sinh viên thứ ba. Giao dịch song phương (2 bên) lập tức bế tắc. Mục tiêu của giải thuật là tìm kiếm chu trình trao đổi khép kín đa phương $S_1 \rightarrow S_2 \rightarrow S_3 \rightarrow \dots \rightarrow S_k \rightarrow S_1$ (với độ dài $k \in [2, 4]$) và giải bài toán bù trừ giá trị chênh lệch tiền mặt để bảo toàn số dư.

### 1.3. Biểu diễn toán học đồ thị có hướng có trọng số
Định nghĩa đồ thị có hướng $G = (V, E, W)$:
- **Tập đỉnh $V$:** Mỗi đỉnh $v_i$ đại diện cho một vật phẩm đăng ký trao đổi. Thuộc tính đỉnh gồm: $\text{Owner}(v_i)$ (mã sinh viên), $\text{Val}(v_i)$ (định giá theo VNĐ), $\text{Wish}(v_i)$ (tập từ khóa nhu cầu mong muốn nhận lại).
- **Tập cạnh $E$:** Cạnh có hướng $(u, v) \in E$ tồn tại khi và chỉ khi:
  $$\text{Owner}(u) \neq \text{Owner}(v) \quad \land \quad [\text{Title}(v) \in \text{Wish}(u) \lor \text{Category}(v) \in \text{Wish}(u) \lor \text{AcceptAny}(u) = \text{True}]$$
- **Hàm trọng số $W$:** $W(u, v)$ thể hiện độ chênh lệch giá trị giữa vật phẩm nhận về và vật phẩm chuyển giao:
  $$W(u, v) = \text{Val}(v) - \text{Val}(u)$$

### 1.4. Thuật toán tìm chu trình Johnson (Johnson's Cycle Finding)
Áp dụng thuật toán Johnson (1975) dựa trên tìm kiếm theo chiều sâu (DFS) kết hợp danh sách chặn (Blocked Set) để tìm toàn bộ chu trình đơn có độ dài từ 2 đến $L_{\max}$ ($L_{\max} = 3$):
- Độ phức tạp thời gian: $O((|V| + |E|)(c + 1))$ với $c$ là số chu trình đơn được tìm thấy.
- Với dữ liệu quy mô toàn trường ($|V| \approx 10^3, |E| \approx 5 \times 10^3$), thời gian phản hồi đạt dưới 15ms.

### 1.5. Định lý bảo toàn số dư tiền mặt (Zero-Sum Balance Invariant)
Xét chu trình $C = (v_1, v_2, \dots, v_k)$. Người sở hữu vật phẩm $v_i$ chuyển giao $v_i$ và nhận về vật phẩm $v_{prev}$ (với $prev = (i - 1 + k) \pmod k$). Khoản tiền chênh lệch $\Delta_i$ được xác định:
$$\Delta_i = \text{Val}(v_{prev}) - \text{Val}(v_i)$$

- Nếu $\Delta_i > 0$: Sinh viên nhận đồ có giá trị cao hơn đồ cho đi $\rightarrow$ Phải nộp bù $\Delta_i$ vào quỹ ký quỹ Smart Escrow.
- Nếu $\Delta_i < 0$: Sinh viên nhận đồ có giá trị thấp hơn đồ cho đi $\rightarrow$ Được nhận lại $|\Delta_i|$ từ quỹ ký quỹ Smart Escrow.
- Nếu $\Delta_i = 0$: Trao đổi ngang giá hoàn hảo.

**Định lý bảo toàn dòng tiền:**
$$\sum_{i=1}^{k} \Delta_i = \sum_{i=1}^{k} \left[ \text{Val}(v_{prev}) - \text{Val}(v_i) \right] = \sum_{i=1}^{k} \text{Val}(v_{prev}) - \sum_{i=1}^{k} \text{Val}(v_i) = 0$$

*Ý nghĩa:* Tổng tiền nộp bù của các sinh viên nhận đồ đắt hơn bằng chính xác tổng tiền chi trả cho các sinh viên nhận đồ rẻ hơn. Quỹ trung gian Escrow luôn cân bằng tài chính 100%, không phát sinh rủi ro thâm hụt.

---

## 2. GIẢI THUẬT THẨM ĐỊNH ĐỘ HAO MÒN & PHÂN HẠNG CHẤT LƯỢNG (COMPUTER VISION)

### 2.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `ai-engine` Microservice.
- **Tệp mã nguồn:** `services/ai-engine/app/services/cv_service.py`.
- **API Endpoint:** `POST /api/v1/ai/cv/inspect`.
- **Giao diện hiển thị:** Modal Thẩm định chất lượng khi sinh viên đăng bài tại `frontend/student-portal/index.html`.

### 2.2. Biểu diễn toán học xử lý tín hiệu hình ảnh
Ảnh đầu vào được chuẩn hóa sang không gian độ xám ma trận $I_{gray}(x, y)$ kích thước $W \times H$:
1. **Gradient vi phân không gian 2 chiều:** Tính đạo hàm riêng theo trục ngang $g_x$ và trục dọc $g_y$:
   $$g_x(x, y) = \frac{\partial I_{gray}}{\partial x}, \quad g_y(x, y) = \frac{\partial I_{gray}}{\partial y}$$
2. **Độ lớn Gradient tại mỗi điểm ảnh và điểm sắc nét trung bình toàn khung ảnh:**
   $$\|\nabla I(x, y)\| = \sqrt{g_x^2(x, y) + g_y^2(x, y)}, \quad S_{sharp} = \frac{1}{W \times H} \sum_{x=1}^{W} \sum_{y=1}^{H} \|\nabla I(x, y)\|$$
3. **Chỉ số bất đồng nhất màu sắc (đo lường vết ố vàng / trầy xước):**
   $$\sigma_{color} = \frac{1}{3} \sum_{c \in \{R, G, B\}} \sqrt{\frac{1}{W \cdot H} \sum_{x, y} \left( I(x, y, c) - \mu_c \right)^2}$$
4. **Hàm ước lượng tỷ lệ khiếm khuyết bề mặt:**
   $$D_{ratio} = \min \left( 0.35, \max \left( 0.01, \frac{100 - \min(3 \cdot S_{sharp}, 90)}{250} \right) \right)$$

### 2.3. Quy tắc phân lớp nhãn chất lượng (Condition Grade)
- $D_{ratio} < 0.03 \rightarrow$ **GRADE_S** (Độ mới 98% - 99%, Hệ số giá sàn đề xuất: 90% giá gốc).
- $0.03 \le D_{ratio} < 0.08 \rightarrow$ **GRADE_A** (Độ mới 90% - 95%, Hệ số giá sàn đề xuất: 75% giá gốc).
- $0.08 \le D_{ratio} < 0.15 \rightarrow$ **GRADE_B** (Độ mới 80% - 89%, Hệ số giá sàn đề xuất: 55% giá gốc).
- $D_{ratio} \ge 0.15 \rightarrow$ **GRADE_C** (Độ mới < 80%, Hệ số giá sàn đề xuất: 35% giá gốc).

---

## 3. THUẬT TOÁN BĂM CẢM NHẬN THỊ GIÁC (dHash) PHÁT HIỆN ẢNH MẠNG CHỐNG GIAN LẬN

### 3.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `ai-engine` Microservice.
- **Tệp mã nguồn:** `services/ai-engine/app/services/anti_fraud.py`.
- **API Endpoint:** `POST /api/v1/ai/anti-fraud/check`.
- **Chức năng:** Tự động phát hiện ảnh tải từ Shopee, Lazada, Tiki hoặc ảnh chụp màn hình đăng bán ảo.

### 3.2. Thuật toán Difference Hashing 64-bit
1. **Thu nhỏ kích thước (Downsampling):** Thu nhỏ ảnh về kích thước cố định $(N + 1) \times N$ với $N = 8$, tức ma trận $9 \times 8 = 72$ pixels bằng thuật toán nội suy Lanczos.
2. **Chuyển đổi sang ảnh xám (Grayscale):** Loại bỏ độ chói màu sắc, giữ lại cường độ sáng.
3. **So sánh vi phân gradient hàng ngang:** So sánh độ sáng giữa 2 điểm ảnh liền kề theo từng hàng:
   $$B(r, c) = \begin{cases} 1 & \text{nếu } P(r, c) > P(r, c + 1) \\ 0 & \text{nếu } P(r, c) \le P(r, c + 1) \end{cases} \quad \forall r \in [0, 7], c \in [0, 7]$$
4. **Tạo chữ ký số Hexadecimal 16 ký tự:** 64 bit nhị phân được gom thành 8 bytes và chuyển thành chuỗi 16 ký tự Hex.
5. **Khoảng cách Hamming và nhận dạng ảnh catalog:** Độ sai khác giữa 2 ảnh được đo bằng khoảng cách Hamming:
   $$D_H(H_1, H_2) = \sum_{k=1}^{64} \left( b_{1, k} \oplus b_{2, k} \right)$$
   Nếu $D_H \le 5$, hai ảnh được xác định là trùng lặp. Đồng thời, bộ lọc phát hiện tỷ lệ kích thước catalog vuông chuẩn ($800 \times 800, 1000 \times 1000, 1200 \times 1200$) kết hợp cảnh báo yêu cầu sinh viên chụp ảnh thực tế.

---

## 4. MÔ HÌNH SUY GIẢM HÀM MŨ ĐỊNH GIÁ TỰ ĐỘNG THEO THỜI GIAN (TIME-DECAY PRICING)

### 4.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `product-service` (Cronjob) và `ai-engine` (API).
- **Tệp mã nguồn:** `services/product-service/app/Services/TimeDecayPricingService.php` và `price_agent.py`.
- **API Endpoint:** `POST /api/v1/ai/pricing/decay`.
- **Chức năng:** Tự động giảm giá đồ dùng học tập cần thanh lý gấp cuối kỳ theo thời gian thực mà không bao giờ dưới Giá sàn.

### 4.2. Công thức toán học phân rã giá trị
Hệ thống mô hình hóa quá trình giảm giá theo hàm phân rã liên tục với chu kỳ bán rã (Exponential Half-Life Decay):
$$P(t) = P_{floor} + (P_{orig} - P_{floor}) \cdot e^{-\lambda t}$$

Trong đó:
- $P(t)$: Giá niêm yết tại thời điểm $t$ giờ sau khi đăng bán.
- $P_{orig}$: Mức giá khởi điểm ban đầu do sinh viên niêm yết.
- $P_{floor}$: Mức giá sàn tối thiểu do người bán thiết lập để bảo toàn vốn.
- $t_{1/2}$: Thời gian bán rã mặc định là 72 giờ (3 ngày). Hằng số suy giảm $\lambda = \frac{\ln(2)}{t_{1/2}} \approx 0.009627$.
- **Bất biến biên (Boundary Invariant):** Khi $t \to \infty$, $P(t) \to P_{floor}$ và $\forall t \ge 0, P(t) \ge P_{floor}$.

---

## 5. GIẢI THUẬT ĐÀM PHÁN THƯƠNG LƯỢNG GIÁ ĐỘNG DỰA TRÊN ĐIỂM UY TÍN (AI PRICE NEGOTIATOR)

### 5.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `ai-engine` Microservice.
- **Tệp mã nguồn:** `services/ai-engine/app/services/price_agent.py`.
- **API Endpoint:** `POST /api/v1/ai/pricing/negotiate`.
- **Giao diện hiển thị:** Modal **"Trả Giá AI"** tại trang chủ chợ sinh viên `frontend/student-portal/index.html`.

### 5.2. Mô hình cây quyết định đa tiêu chí
Cho người mua đề xuất mức giá $P_{offer}$ và có Điểm Uy Tín $T \in [0, 1000]$. Giá niêm yết hiện tại là $P_{curr}$ và giá sàn người bán là $P_{floor}$. Tỷ số đề xuất giá tương đối và ngưỡng chấp nhận linh hoạt được xác định:
$$\rho = \frac{P_{offer} - P_{floor}}{P_{curr} - P_{floor} + 10^{-5}}, \quad \theta_{accept}(T) = 0.5 - \frac{T}{2000}$$

**Quy tắc ra quyết định tự động của AI Agent:**
1. **Nếu $P_{offer} \ge P_{curr}$:** Chấp thuận ngay lập tức (`DECISION = ACCEPT`).
2. **Nếu $P_{offer} < P_{floor}$:** Mức giá dưới giá sàn. Nếu $T \ge 600$ (Hạng Vàng/Kim Cương), AI đưa ra mức giá thỏa hiệp ưu đãi $P_{counter} = P_{floor} \times 1.03$ (`COUNTER_OFFER`); ngược lại từ chối (`REJECT`).
3. **Nếu $P_{floor} \le P_{offer} < P_{curr}$:** Nếu $\rho \ge \theta_{accept}(T) \rightarrow \text{ACCEPT}$; ngược lại đề xuất giá trung gian $P_{counter} = \text{Round}\left(\frac{P_{offer} + P_{curr}}{2}, -3\right)$.

---

## 6. THUẬT TOÁN XÁC THỰC MÃ QR ĐỘNG DYNAMIC QR TOTP XOAY VÒNG 30S (HMAC-SHA256)

### 6.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `hub-service` (Logistics Service - Port 8004).
- **Tệp mã nguồn:** `services/hub-service/app/Services/DynamicQREngine.php`.
- **API Endpoint:** `GET /api/v1/hub/lockers`.
- **Giao diện hiển thị:** Mã QR xoay vòng 30s tại `pages/escrow-order.html` và máy quét PWA của thủ kho tại `frontend/hub-staff-portal/index.html`.

### 6.2. Cơ chế mật mã học HMAC-SHA256 theo cửa sổ thời gian (RFC 6238)
Nhằm ngăn chặn triệt để hành vi chụp trộm màn hình để lấy đồ tại Trạm Hub, mã QR được tạo động theo chu kỳ 30 giây:
1. **Cửa sổ thời gian (Time Window):** $W(t) = \left\lfloor \frac{t}{T_{step}} \right\rfloor$ với $T_{step} = 30$ giây.
2. **Chuỗi thông điệp xác thực:**
   $$M(t) = \text{OrderCode} \parallel \text{UserId} \parallel \text{Role} \parallel W(t)$$
   *(Ký hiệu $\parallel$ là phép nối chuỗi dữ liệu).*
3. **Chữ ký số xác nhận:**
   $$\tau(t) = \text{Truncate}_{16}\left( \text{HMAC-SHA256}\left( K_{secret}, M(t) \right) \right)$$
4. **Cơ chế xác thực chịu lỗi trễ đồng hồ:** Máy quét tại Trạm Hub giải mã và kiểm tra $\tau(t)$ với $W(t)$ và $W(t) - 1$ (cửa sổ trễ 30 giây) thông qua hàm so sánh bất biến thời gian `hash_equals()` nhằm chống lại tấn công vét cạn (Timing Attack).

---

## 7. MÔ HÌNH MÁY TRẠNG THÁI HỮU HẠN & ĐIỀU PHỐI GIAO DỊCH PHÂN TÁN SAGA (SMART ESCROW)

### 7.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `escrow-service` (Escrow & Payment Microservice - Port 8003).
- **Tệp mã nguồn:** `services/escrow-service/app/Services/EscrowSagaOrchestrator.php`.
- **API Endpoint:** `GET /api/v1/escrow/transactions`, `POST /api/v1/escrow/saga/advance`.
- **Giao diện hiển thị:** Thanh tiến trình Stepper 7 bước tại `frontend/student-portal/pages/escrow-order.html`.

### 7.2. Định nghĩa máy trạng thái hữu hạn Automaton 7 trạng thái
Tiến trình ký quỹ được mô hình hóa thành một bộ máy trạng thái hữu hạn xác định $M = (S, \Sigma, \delta, s_0, F)$:
- Tập 7 trạng thái: $S = \{\text{INITIATED}, \text{ESCROW\_LOCKED}, \text{STORED\_AT\_HUB}, \text{INSPECTING}, \text{RELEASED}, \text{DISPUTED}, \text{REFUNDED}\}$.
- Trạng thái khởi đầu: $s_0 = \text{INITIATED}$.
- Tập trạng thái kết thúc: $F = \{\text{RELEASED}, \text{REFUNDED}\}$.

| Trạng thái hiện tại ($s$) | Sự kiện kích hoạt ($e$) | Điều kiện kiểm tra (Guard) | Trạng thái kế tiếp ($s'$) | Hành động Saga đền bù |
| :--- | :--- | :--- | :--- | :--- |
| **INITIATED** | `PAY_DEPOSIT` | Tiền vào tài khoản trung gian | **ESCROW_LOCKED** | Hủy đơn, hoàn cọc |
| **ESCROW_LOCKED** | `SELLER_CHECKIN` | Thủ kho quét mã QR hợp lệ | **STORED_AT_HUB** | Mở tủ trả đồ về người bán |
| **STORED_AT_HUB** | `BUYER_CHECKOUT` | Người mua quét mã nhận đồ | **INSPECTING** | Khóa tủ giữ nguyên vị trí |
| **INSPECTING** | `BUYER_SATISFIED` | Người mua bấm xác nhận hài lòng | **RELEASED** | Giải ngân tiền cho người bán |
| **INSPECTING** | `RAISE_DISPUTE` | Hàng vỡ hỏng / sai mô tả tại Hub | **DISPUTED** | Lập biên bản trung gian |
| **DISPUTED** | `ADMIN_RESOLVE` | Thủ kho xác nhận hàng không đạt | **REFUNDED** | Hoàn tiền 100% người mua |

---

## 8. GIẢI THUẬT ĐÁNH GIÁ TÍN NHIỆM & TÍNH ĐIỂM UY TÍN SINH VIÊN (TRUST SCORE ENGINE)

### 8.1. Chức năng tương ứng trong hệ thống
- **Phân hệ phụ trách:** `auth-service` (Auth & Identity Microservice - Port 8001).
- **Tệp mã nguồn:** `services/auth-service/app/Services/TrustScoreService.php`.
- **API Endpoint:** `GET /api/v1/auth/users/trust-score`.
- **Giao diện hiển thị:** Huy hiệu Điểm Uy Tín gắn liền tài khoản sinh viên trên thanh Navbar toàn hệ thống.

### 8.2. Hàm tích lũy điểm hành vi rời rạc có chặn biên
Điểm uy tín của sinh viên tại thời điểm $n + 1$ là một hàm tích lũy có chặn trên và chặn dưới trong không gian $T \in [0, 1000]$:
$$T_{n+1} = \max \left( 0, \min \left( 1000, T_n + \sum_{j} w_j \cdot E_j \right) \right)$$

Trong đó các trọng số biến cố hành vi được định lượng cụ thể:
- $w_1 = +5$: Hoàn tất giao dịch O2O đúng hẹn tại Trạm Hub CS1.
- $w_2 = +2$: Nhận đánh giá 5 sao từ sinh viên đối tác.
- $w_3 = -15$: Quá hạn 48h không mang đồ đến gửi tại tủ Trạm Hub.
- $w_4 = -20$: Tự ý hủy kèo sau khi Barter Graph đã ghép cặp thành công.
- $w_5 = -30$: Cố tình khai gian tình trạng sản phẩm bị camera Hub phát hiện.

| Thang Điểm Uy Tín | Phân Hạng Sinh Viên (Tier) | Quyền Lợi & Đặc Quyền Trong Hệ Thống |
| :--- | :--- | :--- |
| **800 - 1000 Điểm** | **KIM CƯƠNG** | Bảo chứng uy tín 100%, được phép nhận hàng trước không cần cọc tiền. |
| **600 - 799 Điểm** | **VÀNG** | Ưu tiên số 1 khi quét chu trình Barter Graph, giảm 50% tiền cọc Escrow. |
| **400 - 599 Điểm** | **BẠC (Tiêu chuẩn)** | Hưởng đầy đủ tính năng mua bán, đổi đồ và trả giá AI thông thường. |
| **200 - 399 Điểm** | **ĐỒNG** | Phải đặt cọc 100% giá trị món đồ khi tham gia ký quỹ tại Trạm Hub. |
| **< 200 Điểm** | **CẢNH BÁO** | Hạn chế quyền đổi đồ, bắt buộc xác minh lại thẻ sinh viên tại Đoàn Trường. |

---

## 9. BẢNG TỔNG HỢP ÁNH XẠ GIẢI THUẬT & PHÂN HỆ CHỨC NĂNG

| STT | Tên Thuật Toán / Mô Hình | Microservice Phụ Trách | API Endpoint Cung Cấp | Chức Năng Nghiệp Vụ Cụ Thể |
| :---: | :--- | :--- | :--- | :--- |
| **1** | Johnson's Directed Cycle & Zero-Sum | `ai-engine` (Port 8005) | `POST /api/v1/ai/barter/solve-cycles` | Ghép vòng tròn đổi đồ 3 chiều và tính toán ma trận bù trừ tiền mặt |
| **2** | Spatial Gradient & HSV Color Defect | `ai-engine` (Port 8005) | `POST /api/v1/ai/cv/inspect` | Thị giác máy tính đo độ hao mòn, phân hạng Grade S/A/B/C |
| **3** | Difference Hashing (dHash 64-bit) | `ai-engine` (Port 8005) | `POST /api/v1/ai/anti-fraud/check` | Chống ảnh mạng catalog Shopee/Lazada, xác thực ảnh sinh viên |
| **4** | Exponential Half-Life Decay Pricing | `product-service` (8002) | `POST /api/v1/ai/pricing/decay` | Tự động giảm giá theo giờ thanh lý giáo trình cuối kỳ |
| **5** | Multi-Criteria Price Negotiator Agent | `ai-engine` (Port 8005) | `POST /api/v1/ai/pricing/negotiate` | Trợ lý AI tự động đàm phán giá theo Điểm Uy Tín 24/7 |
| **6** | HMAC-SHA256 Dynamic QR TOTP (30s) | `hub-service` (Port 8004) | `GET /api/v1/hub/lockers` | Sinh và giải mã QR xoay 30s chống chụp trộm màn hình tại Hub |
| **7** | Distributed Saga 7-State FSM | `escrow-service` (8003) | `POST /api/v1/escrow/saga/advance` | Đóng băng tiền cọc ký quỹ và giải ngân khi người mua hài lòng |
| **8** | Accumulative Trust Score Engine | `auth-service` (Port 8001) | `GET /api/v1/auth/users/trust-score` | Đánh giá tín nhiệm sinh viên HUNRE và phân cấp đặc quyền |
