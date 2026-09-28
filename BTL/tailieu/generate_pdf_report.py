# -*- coding: utf-8 -*-
"""
Script tạo tài liệu PDF chuẩn học thuật cho Đồ án / Báo cáo NCKH:
"MÔ HÌNH TOÁN HỌC VÀ CÁC GIẢI THUẬT TRONG HỆ THỐNG HUNRE E-COMMERCE"
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Đăng ký font tiếng Việt chuẩn Windows (Times New Roman)
FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Times', os.path.join(FONT_DIR, 'times.ttf')))
pdfmetrics.registerFont(TTFont('Times-Bold', os.path.join(FONT_DIR, 'timesbd.ttf')))
pdfmetrics.registerFont(TTFont('Times-Italic', os.path.join(FONT_DIR, 'timesi.ttf')))
pdfmetrics.registerFont(TTFont('Times-BoldItalic', os.path.join(FONT_DIR, 'timesbi.ttf')))

class NumberedCanvas(canvas.Canvas):
    """Canvas đánh số trang chuyên nghiệp: 'Trang X / Y' và Header học thuật"""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        # Bỏ qua trang bìa (trang 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont('Times', 9)
        self.setFillColor(colors.HexColor('#4B5563'))

        # Header
        self.drawString(2.5 * cm, 28.3 * cm, "ĐẠI HỌC TÀI NGUYÊN VÀ MÔI TRƯỜNG HÀ NỘI — KHOA CÔNG NGHỆ THÔNG TIN")
        self.setStrokeColor(colors.HexColor('#D1D5DB'))
        self.setLineWidth(0.5)
        self.line(2.5 * cm, 28.1 * cm, 18.5 * cm, 28.1 * cm)

        # Footer
        self.line(2.5 * cm, 1.8 * cm, 18.5 * cm, 1.8 * cm)
        self.drawString(2.5 * cm, 1.4 * cm, "Báo cáo Mô hình Toán học & Thuật toán Hệ thống HUNRE E-Commerce")
        page_str = f"Trang {self._pageNumber} / {page_count}"
        self.drawRightString(18.5 * cm, 1.4 * cm, page_str)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles chuẩn văn bản học thuật Việt Nam
    style_cover_univ = ParagraphStyle(
        'CoverUniv',
        fontName='Times-Bold',
        fontSize=12,
        leading=16,
        alignment=1, # Căn giữa
        textColor=colors.HexColor('#1E3A8A'),
        textTransform='uppercase'
    )
    style_cover_sub = ParagraphStyle(
        'CoverSub',
        fontName='Times-Bold',
        fontSize=11,
        leading=15,
        alignment=1,
        textColor=colors.HexColor('#111827')
    )
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Times-Bold',
        fontSize=20,
        leading=26,
        alignment=1,
        textColor=colors.HexColor('#0F172A')
    )
    style_cover_subtitle = ParagraphStyle(
        'CoverSubTitle',
        fontName='Times-BoldItalic',
        fontSize=13,
        leading=18,
        alignment=1,
        textColor=colors.HexColor('#047857')
    )
    style_cover_meta = ParagraphStyle(
        'CoverMeta',
        fontName='Times',
        fontSize=12,
        leading=18,
        textColor=colors.HexColor('#1F2937')
    )
    style_cover_meta_b = ParagraphStyle(
        'CoverMetaB',
        fontName='Times-Bold',
        fontSize=12,
        leading=18,
        textColor=colors.HexColor('#1F2937')
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Times-Bold',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        fontName='Times-Bold',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#047857'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    style_h3 = ParagraphStyle(
        'Heading3_Custom',
        fontName='Times-BoldItalic',
        fontSize=11.5,
        leading=16,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Body_Custom',
        fontName='Times',
        fontSize=11.5,
        leading=16.5,
        textColor=colors.HexColor('#111827'),
        alignment=4, # Justify căn đều 2 bên
        spaceBefore=3,
        spaceAfter=4
    )
    style_body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        parent=style_body,
        fontName='Times-Bold'
    )
    style_body_italic = ParagraphStyle(
        'Body_Italic_Custom',
        parent=style_body,
        fontName='Times-Italic'
    )
    style_formula = ParagraphStyle(
        'Formula_Custom',
        fontName='Times-BoldItalic',
        fontSize=11.5,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Căn giữa
        spaceBefore=6,
        spaceAfter=6
    )
    style_code = ParagraphStyle(
        'Code_Custom',
        fontName='Times',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=2,
        spaceAfter=2
    )
    style_th = ParagraphStyle(
        'TH_Custom',
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.white,
        alignment=1
    )
    style_td = ParagraphStyle(
        'TD_Custom',
        fontName='Times',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#111827')
    )
    style_td_center = ParagraphStyle(
        'TD_Center_Custom',
        fontName='Times',
        fontSize=10,
        leading=13,
        alignment=1,
        textColor=colors.HexColor('#111827')
    )

    story = []

    # =========================================================================
    # TRANG BÌA HỌC THUẬT (STANDARD ACADEMIC COVER PAGE)
    # =========================================================================
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("BỘ TÀI NGUYÊN VÀ MÔI TRƯỜNG", style_cover_univ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("TRƯỜNG ĐẠI HỌC TÀI NGUYÊN VÀ MÔI TRƯỜNG HÀ NỘI", style_cover_univ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("KHOA CÔNG NGHỆ THÔNG TIN", style_cover_sub))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="60%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=20))
    story.append(Spacer(1, 25 * mm))

    story.append(Paragraph("BÁO CÁO CHUYÊN ĐỀ KHOA HỌC", style_cover_sub))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("MÔ HÌNH TOÁN HỌC VÀ CÁC GIẢI THUẬT CỐT LÕI TRONG NỀN TẢNG THƯƠNG MẠI ĐIỆN TỬ O2O & AI CHO SINH VIÊN HUNRE", style_cover_title))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Hệ Thống HUNRE E-Commerce: Barter Graph 2.0, Computer Vision, Smart Escrow & Security TOTP", style_cover_subtitle))

    story.append(Spacer(1, 40 * mm))

    # Bảng thông tin sinh viên / giảng viên
    meta_table_data = [
        [Paragraph("Giảng viên hướng dẫn:", style_cover_meta_b), Paragraph("Bộ môn Công nghệ phần mềm", style_cover_meta)],
        [Paragraph("Chuyên ngành:", style_cover_meta_b), Paragraph("Công nghệ Thông tin", style_cover_meta)],
        [Paragraph("Đơn vị thực hiện:", style_cover_meta_b), Paragraph("Nhóm Nghiên cứu & Phát triển Hệ thống HUNRE", style_cover_meta)],
        [Paragraph("Cơ sở đào tạo:", style_cover_meta_b), Paragraph("Đại học Tài nguyên và Môi trường Hà Nội", style_cover_meta)],
        [Paragraph("Hà Nội — Năm thực hiện:", style_cover_meta_b), Paragraph("2026", style_cover_meta)]
    ]
    t_meta = Table(meta_table_data, colWidths=[6.0 * cm, 9.5 * cm])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_meta)

    story.append(PageBreak())

    # =========================================================================
    # LỜI MỞ ĐẦU & MỤC LỤC
    # =========================================================================
    story.append(Paragraph("MỤC LỤC TỔNG HỢP NỘI DUNG BÁO CÁO", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))
    
    toc_data = [
        [Paragraph("Phần", style_th), Paragraph("Tên Thuật Toán / Bài Toán Khoa Học", style_th), Paragraph("Phân Hệ Chức Năng Ứng Dụng", style_th), Paragraph("Trang", style_th)],
        [Paragraph("1", style_td_center), Paragraph("Bài toán ghép cặp chu trình trao đổi đồ 3 chiều & Ma trận bù trừ dòng tiền Zero-sum", style_td), Paragraph("AI Barter Graph Solver (FastAPI)", style_td), Paragraph("3", style_td_center)],
        [Paragraph("2", style_td_center), Paragraph("Giải thuật thẩm định độ hao mòn, khuyết tật và dán nhãn Condition Grade bằng Computer Vision", style_td), Paragraph("AI CV Inspection Service", style_td), Paragraph("5", style_td_center)],
        [Paragraph("3", style_td_center), Paragraph("Thuật toán băm cảm nhận thị giác dHash nhận dạng ảnh mạng và chống gian lận thương mại", style_td), Paragraph("AI Anti-Fraud Verification", style_td), Paragraph("7", style_td_center)],
        [Paragraph("4", style_td_center), Paragraph("Mô hình suy giảm hàm mũ định giá tự động theo thời gian (Time-decay Pricing / Dutch Auction)", style_td), Paragraph("Product Service & Price Agent", style_td), Paragraph("8", style_td_center)],
        [Paragraph("5", style_td_center), Paragraph("Giải thuật đàm phán thương lượng giá động dựa trên Điểm Uy Tín sinh viên (Dynamic Negotiator)", style_td), Paragraph("AI Intelligent Price Agent", style_td), Paragraph("9", style_td_center)],
        [Paragraph("6", style_td_center), Paragraph("Thuật toán sinh và giải mã mã QR động xoay vòng 30s Dynamic QR TOTP với HMAC-SHA256", style_td), Paragraph("O2O Physical Hub Service", style_td), Paragraph("11", style_td_center)],
        [Paragraph("7", style_td_center), Paragraph("Mô hình máy trạng thái hữu hạn (FSM) và điều phối giao dịch phân tán Saga 7 trạng thái", style_td), Paragraph("Smart Escrow Orchestrator", style_td), Paragraph("12", style_td_center)],
        [Paragraph("8", style_td_center), Paragraph("Giải thuật tính toán và phân hạng Điểm Uy Tín sinh viên theo quá trình (Trust Score Engine)", style_td), Paragraph("Auth & Identity Service", style_td), Paragraph("14", style_td_center)],
    ]
    t_toc = Table(toc_data, colWidths=[1.2 * cm, 7.8 * cm, 5.5 * cm, 1.5 * cm])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph("LỜI MỞ ĐẦU", style_h1))
    story.append(Paragraph(
        "Trong bối cảnh chuyển đổi số giáo dục đại học và kinh tế chia sẻ, nhu cầu luân chuyển đồ dùng học tập, giáo trình chuyên ngành và thiết bị thí nghiệm giữa các thế hệ sinh viên tại Trường Đại học Tài nguyên và Môi trường Hà Nội (HUNRE) là rất lớn. Tuy nhiên, các phương thức giao dịch truyền thống qua mạng xã hội đang bộc lộ nhiều điểm nghẽn nghiêm trọng: nguy cơ lừa đảo tiền cọc, hiện tượng bùng hẹn (bom hàng), chất lượng đồ cũ không minh bạch và sự bế tắc khi hai bên không có nhu cầu trao đổi trực diện 2 chiều.",
        style_body
    ))
    story.append(Paragraph(
        "Báo cáo này trình bày cơ sở toán học chặt chẽ và thiết kế giải thuật chi tiết của 8 mô hình cốt lõi cấu thành nên hệ thống thương mại điện tử sinh viên HUNRE E-Commerce. Mỗi thuật toán được đặc tả từ bài toán thực tế, không gian toán học, mã giả thuật toán, độ phức tạp thời gian/không gian, cơ chế bảo toàn số dư và ánh xạ chính xác vào các phân hệ Microservices đang vận hành của đề tài.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # BÀI TOÁN 1: BARTER GRAPH 2.0 & JOHNSON'S CYCLE DETECTION
    # =========================================================================
    story.append(Paragraph("1. BÀI TOÁN GHÉP CẶP CHU TRÌNH TRAO ĐỔI ĐỒ 3 CHIỀU & BẢO TOÀN SỐ DƯ (AI BARTER GRAPH 2.0)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("1.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Thuật toán thuộc phân hệ <b>AI Engine Microservice</b> (Port 8005, file <code>services/ai-engine/app/services/graph_solver.py</code>), được tích hợp API tại Endpoint <code>POST /api/v1/ai/barter/solve-cycles</code> và trực quan hóa tương tác tại giao diện <code>frontend/student-portal/pages/barter-graph.html</code>.",
        style_body
    ))

    story.append(Paragraph("1.2. Phát biểu bài toán khoa học", style_h2))
    story.append(Paragraph(
        "Cho tập hợp $N$ sinh viên, mỗi sinh viên sở hữu một vật phẩm $u$ và mong muốn đổi lấy một vật phẩm thuộc danh mục hoặc từ khóa $W$. Trong hầu hết các trường hợp, quan hệ trao đổi 2 chiều $A \\leftrightarrow B$ không tồn tại do sự bất đối xứng về nhu cầu. Bài toán đặt ra là tìm chu trình trao đổi có hướng khép kín $S_1 \\rightarrow S_2 \\rightarrow S_3 \\rightarrow \\dots \\rightarrow S_k \\rightarrow S_1$ có độ dài $k \\in [2, 4]$, đồng thời giải quyết bài toán không đồng nhất về giá trị định giá giữa các vật phẩm thông qua ma trận bù trừ dòng tiền mặt.",
        style_body
    ))

    story.append(Paragraph("1.3. Mô hình toán học và biểu diễn đồ thị", style_h2))
    story.append(Paragraph(
        "Định nghĩa đồ thị có hướng có trọng số $G = (V, E, W)$, trong đó:",
        style_body
    ))
    story.append(Paragraph("• $V = \\{v_1, v_2, \\dots, v_n\\}$: Tập hợp các đỉnh, mỗi đỉnh $v_i$ đại diện cho một vật phẩm đăng ký trao đổi. Thuộc tính đỉnh bao gồm: $\\text{Owner}(v_i)$ (mã sinh viên), $\\text{Val}(v_i)$ (định giá theo VNĐ), $\\text{Wish}(v_i)$ (tập từ khóa nhu cầu).", style_body))
    story.append(Paragraph("• $E \\subseteq V \\times V$: Tập hợp cạnh có hướng. Cạnh $(u, v) \\in E$ tồn tại khi và chỉ khi:", style_body))
    story.append(Paragraph("$$\\text{Owner}(u) \\neq \\text{Owner}(v) \\quad \\land \\quad (\\text{Title}(v) \\in \\text{Wish}(u) \\lor \\text{Category}(v) \\in \\text{Wish}(u))$$", style_formula))
    story.append(Paragraph("• $W: E \\rightarrow \\mathbb{R}$: Trọng số đại diện cho độ chênh lệch giá trị khi chuyển giao:", style_body))
    story.append(Paragraph("$$W(u, v) = \\text{Val}(v) - \\text{Val}(u)$$", style_formula))

    story.append(Paragraph("1.4. Thuật toán tìm chu trình đơn (Johnson's Algorithm)", style_h2))
    story.append(Paragraph(
        "Hệ thống áp dụng <b>Thuật toán Johnson (1975)</b> để liệt kê toàn bộ chu trình đơn có hướng (Elementary Directed Cycles) dựa trên kỹ thuật tìm kiếm theo chiều sâu (DFS) kết hợp danh sách chặn (Blocked Set) để tránh duyệt trùng lặp:",
        style_body
    ))
    
    pseudo_johnson = [
        [Paragraph("<b>Mã giả Thuật toán Johnson's Cycle Finding kết hợp Lọc Chiều Dài:</b>", style_th)],
        [Paragraph(
            "<b>Input:</b> Đồ thị có hướng G = (V, E), Ngưỡng chiều dài tối đa L_max = 3 (hoặc 4)<br/>"
            "<b>Output:</b> Tập hợp các chu trình khép kín C = {c_1, c_2, ...}<br/>"
            "1. Xác định các thành phần liên thông mạnh (SCC) của G: {SCC_1, SCC_2, ...}<br/>"
            "2. Với mỗi thành phần SCC_k có ít nhất 2 đỉnh:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;a. Chọn đỉnh s có chỉ số nhỏ nhất trong SCC_k làm đỉnh gốc.<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;b. Khởi tạo blocked = [False] * |V|, B = {v: [] for v in V}, stack = []<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;c. Định nghĩa hàm Circuit(v):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f = False; push v vào stack; blocked[v] = True<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Với mỗi đỉnh kế tiếp w thuộc danh sách kề Adj[v]:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu w == s:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu 2 &le; len(stack) &le; L_max: Lưu lại chu trình stack; f = True<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ngược lại nếu not blocked[w]:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu Circuit(w): f = True<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu f == True: Unblock(v)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ngược lại: Với mỗi w thuộc Adj[v], thêm v vào B[w]<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Pop v khỏi stack; return f<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;d. Gọi Circuit(s), sau đó loại bỏ s khỏi G và lặp lại bước 2.",
            style_code
        )]
    ]
    t_pj = Table(pseudo_johnson, colWidths=[16.0 * cm])
    t_pj.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F766E')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_pj)
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("1.5. Định lý bảo toàn dòng tiền (Zero-Sum Conservation)", style_h2))
    story.append(Paragraph(
        "<b>Định lý:</b> Xét một chu trình trao đổi khép kín bất kỳ gồm $k$ vật phẩm: $C = (v_1, v_2, \\dots, v_k)$. Trong đó, người sở hữu vật phẩm $v_i$ chuyển giao món đồ $v_i$ cho người tiếp theo và nhận về món đồ $v_{prev}$ với $prev = (i - 1 + k) \\pmod k$. Khoản chênh lệch tiền mặt $\\Delta_i$ gán cho thành viên thứ $i$ được xác định:",
        style_body
    ))
    story.append(Paragraph("$$\\Delta_i = \\text{Val}(v_{prev}) - \\text{Val}(v_i)$$", style_formula))
    story.append(Paragraph("Tổng dòng tiền thanh toán bù trừ trong toàn bộ chu trình luôn bằng 0:", style_body))
    story.append(Paragraph(
        "$$\\sum_{i=1}^{k} \\Delta_i = \\sum_{i=1}^{k} \\left[ \\text{Val}(v_{prev}) - \\text{Val}(v_i) \\right] = \\sum_{i=1}^{k} \\text{Val}(v_{prev}) - \\sum_{i=1}^{k} \\text{Val}(v_i) = 0$$",
        style_formula
    ))
    story.append(Paragraph(
        "<b>Chứng minh:</b> Vì phép gán $i \\mapsto (i - 1 + k) \\pmod k$ là một song ánh (hoán vị) trên tập hợp chỉ số $\\{1, 2, \\dots, k\\}$, nên hai tổng $\\sum_{i=1}^{k} \\text{Val}(v_{prev})$ và $\\sum_{i=1}^{k} \\text{Val}(v_i)$ chứa chính xác các số hạng giống nhau, suy ra hiệu số triệt tiêu hoàn toàn về 0. (Đpcm).",
        style_body_italic
    ))
    story.append(Paragraph(
        "<b>Ý nghĩa thực tiễn:</b> Tổng số tiền sinh viên nhận đồ giá trị cao hơn phải nộp bù vào quỹ ký quỹ Escrow đúng bằng tổng số tiền giải ngân cho các sinh viên nhận đồ có giá trị thấp hơn. Hệ thống Trạm Hub đóng vai trò trung gian điều phối mà không phải chịu bất kỳ khoản thâm hụt tài chính nào.",
        style_body
    ))

    # Bảng ví dụ số liệu thực tế
    story.append(Paragraph("1.6. Dữ liệu thực nghiệm thực tế tại Trạm Hub HUNRE", style_h3))
    eg_data = [
        [Paragraph("Sinh viên", style_th), Paragraph("Món đồ trao đi", style_th), Paragraph("Món đồ nhận về", style_th), Paragraph("Chênh lệch $\\Delta_i$", style_th), Paragraph("Nghiệp vụ Escrow", style_th)],
        [Paragraph("Nguyễn Văn An", style_td), Paragraph("Giáo trình CSDL (75.000đ)", style_td), Paragraph("Bàn phím DareU (250.000đ)", style_td), Paragraph("+175.000đ", style_td_center), Paragraph("Nộp bù 175.000đ vào Escrow", style_td)],
        [Paragraph("Trần Thị Bích", style_td), Paragraph("Máy tính Casio (320.000đ)", style_td), Paragraph("Giáo trình CSDL (75.000đ)", style_td), Paragraph("-245.000đ", style_td_center), Paragraph("Nhận về 245.000đ từ Escrow", style_td)],
        [Paragraph("Lê Hoàng Cường", style_td), Paragraph("Bàn phím DareU (250.000đ)", style_td), Paragraph("Máy tính Casio (320.000đ)", style_td), Paragraph("+70.000đ", style_td_center), Paragraph("Nộp bù 70.000đ vào Escrow", style_td)],
        [Paragraph("<b>TỔNG CỘNG</b>", style_td_center), Paragraph("<b>645.000đ</b>", style_td_center), Paragraph("<b>645.000đ</b>", style_td_center), Paragraph("<b>0 VNĐ</b>", style_td_center), Paragraph("<b>Bảo toàn số dư 100%</b>", style_td_center)]
    ]
    t_eg = Table(eg_data, colWidths=[2.6 * cm, 3.8 * cm, 3.8 * cm, 2.4 * cm, 3.4 * cm])
    t_eg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2E8F0')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_eg)

    story.append(PageBreak())

    # =========================================================================
    # BÀI TOÁN 2: COMPUTER VISION DEFECT & CONDITION GRADING
    # =========================================================================
    story.append(Paragraph("2. GIẢI THUẬT THẨM ĐỊNH ĐỘ HAO MÒN BỀ MẶT & DÁN NHÃN CHẤT LƯỢNG BẰNG COMPUTER VISION", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("2.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Thuộc phân hệ <b>AI Engine Microservice</b> (file <code>services/ai-engine/app/services/cv_service.py</code>), phục vụ API <code>POST /api/v1/ai/cv/inspect</code>. Chức năng này tự động kích hoạt khi sinh viên tải ảnh giáo trình hoặc thiết bị lên sàn giao dịch, ngăn chặn tình trạng khai man chất lượng sản phẩm.",
        style_body
    ))

    story.append(Paragraph("2.2. Cơ sở toán học xử lý tín hiệu hình ảnh", style_h2))
    story.append(Paragraph(
        "Hình ảnh màu đầu vào kích thước $W \\times H$ được biểu diễn dưới dạng tensor bậc 3 $I(x, y, c) \\in [0, 255]$, với $c \\in \\{R, G, B\\}$. Giải thuật thực hiện chuẩn hóa và tính toán qua 3 chỉ số tín hiệu cốt lõi:",
        style_body
    ))

    story.append(Paragraph("<b>a) Phân tích độ biến thiên Gradient vi phân (Sharpness via Spatial Gradient):</b>", style_body))
    story.append(Paragraph(
        "Ảnh được chuyển đổi sang kênh độ xám (Grayscale): $I_{gray}(x, y) = 0.299R + 0.587G + 0.114B$. Toán tử đạo hàm không gian 2 chiều rời rạc theo ma trận Sobel/Gradient được tính theo hai trục:",
        style_body
    ))
    story.append(Paragraph("$$g_x(x, y) = \\frac{\\partial I_{gray}}{\\partial x}, \\quad g_y(x, y) = \\frac{\\partial I_{gray}}{\\partial y}$$", style_formula))
    story.append(Paragraph("Độ lớn Gradient tại mỗi điểm ảnh và độ sắc nét trung bình toàn khung hình:", style_body))
    story.append(Paragraph("$$\\|\\nabla I(x, y)\\| = \\sqrt{g_x^2(x, y) + g_y^2(x, y)}, \\quad S_{sharp} = \\frac{1}{W \\times H} \\sum_{x=1}^{W} \\sum_{y=1}^{H} \\|\\nabla I(x, y)\\|$$", style_formula))

    story.append(Paragraph("<b>b) Phân tích độ đồng nhất màu sắc (Color Heterogeneity / Yellowing Index):</b>", style_body))
    story.append(Paragraph(
        "Đối với sách giáo trình và đồ dùng cũ, các vết ố vàng, vết mốc hoặc trầy xước vỏ nhựa gây ra sự bất đồng nhất cục bộ giữa các kênh màu. Độ lệch chuẩn trung bình giữa các kênh RGB được tính toán:",
        style_body
    ))
    story.append(Paragraph("$$\\sigma_{color} = \\frac{1}{3} \\sum_{c \\in \\{R, G, B\\}} \\sqrt{\\frac{1}{W \\cdot H} \\sum_{x, y} \\left( I(x, y, c) - \\mu_c \\right)^2}$$", style_formula))

    story.append(Paragraph("<b>c) Hàm ước lượng tỷ lệ khiếm khuyết bề mặt (Defect Ratio Function):</b>", style_body))
    story.append(Paragraph(
        "Tỷ lệ khiếm khuyết $D_{ratio} \\in [0.01, 0.35]$ được mô hình hóa phi tuyến từ chỉ số độ biến thiên cạnh:",
        style_body
    ))
    story.append(Paragraph("$$D_{ratio} = \\min \\left( 0.35, \\max \\left( 0.01, \\frac{100 - \\min(3 \\cdot S_{sharp}, 90)}{250} \\right) \\right)$$", style_formula))

    story.append(Paragraph("2.3. Quy tắc phân lớp nhãn chất lượng (Condition Grade Mapping)", style_h2))
    story.append(Paragraph(
        "Hệ thống ánh xạ tỷ lệ khiếm khuyết vào 4 cấp độ thẩm định chuẩn mực kèm hệ số đề xuất giá sàn $K_{discount}$:",
        style_body
    ))

    grade_table = [
        [Paragraph("Tỷ lệ khiếm khuyết $D_{ratio}$", style_th), Paragraph("Phân Hạng AI", style_th), Paragraph("Độ Mới Thực Tế", style_th), Paragraph("Mô Tả Đánh Giá Tự Động", style_th), Paragraph("Hệ Số Giá Sàn $K_{discount}$", style_th)],
        [Paragraph("$D_{ratio} < 0.03$", style_td_center), Paragraph("<b>GRADE_S</b>", style_td_center), Paragraph("98% - 99%", style_td_center), Paragraph("Sản phẩm như mới, góc cạnh nguyên vẹn, không vết xước.", style_td), Paragraph("90% giá gốc", style_td_center)],
        [Paragraph("$0.03 \\le D_{ratio} < 0.08$", style_td_center), Paragraph("<b>GRADE_A</b>", style_td_center), Paragraph("90% - 95%", style_td_center), Paragraph("Rất tốt, vết xước siêu nhỏ khó thấy, trang sách sạch không quăn mép.", style_td), Paragraph("75% giá gốc", style_td_center)],
        [Paragraph("$0.08 \\le D_{ratio} < 0.15$", style_td_center), Paragraph("<b>GRADE_B</b>", style_td_center), Paragraph("80% - 89%", style_td_center), Paragraph("Đã qua sử dụng thực tế, bóng keycap, xước góc nhẹ nhưng hoạt động tốt.", style_td), Paragraph("55% giá gốc", style_td_center)],
        [Paragraph("$D_{ratio} \\ge 0.15$", style_td_center), Paragraph("<b>GRADE_C</b>", style_td_center), Paragraph("&lt; 80%", style_td_center), Paragraph("Nhiều vết trầy xước hoặc trang sách viết nhiều bút dạ, dùng tạm thời.", style_td), Paragraph("35% giá gốc", style_td_center)],
    ]
    t_gr = Table(grade_table, colWidths=[3.2 * cm, 2.3 * cm, 2.2 * cm, 5.8 * cm, 2.5 * cm])
    t_gr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#047857')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_gr)

    story.append(PageBreak())

    # =========================================================================
    # BÀI TOÁN 3: ANTI-FRAUD DIFFERENCE HASHING (dHash)
    # =========================================================================
    story.append(Paragraph("3. THUẬT TOÁN BĂM CẢM NHẬN THỊ GIÁC (dHash) PHÁT HIỆN ẢNH MẠNG CHỐNG GIAN LẬN", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("3.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Thuộc phân hệ <b>AI Engine Microservice</b> (file <code>services/ai-engine/app/services/anti_fraud.py</code>, API <code>POST /api/v1/ai/anti-fraud/check</code>). Chức năng này ngăn chặn tình trạng người bán lấy ảnh sản phẩm lung linh từ sàn Shopee, Tiki, Lazada về đăng bài ảo nhằm trục lợi hoặc bán hàng sai thực tế.",
        style_body
    ))

    story.append(Paragraph("3.2. Nguyên lý thuật toán Difference Hashing (dHash)", style_h2))
    story.append(Paragraph(
        "Khác với các hàm băm mật mã học (MD5, SHA-256) vốn thay đổi toàn bộ mã băm chỉ với 1 bit thay đổi (hiệu ứng thác lũ), thuật toán <b>dHash (Gradient Difference Hashing)</b> duy trì tính tương đồng: các ảnh chụp thực tế có cùng góc chụp hoặc chỉnh độ sáng nhẹ sẽ sinh ra mã băm có khoảng cách Hamming cực nhỏ.",
        style_body
    ))

    story.append(Paragraph("<b>Các bước thực hiện thuật toán dHash 64-bit:</b>", style_body_bold))
    story.append(Paragraph("<b>Bước 1: Giảm kích thước ảnh (Downsampling):</b> Thu nhỏ ảnh về kích thước $(N+1) \\times N$ với $N=8$, tức $9 \\times 8 = 72$ pixels sử dụng bộ lọc nội suy Lanczos.", style_body))
    story.append(Paragraph("<b>Bước 2: Chuyển ảnh xám (Grayscale Conversion):</b> Loại bỏ thông tin màu sắc để tập trung vào cường độ sáng và cấu trúc cạnh vi phân.", style_body))
    story.append(Paragraph("<b>Bước 3: So sánh vi phân gradient hàng ngang:</b> So sánh độ sáng của từng cặp pixel liền kề trên cùng một hàng:", style_body))
    story.append(Paragraph("$$B(r, c) = \\begin{cases} 1 & \\text{nếu } P(r, c) > P(r, c + 1) \\\\ 0 & \\text{nếu } P(r, c) \\le P(r, c + 1) \\end{cases} \\quad \\forall r \\in [0, 7], c \\in [0, 7]$$", style_formula))
    story.append(Paragraph("<b>Bước 4: Sinh mã chuỗi băm Hexadecimal:</b> 64 giá trị nhị phân thu được được nhóm thành 8 byte, chuyển thành chuỗi 16 ký tự Hex: $H = h_1 h_2 \\dots h_{16}$.", style_body))

    story.append(Paragraph("3.3. Đo lường khoảng cách Hamming & Bộ lọc ảnh Catalog thương mại", style_h2))
    story.append(Paragraph(
        "Độ tương đồng giữa hai ảnh được định lượng bằng <b>Khoảng cách Hamming</b>:",
        style_body
    ))
    story.append(Paragraph("$$D_H(H_1, H_2) = \\sum_{k=1}^{64} \\left( b_{1, k} \\oplus b_{2, k} \\right)$$", style_formula))
    story.append(Paragraph(
        "Nếu $D_H \\le 5$, hai ảnh được xác định là trùng lặp 100%. Bên cạnh đó, hệ thống tích hợp bộ lọc nhận dạng kích thước đặc trưng của ảnh catalog thương mại: tỷ lệ vuông chuẩn $1:1$ tại các độ phân giải mẫu của sàn Shopee/Lazada ($800 \\times 800, 1000 \\times 1000, 1200 \\times 1200$) kết hợp chỉ số nghi ngờ $S_{stock} > 0.70$ để đưa ra cảnh báo bắt buộc chụp trực tiếp từ camera sinh viên.",
        style_body
    ))

    story.append(Spacer(1, 5 * mm))

    # =========================================================================
    # BÀI TOÁN 4: TIME-DECAY PRICING / DUTCH AUCTION
    # =========================================================================
    story.append(Paragraph("4. MÔ HÌNH SUY GIẢM HÀM MŨ ĐỊNH GIÁ TỰ ĐỘNG THEO THỜI GIAN (TIME-DECAY PRICING)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("4.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Được hiện thực tại <b>Product Service</b> (file <code>services/product-service/app/Services/TimeDecayPricingService.php</code>) và <b>AI Engine</b> (file <code>price_agent.py</code>, API <code>POST /api/v1/ai/pricing/decay</code>). Phục vụ nhu cầu thanh lý gấp giáo trình cuối kỳ của sinh viên sắp tốt nghiệp.",
        style_body
    ))

    story.append(Paragraph("4.2. Xây dựng công thức toán học phân rã giá trị", style_h2))
    story.append(Paragraph(
        "Hệ thống áp dụng mô hình phân rã liên tục theo quy luật chu kỳ bán rã (Exponential Half-Life Decay):",
        style_body
    ))
    story.append(Paragraph("$$P(t) = P_{floor} + \\left( P_{orig} - P_{floor} \\right) \\cdot e^{-\\lambda t}$$", style_formula))
    story.append(Paragraph(
        "Trong đó:<br/>"
        "• $P(t)$: Giá niêm yết tại thời điểm $t$ giờ sau khi đăng tải.<br/>"
        "• $P_{orig}$: Mức giá khởi điểm ban đầu do sinh viên thiết lập.<br/>"
        "• $P_{floor}$: Mức giá sàn tối thiểu tuyệt đối (Floor Price) bảo vệ quyền lợi người bán.<br/>"
        "• $t_{1/2}$: Thời gian bán rã mặc định là $72$ giờ (3 ngày). Hằng số suy giảm $\\lambda = \\frac{\\ln(2)}{t_{1/2}} \\approx 0.009627$.",
        style_body
    ))
    story.append(Paragraph("Bảo đảm bất biến giới hạn (Boundary Invariant):", style_body_bold))
    story.append(Paragraph("$$\\lim_{t \\to \\infty} P(t) = P_{floor} \\quad \\text{và} \\quad \\forall t \\ge 0, \\; P(t) \\ge P_{floor}$$", style_formula))

    story.append(PageBreak())

    # =========================================================================
    # BÀI TOÁN 5: DYNAMIC PRICE NEGOTIATION AGENT
    # =========================================================================
    story.append(Paragraph("5. GIẢI THUẬT ĐÀM PHÁN THƯƠNG LƯỢNG GIÁ DỰA TRÊN ĐIỂM UY TÍN (AI PRICE NEGOTIATOR)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("5.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Hiện thực tại <b>AI Engine Microservice</b> (file <code>services/ai-engine/app/services/price_agent.py</code>, API <code>POST /api/v1/ai/pricing/negotiate</code>). Tích hợp tại nút <b>\"Trả Giá AI\"</b> trong giao diện Chợ sinh viên, thay thế người bán tự động đàm phán 24/7.",
        style_body
    ))

    story.append(Paragraph("5.2. Mô hình cây quyết định đa tiêu chí (Multi-Criteria Decision Tree)", style_h2))
    story.append(Paragraph(
        "Cho người mua đưa ra mức giá đề xuất $P_{offer}$ và sở hữu Điểm Uy Tín HUNRE $T \\in [0, 1000]$. Giá niêm yết hiện tại là $P_{curr}$ và giá sàn người bán là $P_{floor}$. Thuật toán xác định tỷ số tương đối và ngưỡng chấp nhận linh hoạt:",
        style_body
    ))
    story.append(Paragraph("$$\\rho = \\frac{P_{offer} - P_{floor}}{P_{curr} - P_{floor} + \\epsilon}, \\quad \\theta_{accept}(T) = 0.5 - \\frac{T}{2000}$$", style_formula))
    story.append(Paragraph(
        "Hàm ngưỡng $\\theta_{accept}(T)$ phản ánh tính chất: Sinh viên có điểm uy tín càng cao ($T \\to 1000$) thì ngưỡng đòi hỏi $\\theta_{accept}$ càng hạ thấp ($0.5 \\to 0.0$), giúp việc thương lượng thành công dễ dàng hơn.",
        style_body
    ))

    story.append(Paragraph("<b>Quy tắc ra quyết định tự động:</b>", style_body_bold))
    story.append(Paragraph("1. <b>Trường hợp 1 ($P_{offer} \\ge P_{curr}$):</b> Chấp thuận ngay lập tức (<code>DECISION = ACCEPT</code>).", style_body))
    story.append(Paragraph("2. <b>Trường hợp 2 ($P_{offer} < P_{floor}$):</b> Mức giá vi phạm giá sàn. Nếu $T \\ge 600$ (Hạng Vàng/Kim Cương), AI đưa ra mức giá thỏa hiệp ưu đãi $P_{counter} = P_{floor} \\times 1.03$ (<code>COUNTER_OFFER</code>); ngược lại từ chối thẳng thừng (<code>REJECT</code>).", style_body))
    story.append(Paragraph("3. <b>Trường hợp 3 ($P_{floor} \\le P_{offer} < P_{curr}$):</b> Nếu $\\rho \\ge \\theta_{accept}(T) \\rightarrow$ <code>ACCEPT</code>; ngược lại đề xuất giá trung gian $P_{counter} = \\text{Round}(\\frac{P_{offer} + P_{curr}}{2}, -3)$.", style_body))

    story.append(Spacer(1, 5 * mm))

    # =========================================================================
    # BÀI TOÁN 6: DYNAMIC QR TOTP 30s ROTATION
    # =========================================================================
    story.append(Paragraph("6. THUẬT TOÁN XÁC THỰC MÃ QR ĐỘNG XOAY VÒNG DYNAMIC QR TOTP VỚI HMAC-SHA256", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("6.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Thuộc phân hệ <b>Hub Logistics Microservice</b> (Port 8004, file <code>services/hub-service/app/Services/DynamicQREngine.php</code>), hiển thị trên giao diện người dùng <code>pages/escrow-order.html</code> và máy quét PWA của thủ kho <code>frontend/hub-staff-portal/index.html</code>.",
        style_body
    ))

    story.append(Paragraph("6.2. Cơ chế mật mã học HMAC-SHA256 theo khung thời gian", style_h2))
    story.append(Paragraph(
        "Để triệt tiêu hoàn toàn lỗ hổng kẻ xấu chụp trộm màn hình điện thoại của sinh viên để đến Trạm Hub nhận đồ, mã QR được tạo động theo khung thời gian 30 giây (Time-based One-Time Password - RFC 6238):",
        style_body
    ))
    story.append(Paragraph("$$W(t) = \\left\\lfloor \\frac{t}{T_{step}} \\right\\rfloor \\quad \\text{với } T_{step} = 30 \\text{ giây}$$", style_formula))
    story.append(Paragraph("Thông điệp băm $M(t)$ và chữ ký số $\\tau(t)$:", style_body))
    story.append(Paragraph("$$M(t) = \\text{OrderCode} \\parallel \\text{UserId} \\parallel \\text{Role} \\parallel W(t)$$", style_formula))
    story.append(Paragraph("$$\\tau(t) = \\text{Truncate}_{16} \\left( \\text{HMAC-SHA256}\\left( K_{secret}, M(t) \\right) \\right)$$", style_formula))
    story.append(Paragraph(
        "<b>Cơ chế xác thực chịu lỗi trễ mạng (Clock Skew Tolerance):</b> Khi máy quét tại Trạm Hub nhận mã, hệ thống kiểm tra chữ ký với $W(t)$ và $W(t) - 1$ (cửa sổ trễ 30s) bằng hàm so sánh bất biến thời gian <code>hash_equals()</code> để chống tấn công Timing Attack.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # BÀI TOÁN 7: SMART ESCROW SAGA FINITE STATE MACHINE
    # =========================================================================
    story.append(Paragraph("7. MÔ HÌNH MÁY TRẠNG THÁI HỮU HẠN & ĐIỀU PHỐI GIAO DỊCH PHÂN TÁN SAGA (SMART ESCROW)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("7.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Thuộc phân hệ <b>Escrow & Payment Microservice</b> (Port 8003, file <code>services/escrow-service/app/Services/EscrowSagaOrchestrator.php</code>), hiển thị quy trình 7 bước tại thanh Stepper của trang <code>pages/escrow-order.html</code>.",
        style_body
    ))

    story.append(Paragraph("7.2. Định nghĩa máy trạng thái hữu hạn Automaton", style_h2))
    story.append(Paragraph(
        "Tiến trình ký quỹ được mô hình hóa thành một bộ máy trạng thái hữu hạn xác định $M = (S, \\Sigma, \\delta, s_0, F)$:",
        style_body
    ))
    story.append(Paragraph("• Tập hợp 7 trạng thái: $S = \\{\\text{INITIATED}, \\text{ESCROW\\_LOCKED}, \\text{STORED\\_AT\\_HUB}, \\text{INSPECTING}, \\text{RELEASED}, \\text{DISPUTED}, \\text{REFUNDED}\\}$.", style_body))
    story.append(Paragraph("• Trạng thái khởi đầu: $s_0 = \\text{INITIATED}$.", style_body))
    story.append(Paragraph("• Tập trạng thái kết thúc: $F = \\{\\text{RELEASED}, \\text{REFUNDED}\\}$.", style_body))

    saga_table = [
        [Paragraph("Trạng thái hiện tại $s$", style_th), Paragraph("Sự kiện kích hoạt $e$", style_th), Paragraph("Điều kiện kiểm tra Guard", style_th), Paragraph("Trạng thái kế tiếp $s'$", style_th), Paragraph("Hành động đền bù Saga", style_th)],
        [Paragraph("INITIATED", style_td_center), Paragraph("PAY_DEPOSIT", style_td), Paragraph("Tiền vào tài khoản trung gian", style_td), Paragraph("ESCROW_LOCKED", style_td_center), Paragraph("Hủy đơn, hoàn cọc", style_td)],
        [Paragraph("ESCROW_LOCKED", style_td_center), Paragraph("SELLER_CHECKIN", style_td), Paragraph("Thủ kho quét QR TOTP hợp lệ", style_td), Paragraph("STORED_AT_HUB", style_td_center), Paragraph("Mở tủ trả đồ về người bán", style_td)],
        [Paragraph("STORED_AT_HUB", style_td_center), Paragraph("BUYER_CHECKOUT", style_td), Paragraph("Người mua quét QR nhận đồ", style_td), Paragraph("INSPECTING", style_td_center), Paragraph("Khóa tủ giữ nguyên vị trí", style_td)],
        [Paragraph("INSPECTING", style_td_center), Paragraph("BUYER_SATISFIED", style_td), Paragraph("Người mua bấm xác nhận hài lòng", style_td), Paragraph("<b>RELEASED</b>", style_td_center), Paragraph("Giải ngân cho người bán", style_td)],
        [Paragraph("INSPECTING", style_td_center), Paragraph("RAISE_DISPUTE", style_td), Paragraph("Hàng vỡ/sai mô tả tại Hub", style_td), Paragraph("DISPUTED", style_td_center), Paragraph("Lập biên bản trung gian", style_td)],
        [Paragraph("DISPUTED", style_td_center), Paragraph("ADMIN_RESOLVE", style_td), Paragraph("Thủ kho xác nhận hàng lỗi", style_td), Paragraph("<b>REFUNDED</b>", style_td_center), Paragraph("Hoàn tiền 100% người mua", style_td)],
    ]
    t_sg = Table(saga_table, colWidths=[2.8 * cm, 3.2 * cm, 3.8 * cm, 3.0 * cm, 3.2 * cm])
    t_sg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_sg)

    story.append(Spacer(1, 5 * mm))

    # =========================================================================
    # BÀI TOÁN 8: TRUST SCORE ENGINE
    # =========================================================================
    story.append(Paragraph("8. GIẢI THUẬT ĐÁNH GIÁ TÍN NHIỆM & TÍNH ĐIỂM UY TÍN SINH VIÊN (TRUST SCORE ENGINE)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("8.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "Thuộc phân hệ <b>Auth & Identity Microservice</b> (Port 8001, file <code>services/auth-service/app/Services/TrustScoreService.php</code>, API <code>GET /api/v1/auth/users/trust-score</code>). Quyết định các đặc quyền miễn đặt cọc và ưu tiên ghép cặp trong Barter Graph.",
        style_body
    ))

    story.append(Paragraph("8.2. Hàm tích lũy điểm hành vi rời rạc", style_h2))
    story.append(Paragraph(
        "Điểm uy tín của sinh viên tại thời điểm $n+1$ là một hàm tích lũy có chặn trên và chặn dưới trong không gian $T \\in [0, 1000]$:",
        style_body
    ))
    story.append(Paragraph("$$T_{n+1} = \\max \\left( 0, \\min \\left( 1000, T_n + \\sum_{j} w_j \\cdot E_j \\right) \\right)$$", style_formula))
    story.append(Paragraph(
        "Trong đó $w_j$ là véc-tơ trọng số tương ứng với các biến cố hành vi $E_j$:<br/>"
        "• $w_1 = +5$: Hoàn tất giao dịch O2O đúng hẹn tại Trạm Hub CS1.<br/>"
        "• $w_2 = +2$: Nhận đánh giá 5 sao từ bạn học cùng trường.<br/>"
        "• $w_3 = -15$: Quá hạn 48h không mang đồ đến gửi tại tủ Trạm Hub.<br/>"
        "• $w_4 = -20$: Tự ý hủy kèo sau khi Barter Graph đã ghép cặp thành công.<br/>"
        "• $w_5 = -30$: Cố tình khai gian tình trạng sản phẩm bị camera Hub phát hiện.",
        style_body
    ))

    # Bảng phân hạng Tier
    tier_data = [
        [Paragraph("Thang Điểm Uy Tín", style_th), Paragraph("Phân Hạng Sinh Viên (Tier)", style_th), Paragraph("Quyền Lợi & Đặc Quyền Trong Hệ Thống", style_th)],
        [Paragraph("800 - 1000 Điểm", style_td_center), Paragraph("<b>KIM CƯƠNG</b>", style_td_center), Paragraph("Bảo chứng uy tín 100%, được phép nhận hàng trước không cần cọc tiền.", style_td)],
        [Paragraph("600 - 799 Điểm", style_td_center), Paragraph("<b>VÀNG</b>", style_td_center), Paragraph("Ưu tiên số 1 khi quét chu trình Barter Graph, giảm 50% tiền cọc Escrow.", style_td)],
        [Paragraph("400 - 599 Điểm", style_td_center), Paragraph("<b>BẠC (Tiêu chuẩn)</b>", style_td_center), Paragraph("Hưởng đầy đủ tính năng mua bán, đổi đồ và trả giá AI thông thường.", style_td)],
        [Paragraph("200 - 399 Điểm", style_td_center), Paragraph("<b>ĐỒNG</b>", style_td_center), Paragraph("Phải đặt cọc 100% giá trị món đồ khi tham gia ký quỹ tại Trạm Hub.", style_td)],
        [Paragraph("&lt; 200 Điểm", style_td_center), Paragraph("<b>CẢNH BÁO</b>", style_td_center), Paragraph("Hạn chế quyền đổi đồ, bắt buộc xác minh lại thẻ sinh viên tại Đoàn Trường.", style_td)],
    ]
    t_tr = Table(tier_data, colWidths=[3.2 * cm, 3.8 * cm, 9.0 * cm])
    t_tr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_tr)

    story.append(PageBreak())

    # =========================================================================
    # KẾT LUẬN & TỔNG KẾT BẢO VỆ ĐỒ ÁN
    # =========================================================================
    story.append(Paragraph("KẾT LUẬN & ĐÁNH GIÁ ĐÓNG GÓP KHOA HỌC", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "Báo cáo đã hệ thống hóa và đặc tả chi tiết 8 mô hình toán học và giải thuật được tích hợp hoàn chỉnh trong dự án HUNRE E-Commerce. Các đóng góp học thuật và ứng dụng thực tiễn nổi bật bao gồm:",
        style_body
    ))
    story.append(Paragraph(
        "1. <b>Tính hoàn chỉnh lý thuyết và bảo toàn dòng tiền:</b> Đã xây dựng và chứng minh thành công định lý bảo toàn số dư (Zero-Sum Conservation) trên chu trình có hướng đa chiều, cho phép giải phóng nhu cầu trao đổi hàng hóa không cần tiền tệ hóa hoàn toàn.",
        style_body
    ))
    story.append(Paragraph(
        "2. <b>Ứng dụng trí tuệ nhân tạo thiết thực:</b> Kết hợp hài hòa giữa thị giác máy tính xử lý ảnh (Computer Vision, dHash) và các tác tử đàm phán thông minh (Negotiation Agent) giúp giải quyết triệt để vấn đề niềm tin và minh bạch chất lượng đồ cũ.",
        style_body
    ))
    story.append(Paragraph(
        "3. <b>Mô hình vận hành O2O an toàn tuyệt đối:</b> Hệ thống kết hợp nhịp nhàng giữa máy trạng thái ký quỹ phân tán Saga và mã QR động bảo mật TOTP 30s với Trạm Hub vật lý tại Đoàn Thanh niên HUNRE, mang lại giải pháp công nghệ mang tính khả thi cao phục vụ trực tiếp cộng đồng sinh viên nhà trường.",
        style_body
    ))

    story.append(Spacer(1, 15 * mm))

    # Chữ ký đại diện
    sign_data = [
        [Paragraph("", style_body), Paragraph("Hà Nội, ngày 23 tháng 09 năm 2026", style_cover_meta)],
        [Paragraph("", style_body), Paragraph("<b>ĐẠI DIỆN NHÓM NGHIÊN CỨU & PHÁT TRIỂN</b>", style_cover_meta_b)],
        [Paragraph("", style_body), Spacer(1, 20 * mm)],
        [Paragraph("", style_body), Paragraph("<b>Hệ thống HUNRE E-Commerce</b>", style_cover_meta_b)]
    ]
    t_sign = Table(sign_data, colWidths=[7.0 * cm, 9.0 * cm])
    t_sign.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_sign)

    # Build tài liệu
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"XUẤT BẢN FILE PDF THÀNH CÔNG: {filename}")

if __name__ == '__main__':
    output_pdf = "d:/Intel/Project/crs-microservices/BTL/tailieu/BAO_CAO_TOAN_HOC_VA_THUAT_TOAN_HE_THONG.pdf"
    build_pdf(output_pdf)
