# -*- coding: utf-8 -*-
"""
Script xuất tài liệu kỹ thuật chuẩn định dạng:
TÀI LIỆU KỸ THUẬT: MÔ HÌNH TOÁN HỌC VÀ CÁC GIẢI THUẬT HỆ THỐNG
HUNRE E-Commerce Platform
Định dạng: Đơn sắc (đen trắng), chuẩn tài liệu khoa học, không màu mè, không lỗi công thức.
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

# Đăng ký font Times New Roman chuẩn hệ thống
FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Times', os.path.join(FONT_DIR, 'times.ttf')))
pdfmetrics.registerFont(TTFont('Times-Bold', os.path.join(FONT_DIR, 'timesbd.ttf')))
pdfmetrics.registerFont(TTFont('Times-Italic', os.path.join(FONT_DIR, 'timesi.ttf')))
pdfmetrics.registerFont(TTFont('Times-BoldItalic', os.path.join(FONT_DIR, 'timesbi.ttf')))

class MonochromeNumberedCanvas(canvas.Canvas):
    """Canvas đánh số trang đen trắng: 'Trang X / Y' và Header kỹ thuật"""
    def __init__(self, *args, **kwargs):
        super(MonochromeNumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont('Times', 8.5)
        self.setFillColor(colors.black)

        # Header trên mọi trang
        self.drawString(2.0 * cm, 28.5 * cm, "TÀI LIỆU KỸ THUẬT: MÔ HÌNH TOÁN HỌC & GIẢI THUẬT HỆ THỐNG — HUNRE E-COMMERCE")
        self.setStrokeColor(colors.black)
        self.setLineWidth(0.6)
        self.line(2.0 * cm, 28.3 * cm, 19.0 * cm, 28.3 * cm)

        # Footer dưới mọi trang
        self.line(2.0 * cm, 1.6 * cm, 19.0 * cm, 1.6 * cm)
        self.drawString(2.0 * cm, 1.2 * cm, "Hệ Thống Thương Mại Điện Tử O2O & Trí Tuệ Nhân Tạo — Khoa CNTT, HUNRE")
        page_str = f"Trang {self._pageNumber} / {page_count}"
        self.drawRightString(19.0 * cm, 1.2 * cm, page_str)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm
    )

    styles = getSampleStyleSheet()

    # Định dạng văn bản đơn sắc kỹ thuật chuẩn mực (Black & White)
    style_doc_title = ParagraphStyle(
        'DocTitle',
        fontName='Times-Bold',
        fontSize=17,
        leading=22,
        alignment=1, # Căn giữa
        textColor=colors.black,
        spaceAfter=4
    )
    style_doc_subtitle = ParagraphStyle(
        'DocSubTitle',
        fontName='Times-Italic',
        fontSize=11,
        leading=15,
        alignment=1,
        textColor=colors.black,
        spaceAfter=12
    )
    style_meta_block = ParagraphStyle(
        'MetaBlock',
        fontName='Times',
        fontSize=9.5,
        leading=14,
        alignment=0,
        textColor=colors.black,
        spaceAfter=10
    )
    style_h1 = ParagraphStyle(
        'H1_Mono',
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.black,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'H2_Mono',
        fontName='Times-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.black,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Body_Mono',
        fontName='Times',
        fontSize=10,
        leading=14.5,
        textColor=colors.black,
        alignment=4, # Justify
        spaceBefore=2,
        spaceAfter=3
    )
    style_body_bold = ParagraphStyle(
        'BodyBold_Mono',
        parent=style_body,
        fontName='Times-Bold'
    )
    style_body_italic = ParagraphStyle(
        'BodyItalic_Mono',
        parent=style_body,
        fontName='Times-Italic'
    )
    style_formula = ParagraphStyle(
        'Formula_Mono',
        fontName='Times-Italic',
        fontSize=10.5,
        leading=15,
        alignment=1, # Căn giữa
        textColor=colors.black,
        spaceBefore=4,
        spaceAfter=4
    )
    style_code = ParagraphStyle(
        'Code_Mono',
        fontName='Times',
        fontSize=9,
        leading=12.5,
        textColor=colors.black,
        spaceBefore=2,
        spaceAfter=2
    )
    style_th = ParagraphStyle(
        'TH_Mono',
        fontName='Times-Bold',
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.black
    )
    style_td = ParagraphStyle(
        'TD_Mono',
        fontName='Times',
        fontSize=9,
        leading=12,
        textColor=colors.black
    )
    style_td_center = ParagraphStyle(
        'TDC_Mono',
        fontName='Times',
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.black
    )

    story = []

    # =========================================================================
    # TIÊU ĐỀ TÀI LIỆU (KHÔNG DÙNG BÌA MÀU MÈ, BẮT ĐẦU TRỰC TIẾP NHƯ SPEC KỸ THUẬT)
    # =========================================================================
    story.append(Paragraph("TÀI LIỆU KỸ THUẬT GIẢI THUẬT VÀ MÔ HÌNH TOÁN HỌC", style_doc_title))
    story.append(Paragraph("Hệ thống giao dịch trao đổi hàng hóa sinh viên O2O & AI (HUNRE E-Commerce)", style_doc_subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=8))

    meta_text = (
        "<b>Đơn vị phát triển:</b> Nhóm Nghiên cứu & Phát triển Hệ thống HUNRE E-Commerce<br/>"
        "<b>Cơ sở đào tạo:</b> Khoa Công nghệ Thông tin — Trường Đại học Tài nguyên và Môi trường Hà Nội<br/>"
        "<b>Phiên bản tài liệu:</b> 2.1.0 &nbsp;|&nbsp; <b>Phạm vi:</b> Kiến trúc thuật toán lõi trong 5 Microservices và 2 Web Portals<br/>"
        "<b>Mục đích:</b> Tài liệu kỹ thuật chi tiết phục vụ thẩm định giải thuật, đối chiếu mã nguồn và nghiệm thu hệ thống."
    )
    story.append(Paragraph(meta_text, style_meta_block))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=2, spaceAfter=10))

    # =========================================================================
    # PHẦN 1: BARTER GRAPH 2.0 & JOHNSON'S CYCLE DETECTION
    # =========================================================================
    story.append(Paragraph("1. BÀI TOÁN GHÉP CẶP CHU TRÌNH TRAO ĐỔI ĐỒ 3 CHIỀU & BẢO TOÀN SỐ DƯ (AI BARTER GRAPH 2.0)", style_h1))
    
    story.append(Paragraph("1.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> AI Engine Microservice (Port 8005).<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/ai-engine/app/services/graph_solver.py</code>.<br/>"
        "• <b>Endpoint API:</b> <code>POST /api/v1/ai/barter/solve-cycles</code>.<br/>"
        "• <b>Giao diện hiển thị:</b> <code>frontend/student-portal/pages/barter-graph.html</code> (Canvas đồ thị và bảng bù trừ).",
        style_body
    ))

    story.append(Paragraph("1.2. Phát biểu bài toán", style_h2))
    story.append(Paragraph(
        "Trong kinh tế chia sẻ tại trường đại học, một sinh viên sở hữu vật phẩm <i>u</i> muốn đổi lấy vật phẩm <i>v</i>, nhưng người giữ <i>v</i> không cần <i>u</i> mà lại cần vật phẩm <i>w</i> của sinh viên thứ ba. Giao dịch song phương (2 bên) lập tức bế tắc. Mục tiêu của bài toán là tìm chu trình trao đổi khép kín đa phương <i>S</i><sub>1</sub> &rarr; <i>S</i><sub>2</sub> &rarr; <i>S</i><sub>3</sub> &rarr; ... &rarr; <i>S</i><sub><i>k</i></sub> &rarr; <i>S</i><sub>1</sub> (độ dài <i>k</i> &in; [2, 4]) và giải bài toán bù trừ giá trị chênh lệch tiền mặt để bảo toàn số dư.",
        style_body
    ))

    story.append(Paragraph("1.3. Biểu diễn toán học đồ thị có hướng có trọng số", style_h2))
    story.append(Paragraph(
        "Định nghĩa đồ thị có hướng <i>G</i> = (<i>V</i>, <i>E</i>, <i>W</i>):<br/>"
        "• <b>Tập đỉnh <i>V</i>:</b> Mỗi đỉnh <i>v</i><sub><i>i</i></sub> đại diện cho một vật phẩm đăng ký trao đổi. Thuộc tính đỉnh gồm: Owner(<i>v</i><sub><i>i</i></sub>) (mã sinh viên), Val(<i>v</i><sub><i>i</i></sub>) (giá trị định giá theo VNĐ), Wish(<i>v</i><sub><i>i</i></sub>) (tập từ khóa nhu cầu mong muốn nhận lại).<br/>"
        "• <b>Tập cạnh <i>E</i>:</b> Cạnh có hướng (<i>u</i>, <i>v</i>) &in; <i>E</i> tồn tại khi và chỉ khi:",
        style_body
    ))
    story.append(Paragraph("Owner(<i>u</i>) &ne; Owner(<i>v</i>) &nbsp;&and;&nbsp; [Title(<i>v</i>) &in; Wish(<i>u</i>) &nbsp;&or;&nbsp; Category(<i>v</i>) &in; Wish(<i>u</i>) &nbsp;&or;&nbsp; AcceptAny(<i>u</i>) = True]", style_formula))
    story.append(Paragraph("• <b>Hàm trọng số <i>W</i>:</b> <i>W</i>(<i>u</i>, <i>v</i>) thể hiện độ chênh lệch giá trị giữa vật phẩm nhận về và vật phẩm chuyển giao: <i>W</i>(<i>u</i>, <i>v</i>) = Val(<i>v</i>) - Val(<i>u</i>).", style_body))

    story.append(Paragraph("1.4. Thuật toán tìm chu trình Johnson (Johnson's Simple Directed Cycle Finding)", style_h2))
    story.append(Paragraph(
        "Áp dụng thuật toán Johnson (1975) dựa trên duyệt theo chiều sâu (DFS) có kiểm soát danh sách chặn (Blocked Set) để tìm toàn bộ chu trình đơn có độ dài từ 2 đến <i>L</i><sub>max</sub> (mặc định <i>L</i><sub>max</sub> = 3):",
        style_body
    ))

    pseudo_j = [
        [Paragraph("<b>Mã giả Thuật toán Johnson's Cycle Finding kết hợp Ràng buộc Chiều dài:</b>", style_th)],
        [Paragraph(
            "<b>Đầu vào:</b> Đồ thị có hướng G = (V, E), giới hạn chiều dài L_max = 3<br/>"
            "<b>Đầu ra:</b> Danh sách các chu trình thỏa mãn Cycles = {C_1, C_2, ...}<br/>"
            "1. Phân rã G thành các thành phần liên thông mạnh (Strongly Connected Components - SCC).<br/>"
            "2. Với mỗi thành phần SCC_k có từ 2 đỉnh trở lên:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;a. Chọn đỉnh s có chỉ số thứ tự nhỏ nhất làm đỉnh gốc.<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;b. Khởi tạo mảng blocked = [False] * |V|, B = {v: [] cho mọi v trong V}, stack = []<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;c. Hàm đệ quy Circuit(v):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;f = False; push v vào stack; blocked[v] = True<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Duyệt từng đỉnh kề w thuộc danh sách kề Adj[v]:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu w == s:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu 2 &le; độ dài stack &le; L_max: Lưu lại chu trình stack; f = True<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ngược lại nếu blocked[w] == False:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu Circuit(w) == True: f = True<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nếu f == True: Unblock(v)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ngược lại: Với mỗi w trong Adj[v], thêm v vào B[w]<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Pop v khỏi stack; trả về f<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;d. Gọi Circuit(s), sau đó xóa bỏ s khỏi G và lặp lại bước 2.",
            style_code
        )]
    ]
    t_pj = Table(pseudo_j, colWidths=[17.0 * cm])
    t_pj.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E5E5')),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.6, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_pj)

    story.append(Paragraph("1.5. Định lý bảo toàn số dư tiền mặt (Zero-Sum Balance Invariant)", style_h2))
    story.append(Paragraph(
        "<b>Định lý:</b> Xét chu trình <i>C</i> = (<i>v</i><sub>1</sub>, <i>v</i><sub>2</sub>, ..., <i>v</i><sub><i>k</i></sub>). Người sở hữu vật phẩm <i>v</i><sub><i>i</i></sub> chuyển giao <i>v</i><sub><i>i</i></sub> và nhận về vật phẩm <i>v</i><sub><i>prev</i></sub> (với <i>prev</i> = (<i>i</i> - 1 + <i>k</i>) mod <i>k</i>). Khoản tiền chênh lệch &Delta;<sub><i>i</i></sub> được xác định:",
        style_body
    ))
    story.append(Paragraph("&Delta;<sub><i>i</i></sub> = Val(<i>v</i><sub><i>prev</i></sub>) - Val(<i>v</i><sub><i>i</i></sub>)", style_formula))
    story.append(Paragraph(
        "• Nếu &Delta;<sub><i>i</i></sub> &gt; 0: Sinh viên nhận đồ có giá trị cao hơn đồ cho đi &rarr; Phải nộp bù &Delta;<sub><i>i</i></sub> vào quỹ ký quỹ Smart Escrow.<br/>"
        "• Nếu &Delta;<sub><i>i</i></sub> &lt; 0: Sinh viên nhận đồ có giá trị thấp hơn &rarr; Được nhận lại |&Delta;<sub><i>i</i></sub>| từ quỹ ký quỹ Smart Escrow.<br/>"
        "• Nếu &Delta;<sub><i>i</i></sub> = 0: Trao đổi ngang giá hoàn hảo.",
        style_body
    ))
    story.append(Paragraph("Tổng dòng tiền thanh toán bù trừ trong chu trình luôn bảo toàn triệt để:", style_body))
    story.append(Paragraph("&Sigma;<sub><i>i</i>=1..<i>k</i></sub> &Delta;<sub><i>i</i></sub> = &Sigma;<sub><i>i</i>=1..<i>k</i></sub> [Val(<i>v</i><sub><i>prev</i></sub>) - Val(<i>v</i><sub><i>i</i></sub>)] = &Sigma;<sub><i>i</i>=1..<i>k</i></sub> Val(<i>v</i><sub><i>prev</i></sub>) - &Sigma;<sub><i>i</i>=1..<i>k</i></sub> Val(<i>v</i><sub><i>i</i></sub>) = 0", style_formula))
    story.append(Paragraph("<b>Ý nghĩa:</b> Tổng tiền nộp bù của các sinh viên nhận đồ đắt hơn bằng chính xác tổng tiền chi trả cho các sinh viên nhận đồ rẻ hơn. Quỹ trung gian Escrow luôn cân bằng tài chính 100%, không phát sinh rủi ro thâm hụt.", style_body_italic))

    # Bảng ví dụ số liệu thực tế
    eg_table = [
        [Paragraph("Thành viên", style_th), Paragraph("Món đồ trao đi", style_th), Paragraph("Món đồ nhận về", style_th), Paragraph("Chênh lệch &Delta;<sub>i</sub>", style_th), Paragraph("Nghiệp vụ Smart Escrow", style_th)],
        [Paragraph("Nguyễn Văn An", style_td), Paragraph("Giáo trình CSDL (75.000đ)", style_td), Paragraph("Bàn phím DareU (250.000đ)", style_td), Paragraph("+175.000đ", style_td_center), Paragraph("Nộp bù 175.000đ vào Escrow", style_td)],
        [Paragraph("Trần Thị Bích", style_td), Paragraph("Casio FX 580VN (320.000đ)", style_td), Paragraph("Giáo trình CSDL (75.000đ)", style_td), Paragraph("-245.000đ", style_td_center), Paragraph("Nhận lại 245.000đ từ Escrow", style_td)],
        [Paragraph("Lê Hoàng Cường", style_td), Paragraph("Bàn phím DareU (250.000đ)", style_td), Paragraph("Casio FX 580VN (320.000đ)", style_td), Paragraph("+70.000đ", style_td_center), Paragraph("Nộp bù 70.000đ vào Escrow", style_td)],
        [Paragraph("<b>TỔNG CỘNG</b>", style_td_center), Paragraph("<b>645.000đ</b>", style_td_center), Paragraph("<b>645.000đ</b>", style_td_center), Paragraph("<b>0 VNĐ</b>", style_td_center), Paragraph("<b>Bảo toàn dòng tiền tuyệt đối</b>", style_td_center)],
    ]
    t_eg = Table(eg_table, colWidths=[2.8 * cm, 3.8 * cm, 3.8 * cm, 2.5 * cm, 4.1 * cm])
    t_eg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E5E5')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F5F5F5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_eg)

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 2: THẨM ĐỊNH COMPUTER VISION & CONDITION GRADING
    # =========================================================================
    story.append(Paragraph("2. GIẢI THUẬT THẨM ĐỊNH ĐỘ HAO MÒN & PHÂN HẠNG CHẤT LƯỢNG (COMPUTER VISION)", style_h1))
    
    story.append(Paragraph("2.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> AI Engine Microservice.<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/ai-engine/app/services/cv_service.py</code>.<br/>"
        "• <b>Endpoint API:</b> <code>POST /api/v1/ai/cv/inspect</code>.<br/>"
        "• <b>Giao diện hiển thị:</b> Modal Thẩm định chất lượng khi sinh viên đăng bài tại <code>frontend/student-portal/index.html</code>.",
        style_body
    ))

    story.append(Paragraph("2.2. Biểu diễn toán học xử lý tín hiệu hình ảnh", style_h2))
    story.append(Paragraph(
        "Ảnh đầu vào được chuẩn hóa sang không gian độ xám ma trận <i>I</i><sub>gray</sub>(<i>x</i>, <i>y</i>) kích thước <i>W</i> &times; <i>H</i>:<br/>"
        "1. <b>Gradient vi phân không gian 2 chiều:</b> Tính đạo hàm riêng theo trục ngang <i>g</i><sub><i>x</i></sub> và trục dọc <i>g</i><sub><i>y</i></sub>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<i>g</i><sub><i>x</i></sub>(<i>x</i>, <i>y</i>) = &part;<i>I</i><sub>gray</sub> / &part;<i>x</i>, &nbsp;&nbsp;&nbsp;&nbsp; <i>g</i><sub><i>y</i></sub>(<i>x</i>, <i>y</i>) = &part;<i>I</i><sub>gray</sub> / &part;<i>y</i><br/>"
        "2. <b>Độ lớn Gradient tại mỗi điểm ảnh và điểm sắc nét trung bình toàn khung ảnh:</b>",
        style_body
    ))
    story.append(Paragraph("||&nabla;I(<i>x</i>, <i>y</i>)|| = &radic;(<i>g</i><sub><i>x</i></sub><sup>2</sup>(<i>x</i>, <i>y</i>) + <i>g</i><sub><i>y</i></sub><sup>2</sup>(<i>x</i>, <i>y</i>)), &nbsp;&nbsp;&nbsp;&nbsp; <i>S</i><sub>sharp</sub> = (1 / (<i>W</i> &times; <i>H</i>)) &times; &Sigma;<sub><i>x</i>, <i>y</i></sub> ||&nabla;I(<i>x</i>, <i>y</i>)||", style_formula))
    story.append(Paragraph(
        "3. <b>Chỉ số bất đồng nhất màu sắc (đo lường vết ố vàng / trầy xước):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&sigma;<sub>color</sub> = (1 / 3) &times; &Sigma;<sub><i>c</i> &in; {R,G,B}</sub> &radic;[ (1 / (<i>W</i> &times; <i>H</i>)) &times; &Sigma;<sub><i>x</i>, <i>y</i></sub> (<i>I</i>(<i>x</i>, <i>y</i>, <i>c</i>) - &mu;<sub><i>c</i></sub>)<sup>2</sup> ]<br/>"
        "4. <b>Hàm ước lượng tỷ lệ khiếm khuyết bề mặt:</b>",
        style_body
    ))
    story.append(Paragraph("<i>D</i><sub>ratio</sub> = min(0.35, max(0.01, (100 - min(3 &times; <i>S</i><sub>sharp</sub>, 90)) / 250))", style_formula))

    story.append(Paragraph("2.3. Bảng quy tắc phân lớp nhãn chất lượng (Condition Grade)", style_h2))
    
    cv_table = [
        [Paragraph("Tỷ lệ khiếm khuyết <i>D</i><sub>ratio</sub>", style_th), Paragraph("Phân Hạng AI", style_th), Paragraph("Độ mới thực tế", style_th), Paragraph("Mô tả đánh giá chất lượng", style_th), Paragraph("Hệ số giá sàn đề xuất", style_th)],
        [Paragraph("<i>D</i><sub>ratio</sub> &lt; 0.03", style_td_center), Paragraph("<b>GRADE_S</b>", style_td_center), Paragraph("98% - 99%", style_td_center), Paragraph("Sản phẩm như mới, góc cạnh nguyên vẹn, không vết xước.", style_td), Paragraph("90% giá gốc", style_td_center)],
        [Paragraph("0.03 &le; <i>D</i><sub>ratio</sub> &lt; 0.08", style_td_center), Paragraph("<b>GRADE_A</b>", style_td_center), Paragraph("90% - 95%", style_td_center), Paragraph("Tình trạng rất tốt, chỉ có xước dăm cực nhỏ, trang sách sạch.", style_td), Paragraph("75% giá gốc", style_td_center)],
        [Paragraph("0.08 &le; <i>D</i><sub>ratio</sub> &lt; 0.15", style_td_center), Paragraph("<b>GRADE_B</b>", style_td_center), Paragraph("80% - 89%", style_td_center), Paragraph("Có dấu vết sử dụng thực tế (bóng phím, sờn mép), hoạt động tốt.", style_td), Paragraph("55% giá gốc", style_td_center)],
        [Paragraph("<i>D</i><sub>ratio</sub> &ge; 0.15", style_td_center), Paragraph("<b>GRADE_C</b>", style_td_center), Paragraph("&lt; 80%", style_td_center), Paragraph("Nhiều vết xước sâu hoặc viết bút dạ nhiều, mua dùng tạm thời.", style_td), Paragraph("35% giá gốc", style_td_center)],
    ]
    t_cv = Table(cv_table, colWidths=[3.2 * cm, 2.3 * cm, 2.3 * cm, 6.2 * cm, 3.0 * cm])
    t_cv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E5E5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_cv)

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 3: ANTI-FRAUD DIFFERENCE HASHING (dHash)
    # =========================================================================
    story.append(Paragraph("3. THUẬT TOÁN BĂM CẢM NHẬN THỊ GIÁC (dHash) PHÁT HIỆN ẢNH MẠNG CHỐNG GIAN LẬN", style_h1))
    
    story.append(Paragraph("3.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> AI Engine Microservice.<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/ai-engine/app/services/anti_fraud.py</code>.<br/>"
        "• <b>Endpoint API:</b> <code>POST /api/v1/ai/anti-fraud/check</code>.<br/>"
        "• <b>Chức năng:</b> Tự động phát hiện ảnh tải từ Shopee, Lazada, Tiki hoặc ảnh chụp màn hình đăng bán ảo.",
        style_body
    ))

    story.append(Paragraph("3.2. Thuật toán Difference Hashing 64-bit", style_h2))
    story.append(Paragraph(
        "1. <b>Thu nhỏ kích thước (Downsampling):</b> Thu nhỏ ảnh về kích thước cố định (<i>N</i> + 1) &times; <i>N</i> với <i>N</i> = 8, tức ma trận 9 &times; 8 = 72 pixels bằng thuật toán nội suy Lanczos.<br/>"
        "2. <b>Chuyển đổi sang ảnh xám (Grayscale):</b> Loại bỏ độ chói màu sắc, giữ lại cường độ sáng.<br/>"
        "3. <b>So sánh vi phân gradient hàng ngang:</b> So sánh độ sáng giữa 2 điểm ảnh liền kề theo từng hàng:",
        style_body
    ))
    story.append(Paragraph("B(r, c) = 1 &nbsp; nếu &nbsp; P(r, c) &gt; P(r, c + 1); &nbsp;&nbsp;&nbsp;&nbsp; B(r, c) = 0 &nbsp; nếu &nbsp; P(r, c) &le; P(r, c + 1) &nbsp;&nbsp; (với r &in; [0, 7], c &in; [0, 7])", style_formula))
    story.append(Paragraph(
        "4. <b>Tạo chữ ký số Hexadecimal 16 ký tự:</b> 64 bit nhị phân được gom thành 8 bytes và chuyển thành chuỗi 16 ký tự Hex.<br/>"
        "5. <b>Khoảng cách Hamming và nhận dạng ảnh catalog:</b> Độ sai khác giữa 2 ảnh được đo bằng khoảng cách Hamming: <i>D</i><sub><i>H</i></sub>(<i>H</i><sub>1</sub>, <i>H</i><sub>2</sub>) = &Sigma;<sub><i>k</i>=1..64</sub> (<i>b</i><sub>1, <i>k</i></sub> &oplus; <i>b</i><sub>2, <i>k</i></sub>). Nếu <i>D</i><sub><i>H</i></sub> &le; 5, hai ảnh được xác định là trùng lặp. Đồng thời, bộ lọc phát hiện tỷ lệ kích thước catalog vuông chuẩn (800&times;800, 1000&times;1000, 1200&times;1200) cảnh báo yêu cầu sinh viên chụp ảnh thực tế.",
        style_body
    ))

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 4: TIME-DECAY PRICING / DUTCH AUCTION
    # =========================================================================
    story.append(Paragraph("4. MÔ HÌNH SUY GIẢM HÀM MŨ ĐỊNH GIÁ TỰ ĐỘNG THEO THỜI GIAN (TIME-DECAY PRICING)", style_h1))
    
    story.append(Paragraph("4.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> Product Service (Cronjob) và AI Engine (API).<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/product-service/app/Services/TimeDecayPricingService.php</code> và <code>price_agent.py</code>.<br/>"
        "• <b>Endpoint API:</b> <code>POST /api/v1/ai/pricing/decay</code>.<br/>"
        "• <b>Chức năng:</b> Tự động giảm giá đồ dùng học tập cần thanh lý gấp cuối kỳ theo thời gian thực mà không bao giờ dưới Giá sàn.",
        style_body
    ))

    story.append(Paragraph("4.2. Xây dựng công thức toán học phân rã giá trị", style_h2))
    story.append(Paragraph(
        "Hệ thống mô hình hóa quá trình giảm giá theo hàm phân rã liên tục với chu kỳ bán rã (Exponential Half-Life Decay):",
        style_body
    ))
    story.append(Paragraph("P(t) = P<sub>floor</sub> + (P<sub>orig</sub> - P<sub>floor</sub>) &times; e<sup>-&lambda;t</sup>", style_formula))
    story.append(Paragraph(
        "Trong đó:<br/>"
        "• <i>P</i>(<i>t</i>): Giá niêm yết tại thời điểm <i>t</i> giờ sau khi đăng bán.<br/>"
        "• <i>P</i><sub>orig</sub>: Mức giá khởi điểm ban đầu do sinh viên niêm yết.<br/>"
        "• <i>P</i><sub>floor</sub>: Mức giá sàn tối thiểu do người bán thiết lập để bảo toàn vốn.<br/>"
        "• <i>t</i><sub>1/2</sub>: Thời gian bán rã mặc định là 72 giờ (3 ngày). Hằng số suy giảm &lambda; = ln(2) / <i>t</i><sub>1/2</sub> &approx; 0.009627.<br/>"
        "• <b>Bảo đảm bất biến biên (Boundary Invariant):</b> Khi <i>t</i> &rarr; &infin;, <i>P</i>(<i>t</i>) &rarr; <i>P</i><sub>floor</sub> và &forall;<i>t</i> &ge; 0, <i>P</i>(<i>t</i>) &ge; <i>P</i><sub>floor</sub>.",
        style_body
    ))

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 5: DYNAMIC PRICE NEGOTIATION AGENT
    # =========================================================================
    story.append(Paragraph("5. GIẢI THUẬT ĐÀM PHÁN THƯƠNG LƯỢNG GIÁ ĐỘNG DỰA TRÊN ĐIỂM UY TÍN (AI PRICE NEGOTIATOR)", style_h1))
    
    story.append(Paragraph("5.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> AI Engine Microservice.<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/ai-engine/app/services/price_agent.py</code>.<br/>"
        "• <b>Endpoint API:</b> <code>POST /api/v1/ai/pricing/negotiate</code>.<br/>"
        "• <b>Giao diện hiển thị:</b> Modal <b>\"Trả Giá AI\"</b> tại trang chủ chợ sinh viên <code>frontend/student-portal/index.html</code>.",
        style_body
    ))

    story.append(Paragraph("5.2. Mô hình cây quyết định đa tiêu chí", style_h2))
    story.append(Paragraph(
        "Cho người mua đề xuất mức giá <i>P</i><sub>offer</sub> và có Điểm Uy Tín <i>T</i> &in; [0, 1000]. Giá niêm yết hiện tại là <i>P</i><sub>curr</sub> và giá sàn người bán là <i>P</i><sub>floor</sub>. Tỷ số đề xuất giá tương đối và ngưỡng chấp nhận linh hoạt được xác định:",
        style_body
    ))
    story.append(Paragraph("&rho; = (P<sub>offer</sub> - P<sub>floor</sub>) / (P<sub>curr</sub> - P<sub>floor</sub> + 10<sup>-5</sup>), &nbsp;&nbsp;&nbsp;&nbsp; &theta;<sub>accept</sub>(T) = 0.5 - (T / 2000)", style_formula))
    story.append(Paragraph(
        "<b>Quy tắc ra quyết định tự động của AI Agent:</b><br/>"
        "1. <b>Nếu <i>P</i><sub>offer</sub> &ge; <i>P</i><sub>curr</sub>:</b> Chấp thuận ngay lập tức (<code>DECISION = ACCEPT</code>).<br/>"
        "2. <b>Nếu <i>P</i><sub>offer</sub> &lt; <i>P</i><sub>floor</sub>:</b> Mức giá dưới giá sàn. Nếu <i>T</i> &ge; 600 (Hạng Vàng/Kim Cương), AI đưa ra mức giá thỏa hiệp ưu đãi <i>P</i><sub>counter</sub> = <i>P</i><sub>floor</sub> &times; 1.03 (<code>COUNTER_OFFER</code>); ngược lại từ chối (<code>REJECT</code>).<br/>"
        "3. <b>Nếu <i>P</i><sub>floor</sub> &le; <i>P</i><sub>offer</sub> &lt; <i>P</i><sub>curr</sub>:</b> Nếu &rho; &ge; &theta;<sub>accept</sub>(<i>T</i>) &rarr; <code>ACCEPT</code>; ngược lại đề xuất giá trung gian <i>P</i><sub>counter</sub> = Round((<i>P</i><sub>offer</sub> + <i>P</i><sub>curr</sub>) / 2, -3).",
        style_body
    ))

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 6: DYNAMIC QR TOTP 30s ROTATION
    # =========================================================================
    story.append(Paragraph("6. THUẬT TOÁN XÁC THỰC MÃ QR ĐỘNG DYNAMIC QR TOTP XOAY VÒNG 30S (HMAC-SHA256)", style_h1))
    
    story.append(Paragraph("6.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> O2O Hub Logistics Service (Port 8004).<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/hub-service/app/Services/DynamicQREngine.php</code>.<br/>"
        "• <b>Endpoint API:</b> <code>GET /api/v1/hub/lockers</code>.<br/>"
        "• <b>Giao diện hiển thị:</b> Mã QR xoay vòng 30s tại <code>pages/escrow-order.html</code> và máy quét PWA của thủ kho tại <code>frontend/hub-staff-portal/index.html</code>.",
        style_body
    ))

    story.append(Paragraph("6.2. Cơ chế mật mã học HMAC-SHA256 theo cửa sổ thời gian (RFC 6238)", style_h2))
    story.append(Paragraph(
        "Nhằm ngăn chặn triệt để hành vi chụp trộm màn hình để lấy đồ tại Trạm Hub, mã QR được tạo động theo chu kỳ 30 giây:<br/>"
        "1. <b>Cửa sổ thời gian (Time Window):</b> <i>W</i>(<i>t</i>) = &lfloor; <i>t</i> / <i>T</i><sub>step</sub> &rfloor; với <i>T</i><sub>step</sub> = 30 giây.<br/>"
        "2. <b>Chuỗi thông điệp xác thực:</b>",
        style_body
    ))
    story.append(Paragraph("M(t) = OrderCode || UserId || Role || W(t)", style_formula))
    story.append(Paragraph(
        "Trong đó: Ký hiệu || là phép nối chuỗi dữ liệu (Concatenation).<br/>"
        "3. <b>Chữ ký số xác nhận:</b>",
        style_body
    ))
    story.append(Paragraph("&tau;(t) = Truncate<sub>16</sub>( HMAC-SHA256( K<sub>secret</sub>, M(t) ) )", style_formula))
    story.append(Paragraph(
        "4. <b>Cơ chế xác thực chịu lỗi trễ đồng hồ:</b> Máy quét tại Trạm Hub giải mã và kiểm tra &tau;(<i>t</i>) với <i>W</i>(<i>t</i>) và <i>W</i>(<i>t</i>) - 1 (cửa sổ trễ 30 giây) thông qua hàm so sánh bất biến thời gian <code>hash_equals()</code> nhằm chống lại tấn công vét cạn (Timing Attack).",
        style_body
    ))

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 7: SMART ESCROW SAGA FINITE STATE MACHINE
    # =========================================================================
    story.append(Paragraph("7. MÔ HÌNH MÁY TRẠNG THÁI HỮU HẠN & ĐIỀU PHỐI GIAO DỊCH PHÂN TÁN SAGA (SMART ESCROW)", style_h1))
    
    story.append(Paragraph("7.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> Escrow & Payment Microservice (Port 8003).<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/escrow-service/app/Services/EscrowSagaOrchestrator.php</code>.<br/>"
        "• <b>Endpoint API:</b> <code>GET /api/v1/escrow/transactions</code>, <code>POST /api/v1/escrow/saga/advance</code>.<br/>"
        "• <b>Giao diện hiển thị:</b> Thanh tiến trình Stepper 7 bước tại <code>frontend/student-portal/pages/escrow-order.html</code>.",
        style_body
    ))

    story.append(Paragraph("7.2. Định nghĩa máy trạng thái hữu hạn Automaton 7 trạng thái", style_h2))
    story.append(Paragraph(
        "Tiến trình ký quỹ được mô hình hóa thành một bộ máy trạng thái hữu hạn xác định <i>M</i> = (<i>S</i>, &Sigma;, &delta;, <i>s</i><sub>0</sub>, <i>F</i>):<br/>"
        "• Tập 7 trạng thái: <i>S</i> = {INITIATED, ESCROW_LOCKED, STORED_AT_HUB, INSPECTING, RELEASED, DISPUTED, REFUNDED}.<br/>"
        "• Trạng thái khởi đầu: <i>s</i><sub>0</sub> = INITIATED. &nbsp;|&nbsp; Tập trạng thái kết thúc: <i>F</i> = {RELEASED, REFUNDED}.",
        style_body
    ))

    saga_table = [
        [Paragraph("Trạng thái hiện tại", style_th), Paragraph("Sự kiện kích hoạt", style_th), Paragraph("Điều kiện kiểm tra Guard", style_th), Paragraph("Trạng thái kế tiếp", style_th), Paragraph("Hành động Saga đền bù", style_th)],
        [Paragraph("INITIATED", style_td_center), Paragraph("PAY_DEPOSIT", style_td), Paragraph("Tiền vào tài khoản trung gian", style_td), Paragraph("ESCROW_LOCKED", style_td_center), Paragraph("Hủy đơn, hoàn cọc", style_td)],
        [Paragraph("ESCROW_LOCKED", style_td_center), Paragraph("SELLER_CHECKIN", style_td), Paragraph("Thủ kho quét mã QR hợp lệ", style_td), Paragraph("STORED_AT_HUB", style_td_center), Paragraph("Mở tủ trả đồ về người bán", style_td)],
        [Paragraph("STORED_AT_HUB", style_td_center), Paragraph("BUYER_CHECKOUT", style_td), Paragraph("Người mua quét mã nhận đồ", style_td), Paragraph("INSPECTING", style_td_center), Paragraph("Khóa tủ giữ nguyên vị trí", style_td)],
        [Paragraph("INSPECTING", style_td_center), Paragraph("BUYER_SATISFIED", style_td), Paragraph("Người mua bấm xác nhận hài lòng", style_td), Paragraph("<b>RELEASED</b>", style_td_center), Paragraph("Giải ngân tiền cho người bán", style_td)],
        [Paragraph("INSPECTING", style_td_center), Paragraph("RAISE_DISPUTE", style_td), Paragraph("Hàng vỡ hỏng / sai mô tả tại Hub", style_td), Paragraph("DISPUTED", style_td_center), Paragraph("Lập biên bản trung gian", style_td)],
        [Paragraph("DISPUTED", style_td_center), Paragraph("ADMIN_RESOLVE", style_td), Paragraph("Thủ kho xác nhận hàng không đạt", style_td), Paragraph("<b>REFUNDED</b>", style_td_center), Paragraph("Hoàn tiền 100% người mua", style_td)],
    ]
    t_sg = Table(saga_table, colWidths=[2.8 * cm, 3.2 * cm, 4.0 * cm, 3.0 * cm, 4.0 * cm])
    t_sg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E5E5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sg)

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 8: TRUST SCORE ENGINE
    # =========================================================================
    story.append(Paragraph("8. GIẢI THUẬT ĐÁNH GIÁ TÍN NHIỆM & TÍNH ĐIỂM UY TÍN SINH VIÊN (TRUST SCORE ENGINE)", style_h1))
    
    story.append(Paragraph("8.1. Chức năng tương ứng trong hệ thống", style_h2))
    story.append(Paragraph(
        "• <b>Phân hệ phụ trách:</b> Auth & Identity Microservice (Port 8001).<br/>"
        "• <b>Tệp mã nguồn:</b> <code>services/auth-service/app/Services/TrustScoreService.php</code>.<br/>"
        "• <b>Endpoint API:</b> <code>GET /api/v1/auth/users/trust-score</code>.<br/>"
        "• <b>Giao diện hiển thị:</b> Huy hiệu Điểm Uy Tín gắn liền tài khoản sinh viên trên thanh Navbar toàn hệ thống.",
        style_body
    ))

    story.append(Paragraph("8.2. Hàm tích lũy điểm hành vi rời rạc có chặn biên", style_h2))
    story.append(Paragraph(
        "Điểm uy tín của sinh viên tại thời điểm <i>n</i> + 1 là một hàm tích lũy có chặn trên và chặn dưới trong không gian <i>T</i> &in; [0, 1000]:",
        style_body
    ))
    story.append(Paragraph("T<sub>n+1</sub> = max( 0, min( 1000, T<sub>n</sub> + &Sigma;<sub>j</sub> w<sub>j</sub> &times; E<sub>j</sub> ) )", style_formula))
    story.append(Paragraph(
        "Trong đó các trọng số biến cố hành vi được định lượng cụ thể:<br/>"
        "• <i>w</i><sub>1</sub> = +5: Hoàn tất giao dịch O2O đúng hẹn tại Trạm Hub CS1.<br/>"
        "• <i>w</i><sub>2</sub> = +2: Nhận đánh giá 5 sao từ sinh viên đối tác.<br/>"
        "• <i>w</i><sub>3</sub> = -15: Quá hạn 48h không mang đồ đến gửi tại tủ Trạm Hub.<br/>"
        "• <i>w</i><sub>4</sub> = -20: Tự ý hủy kèo sau khi Barter Graph đã ghép cặp thành công.<br/>"
        "• <i>w</i><sub>5</sub> = -30: Cố tình khai gian tình trạng sản phẩm bị camera Hub phát hiện.",
        style_body
    ))

    tier_table = [
        [Paragraph("Thang Điểm Uy Tín", style_th), Paragraph("Phân Hạng Sinh Viên (Tier)", style_th), Paragraph("Quyền Lợi & Đặc Quyền Trong Hệ Thống", style_th)],
        [Paragraph("800 - 1000 Điểm", style_td_center), Paragraph("<b>KIM CƯƠNG</b>", style_td_center), Paragraph("Bảo chứng uy tín 100%, được phép nhận hàng trước không cần cọc tiền.", style_td)],
        [Paragraph("600 - 799 Điểm", style_td_center), Paragraph("<b>VÀNG</b>", style_td_center), Paragraph("Ưu tiên số 1 khi quét chu trình Barter Graph, giảm 50% tiền cọc Escrow.", style_td)],
        [Paragraph("400 - 599 Điểm", style_td_center), Paragraph("<b>BẠC (Tiêu chuẩn)</b>", style_td_center), Paragraph("Hưởng đầy đủ tính năng mua bán, đổi đồ và trả giá AI thông thường.", style_td)],
        [Paragraph("200 - 399 Điểm", style_td_center), Paragraph("<b>ĐỒNG</b>", style_td_center), Paragraph("Phải đặt cọc 100% giá trị món đồ khi tham gia ký quỹ tại Trạm Hub.", style_td)],
        [Paragraph("&lt; 200 Điểm", style_td_center), Paragraph("<b>CẢNH BÁO</b>", style_td_center), Paragraph("Hạn chế quyền đổi đồ, bắt buộc xác minh lại thẻ sinh viên tại Đoàn Trường.", style_td)],
    ]
    t_tr = Table(tier_table, colWidths=[3.2 * cm, 3.8 * cm, 10.0 * cm])
    t_tr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E5E5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_tr)

    story.append(Spacer(1, 6 * mm))

    # =========================================================================
    # PHẦN 9: BẢNG TỔNG HỢP ÁNH XẠ GIẢI THUẬT VÀ MICROSERVICES
    # =========================================================================
    story.append(Paragraph("9. BẢNG TỔNG HỢP ÁNH XẠ GIẢI THUẬT & PHÂN HỆ CHỨC NĂNG", style_h1))
    
    summary_table = [
        [Paragraph("STT", style_th), Paragraph("Tên Thuật Toán / Mô Hình", style_th), Paragraph("Microservice Phụ Trách", style_th), Paragraph("API Endpoint Cung Cấp", style_th), Paragraph("Chức Năng Nghiệp Vụ", style_th)],
        [Paragraph("1", style_td_center), Paragraph("Johnson's Directed Cycle & Zero-Sum", style_td), Paragraph("ai-engine (Port 8005)", style_td), Paragraph("POST /api/v1/ai/barter/solve-cycles", style_td), Paragraph("Ghép vòng tròn đổi đồ 3 chiều và tính toán bù trừ tiền mặt", style_td)],
        [Paragraph("2", style_td_center), Paragraph("Spatial Gradient & HSV Color Defect", style_td), Paragraph("ai-engine (Port 8005)", style_td), Paragraph("POST /api/v1/ai/cv/inspect", style_td), Paragraph("Thị giác máy tính đo độ hao mòn, phân hạng Grade S/A/B/C", style_td)],
        [Paragraph("3", style_td_center), Paragraph("Difference Hashing (dHash 64-bit)", style_td), Paragraph("ai-engine (Port 8005)", style_td), Paragraph("POST /api/v1/ai/anti-fraud/check", style_td), Paragraph("Chống ảnh mạng catalog Shopee/Lazada, bảo vệ giao dịch", style_td)],
        [Paragraph("4", style_td_center), Paragraph("Exponential Half-Life Decay Pricing", style_td), Paragraph("product-service (8002)", style_td), Paragraph("POST /api/v1/ai/pricing/decay", style_td), Paragraph("Tự động giảm giá theo giờ thanh lý giáo trình cuối kỳ", style_td)],
        [Paragraph("5", style_td_center), Paragraph("Multi-Criteria Price Negotiator Agent", style_td), Paragraph("ai-engine (Port 8005)", style_td), Paragraph("POST /api/v1/ai/pricing/negotiate", style_td), Paragraph("Trợ lý AI tự động đàm phán giá theo Điểm Uy Tín 24/7", style_td)],
        [Paragraph("6", style_td_center), Paragraph("HMAC-SHA256 Dynamic QR TOTP (30s)", style_td), Paragraph("hub-service (Port 8004)", style_td), Paragraph("GET /api/v1/hub/lockers", style_td), Paragraph("Sinh và giải mã QR xoay 30s chống chụp trộm màn hình", style_td)],
        [Paragraph("7", style_td_center), Paragraph("Distributed Saga 7-State FSM", style_td), Paragraph("escrow-service (8003)", style_td), Paragraph("POST /api/v1/escrow/saga/advance", style_td), Paragraph("Đóng băng tiền cọc ký quỹ và giải ngân khi hài lòng", style_td)],
        [Paragraph("8", style_td_center), Paragraph("Accumulative Trust Score Engine", style_td), Paragraph("auth-service (Port 8001)", style_td), Paragraph("GET /api/v1/auth/users/trust-score", style_td), Paragraph("Đánh giá tín nhiệm sinh viên HUNRE và phân cấp đặc quyền", style_td)],
    ]
    t_sm = Table(summary_table, colWidths=[0.8 * cm, 4.3 * cm, 3.4 * cm, 4.5 * cm, 4.0 * cm])
    t_sm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5E5E5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sm)

    # Build PDF
    doc.build(story, canvasmaker=MonochromeNumberedCanvas)
    sys.stdout.write("PDF BUILD SUCCESSFUL\n")

if __name__ == '__main__':
    out_path = "d:/Intel/Project/crs-microservices/BTL/tailieu/TAI_LIEU_TOAN_HOC_VA_GIAI_THUAT_HE_THONG.pdf"
    build_pdf(out_path)
