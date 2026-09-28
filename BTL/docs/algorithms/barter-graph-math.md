# MÔ HÌNH TOÁN HỌC & GIẢI THUẬT VÒNG TRÒN TRAO ĐỔI ĐỒ (AI BARTER GRAPH 2.0)
> **Tài liệu phục vụ Báo cáo Nghiên cứu Khoa học & Khóa Luận Tốt Nghiệp**  
> **Tác giả:** Đội ngũ Nghiên cứu HUNRE E-Commerce

---

## 1. ĐẶT BÀI TOÁN KHOA HỌC
Trong nền kinh tế chia sẻ tại trường đại học, một sinh viên sở hữu tài sản $A$ muốn đổi lấy tài sản $B$, nhưng người giữ $B$ lại không có nhu cầu với $A$ mà lại cần tài sản $C$. Mô hình trao đổi 2 chiều truyền thống lập tức bế tắc.

Mục tiêu của giải thuật là:
1. **Phát hiện chu trình trao đổi khép kín đa chiều (Multi-Hop Cycle Detection):** Sinh viên $S_1 \rightarrow S_2 \rightarrow S_3 \rightarrow \dots \rightarrow S_n \rightarrow S_1$.
2. **Giải bài toán không đồng nhất về giá trị:** Vì các món đồ trao đổi hiếm khi có giá trị bằng nhau tuyệt đối, hệ thống phải giải ma trận bù trừ dòng tiền mặt thông qua **Smart Escrow** để đảm bảo không ai bị thiệt hại và tổng số dư của hệ thống luôn được bảo toàn.

---

## 2. BIỂU DIỄN ĐỒ THỊ (GRAPH FORMULATION)

Định nghĩa đồ thị có hướng có trọng số:
$$G = (V, E, W)$$

Trong đó:
- $V = \{v_1, v_2, \dots, v_n\}$: Tập hợp các đỉnh, mỗi đỉnh đại diện cho một sản phẩm được đăng ký trao đổi. Thuộc tính của đỉnh $v_i$ bao gồm:
  - $\text{Owner}(v_i)$: Mã định danh sinh viên sở hữu.
  - $\text{Value}(v_i)$: Định giá của món đồ $v_i$ theo VNĐ.
  - $\text{Wishlist}(v_i)$: Danh mục hoặc từ khóa món đồ mong muốn nhận về.
- $E \subseteq V \times V$: Tập hợp các cạnh có hướng. Cạnh $(u, v) \in E$ tồn tại khi và chỉ khi:
  $$\text{Owner}(u) \neq \text{Owner}(v) \quad \land \quad v \text{ thỏa mãn } \text{Wishlist}(u)$$
- $W: E \rightarrow \mathbb{R}$: Hàm trọng số trên cạnh, thể hiện sự chênh lệch giá trị:
  $$W(u, v) = \text{Value}(v) - \text{Value}(u)$$

---

## 3. THUẬT TOÁN TÌM CHU TRÌNH (CYCLE DETECTION)

Chúng ta áp dụng **Thuật toán Johnson (1975)** kết hợp với hàm giới hạn độ dài chu trình $L \in [2, 4]$ (vì trong thực tế sinh viên, chu trình dài hơn 4 bước sẽ làm tăng độ phức tạp trong việc hẹn gặp tại Trạm Hub).

### Giới hạn độ phức tạp:
- Độ phức tạp thời gian: $O((|V| + |E|)(c + 1))$ với $c$ là số chu trình đơn được tìm thấy.
- Với mạng lưới quy mô trường đại học ($|V| \approx 10^3, |E| \approx 5 \times 10^3$), thời gian phản hồi của Python FastAPI đạt **dưới 15ms**.

---

## 4. MA TRẬN BÙ TRỪ TIỀN MẶT & ĐỊNH LÝ BẢO TOÀN SỐ DƯ (ZERO-SUM CONSERVATION)

Xét một chu trình $C = (v_1, v_2, \dots, v_k)$ có độ dài $k$.
Trong chu trình này:
- Sinh viên sở hữu $v_i$ sẽ **cho đi** món đồ $v_i$.
- Sinh viên sở hữu $v_i$ sẽ **nhận về** món đồ $v_{prev}$ (với $prev = (i - 1 + k) \pmod k$).

### Khoản chênh lệch tiền mặt cần bù trừ $\Delta_i$:
$$\Delta_i = \text{Value}(v_{prev}) - \text{Value}(v_i)$$

- Nếu $\Delta_i > 0$: Giá trị đồ nhận về lớn hơn đồ cho đi $\rightarrow$ Sinh viên $i$ **phải nạp bù $\Delta_i$** vào ví Smart Escrow tại Trạm Hub.
- Nếu $\Delta_i < 0$: Giá trị đồ nhận về nhỏ hơn đồ cho đi $\rightarrow$ Sinh viên $i$ **được nhận lại $|\Delta_i|$** từ ví Smart Escrow khi nhận đồ.
- Nếu $\Delta_i = 0$: Trao đổi ngang giá hoàn hảo không cần bù trừ.

### Định lý bảo toàn dòng tiền (Zero-Sum Balance Invariant):
$$\sum_{i=1}^{k} \Delta_i = \sum_{i=1}^{k} \left( \text{Value}(v_{prev}) - \text{Value}(v_i) \right) = \sum_{i=1}^{k} \text{Value}(v_{prev}) - \sum_{i=1}^{k} \text{Value}(v_i) = 0$$

> **Ý nghĩa khoa học:** Tổng số tiền nạp bù của các sinh viên nhận đồ đắt hơn luôn bằng chính xác tổng số tiền giải ngân cho các sinh viên nhận đồ rẻ hơn. Quỹ Smart Escrow không bị thâm hụt và hệ thống không chịu rủi ro tín dụng!
