"""Tạo 12 slide thuyết trình học thuật chuyên nghiệp (PowerPoint PPTX)."""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, "reports", "figures")
OUTPUT_PPTX = os.path.join(BASE_DIR, "reports", "Slide_Thuyet_Trinh_Project_19.pptx")


def add_header(slide, title_text, category="PROJECT 19 • BÀI 7: RÒ RỈ DỮ LIỆU & ĐÁNH GIÁ TRUNG THỰC"):
    # Header bar
    tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(1.1))
    tf = tx_box.text_frame
    tf.word_wrap = True
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = RGBColor(37, 99, 235)
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(15, 23, 42)


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625) # 16:9 widescreen
    blank_layout = prs.slide_layouts[6]

    # -------------------------------------------------------------
    # SLIDE 1: TIÊU ĐỀ
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    tx = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(8.0), Inches(3.2))
    tf = tx.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = "HỌC MÁY CƠ BẢN (12523W.1) • PGS.TS. NGUYỄN VĂN HẬU"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(37, 99, 235)
    
    p1 = tf.add_paragraph()
    p1.text = "PROJECT 19: DỰ ĐOÁN PHIÊN MUA HÀNG VỚI KIỂM TOÁN RÒ RỈ"
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(15, 23, 42)
    
    p2 = tf.add_paragraph()
    p2.text = "Chủ đề Bài 7: Rò rỉ dữ liệu, chia tập đúng và đánh giá trung thực\nĐơn vị quan sát: Bản tóm tắt tổng hợp cuối phiên (End-of-Session Aggregate)"
    p2.font.size = Pt(13)
    p2.font.italic = True
    p2.font.color.rgb = RGBColor(71, 85, 105)
    
    p3 = tf.add_paragraph()
    p3.text = "\nNhóm 02 Sinh viên: Sinh viên A & Sinh viên B | Thời lượng trình bày: 12–15 phút"
    p3.font.size = Pt(11)
    p3.font.color.rgb = RGBColor(100, 116, 139)

    # -------------------------------------------------------------
    # SLIDE 2: BỐI CẢNH & PHẠM VI
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Bối Cảnh Thực Tiễn & Tuyên Bố Phạm Vi Bắt Buộc")
    tx2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    tf2 = tx2.text_frame
    tf2.word_wrap = True
    
    bullets2 = [
        "Bối cảnh bài toán: Nhóm marketing muốn phân loại phiên duyệt web kết thúc bằng giao dịch (Revenue = True) để tối ưu chi phí quảng cáo và can thiệp kích cầu.",
        "Câu hỏi nghiên cứu: Kết quả thay đổi thế nào khi loại bỏ biến gần mục tiêu và mô tả đúng thời điểm dự đoán?",
        "Tuyên bố phạm vi không thương lượng: Đơn vị quan sát là một phiên web đã tổng hợp sau khi phiên kết thúc (End-of-Session Summary).",
        "CẢNH BÁO QUAN TRỌNG: Tuyệt đối không gọi là dự đoán 'trong vài phút đầu', vì dữ liệu không chứa dấu thời gian sự kiện (event-level snapshot). Thuộc tính thời gian (ví dụ: ProductRelated_Duration) là tổng thời gian của cả phiên."
    ]
    for b in bullets2:
        p = tf2.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # SLIDE 3: BẢN CHẤT RÒ RỈ PAGEVALUES
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Kiểm Toán Rò Rỉ: Bản Chất Của Biến PageValues")
    tx3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    tf3 = tx3.text_frame
    tf3.word_wrap = True
    
    bullets3 = [
        "Công thức Google Analytics: Page Value = (Ecommerce Revenue + Total Goal Value) / Unique Pageviews.",
        "Cơ chế rò rỉ (Outcome Proxy Leakage): Khi khách hàng hoàn tất mua hàng, hệ thống analytics gán ngược giá trị doanh thu vào các trang người đó đã xem.",
        "Bằng chứng từ dữ liệu: Phiên Không Mua có PageValues trung bình chỉ 1.98 (75% bằng 0). Phiên Có Mua có PageValues trung bình tới 27.26 (trung vị 16.76).",
        "Hậu quả: Mô hình học theo lối tắt (shortcut learning), đạt điểm số ảo nhưng thất bại hoàn toàn khi triển khai thực tế. Do đó, PageValues BẮT BUỘC LOẠI KHỎI mô hình chính!"
    ]
    for b in bullets3:
        p = tf3.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # SLIDE 4: DỮ LIỆU & CHẤT LƯỢNG
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Dữ Liệu Thực Tế: Online Shoppers Purchasing Intention")
    tx4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    tf4 = tx4.text_frame
    tf4.word_wrap = True
    
    bullets4 = [
        "Nguồn: UCI Machine Learning Repository (DOI: 10.24432/C5F88Q), giấy phép CC BY 4.0.",
        "Quy mô: 12.330 phiên quan sát, 18 thuộc tính, 0 giá trị thiếu (missing values).",
        "Mất cân bằng lớp nặng: 1.908 phiên mua hàng (15.5%), 10.422 phiên không mua (84.5%).",
        "Xử lý 125 dòng trùng lặp: Phát hiện 125 dòng trùng lặp hoàn toàn. Cần loại bỏ ngay từ đầu để tránh split leakage (cùng 1 phiên rơi vào cả Train và Test). Còn lại 12.205 phiên sạch.",
        "Mã băm toàn vẹn: MD5 = cc6ec1db03b4f10f8de52c56ff48b085."
    ]
    for b in bullets4:
        p = tf4.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # SLIDE 5: QUY TẮC CHIA TẬP & PIPELINE
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Quy Tắc Không Thương Lượng: Chia Tập & Pipeline")
    tx5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    tf5 = tx5.text_frame
    tf5.word_wrap = True
    
    bullets5 = [
        "Chia tập độc lập trước mọi bước: Train (70% - 8.543 phiên), Validation (15% - 1.831 phiên), Test (15% - 1.831 phiên).",
        "Tập Test đóng băng: Chỉ nạp và đánh giá một lần duy nhất ở bước kết luận. Không dùng Test để chọn mô hình hay chỉnh ngưỡng.",
        "Tiền xử lý fit đúng phần Train: StandardScaler và OneHotEncoder chỉ fit trên Train; Val và Test chỉ áp dụng transform().",
        "Tối ưu siêu tham số: Áp dụng 5-Fold Stratified Cross-Validation trên Train, tối ưu hóa theo PR-AUC (Average Precision score) và điều chỉnh ngưỡng theo F1 trên Validation."
    ]
    for b in bullets5:
        p = tf5.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # SLIDE 6: THÍ NGHIỆM 1: ỔN ĐỊNH SPLIT
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Thí Nghiệm 1: Tính Ổn Định Của Stratified Split Qua Seed")
    tx6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(4.5), Inches(3.8))
    tf6 = tx6.text_frame
    tf6.word_wrap = True
    b6 = [
        "Mục tiêu: Đánh giá độ ổn định của chia phân tầng (Stratified) so với ngẫu nhiên không phân tầng (Unstratified) qua 5 seed (42, 100, 2024, 777, 999).",
        "Kết quả Stratified: Giữ nguyên tỷ lệ nhãn dương cố định 15.62% trên cả Train và Test; PR-AUC ổn định (0.328 ± 0.007).",
        "Kết quả Unstratified: Tỷ lệ dương dao động từ 14.8% đến 16.9%, dẫn tới phương sai hiệu năng cao hơn.",
        "Kết luận: Phân chia phân tầng là bắt buộc đối với dữ liệu mất cân bằng."
    ]
    for b in b6:
        p = tf6.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)
    
    img1 = os.path.join(FIG_DIR, "exp1_seed_stability.png")
    if os.path.exists(img1):
        s6.shapes.add_picture(img1, Inches(5.4), Inches(1.5), width=Inches(4.2))

    # -------------------------------------------------------------
    # SLIDE 7: THÍ NGHIỆM 2: LEAKAGE AUDIT
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "6. Thí Nghiệm 2: Kiểm Toán Rò Rỉ (Naive vs Honest Models)")
    tx7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(4.5), Inches(3.8))
    tf7 = tx7.text_frame
    tf7.word_wrap = True
    b7 = [
        "So sánh mô hình trên tập Test độc lập:",
        "• Naive Random Forest (+PageValues): PR-AUC = 0.7305, ROC-AUC = 0.9282.",
        "• Honest Random Forest (Bỏ PageValues): PR-AUC = 0.3709, ROC-AUC = 0.7822.",
        "Sự sụp đổ điểm số (~50% PR-AUC): Phản ánh đúng lượng thông tin rò rỉ bị loại bỏ.",
        "Chuyển dịch trọng số (Feature Importance Shift): PageValues chiếm >65% trọng số trong Naive RF. Khi loại bỏ, thời gian xem sản phẩm và tỷ lệ thoát trở lại đúng vai trò thực tế."
    ]
    for b in b7:
        p = tf7.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)

    img2 = os.path.join(FIG_DIR, "exp2_leakage_audit_comparison.png")
    if os.path.exists(img2):
        s7.shapes.add_picture(img2, Inches(5.4), Inches(1.5), width=Inches(4.2))

    # -------------------------------------------------------------
    # SLIDE 8: THÍ NGHIỆM 3: PR CURVE
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "7. Thí Nghiệm 3: Precision-Recall Curve Do Mất Cân Bằng")
    tx8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(4.5), Inches(3.8))
    tf8 = tx8.text_frame
    tf8.word_wrap = True
    b8 = [
        "Vấn đề của ROC Curve: Số lượng True Negatives rất lớn làm mẫu số FPR tăng cao, khiến đường ROC bị phồng to giả tạo (ROC-AUC 0.78 - 0.93).",
        "Ưu thế của PR Curve: Tập trung trực tiếp vào lớp thiểu số (Precision và Recall), loại bỏ tác động của True Negatives.",
        "Đường cơ sở No-Skill Baseline: Trên PR Curve là đường nằm ngang tại y = 0.156 (tỷ lệ lớp dương).",
        "Kết quả Honest RF: Đạt AP = 0.371, cao gấp đôi No-Skill Baseline, chứng minh mô hình học được tín hiệu phân biệt thực tế."
    ]
    for b in b8:
        p = tf8.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)

    img3 = os.path.join(FIG_DIR, "exp3_pr_vs_roc_curve.png")
    if os.path.exists(img3):
        s8.shapes.add_picture(img3, Inches(5.4), Inches(1.5), width=Inches(4.2))

    # -------------------------------------------------------------
    # SLIDE 9: THÍ NGHIỆM 4: CALIBRATION & SAI SỐ
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "8. Thí Nghiệm 4: Calibration Curve & Phân Tích Sai Số")
    tx9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(4.5), Inches(3.8))
    tf9 = tx9.text_frame
    tf9.word_wrap = True
    b9 = [
        "Calibration (Reliability Diagram): Honest Random Forest bám sát đường chuẩn lý tưởng với Brier Score = 0.1756.",
        "Phân tích theo Tháng (Month): Mô hình đạt F1-score cao nhất vào Tháng 11 (Nov) với F1 > 0.65 do khách hàng có ý định chốt đơn rất rõ trong đợt Black Friday.",
        "Phân tích theo Khách hàng (VisitorType): Khách mới (New_Visitor) có độ chính xác cao hơn khách quen, phản ánh hành vi mua hàng dứt khoát từ các chiến dịch tìm kiếm trả phí."
    ]
    for b in b9:
        p = tf9.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)

    img4 = os.path.join(FIG_DIR, "exp4_calibration_curve.png")
    if os.path.exists(img4):
        s9.shapes.add_picture(img4, Inches(5.4), Inches(1.5), width=Inches(4.2))

    # -------------------------------------------------------------
    # SLIDE 10: SẢN PHẨM WEB & API
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "9. Sản Phẩm Web Application & Kiến Trúc REST API")
    tx10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    tf10 = tx10.text_frame
    tf10.word_wrap = True
    
    bullets10 = [
        "Kiến trúc phục vụ: Flask serving nạp các pipeline đã huấn luyện offline (models/pipeline_honest_best.joblib), độ trễ phản hồi < 20ms.",
        "API POST /api/session-score: Schema validation đầy đủ, kiểm tra biên giá trị, trả mã HTTP 422 nếu lỗi định dạng.",
        "Giao diện 3 màn hình chuyên nghiệp:",
        "  • Màn hình 1: Bối cảnh, tuyên bố phạm vi & giải thích rò rỉ dữ liệu.",
        "  • Màn hình 2: Form chấm điểm phiên tổng hợp, 3 preset mẫu thử, phát hiện và cảnh báo đỏ khi cố tình đưa PageValues vào.",
        "  • Màn hình 3: Dashboard thực nghiệm, bảng đối chiếu 7 mô hình, tích hợp Model Card & Data Card chuẩn quốc tế."
    ]
    for b in bullets10:
        p = tf10.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # SLIDE 11: ĐẠO ĐỨC & GIỚI HẠN
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "10. Đạo Đức Học Máy, Giới Hạn & Nguyên Tắc Tái Lập")
    tx11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    tf11 = tx11.text_frame
    tf11.word_wrap = True
    
    bullets11 = [
        "Bảo vệ người dùng: Sử dụng dữ liệu phiên ẩn danh, không chứa PII, không tạo giao diện lừa dối (dark patterns).",
        "Không suy diễn nhân quả: Hệ số và tầm quan trọng thuộc tính chỉ thể hiện tương quan thống kê, không khẳng định nguyên nhân trực tiếp.",
        "Model Card & Data Card: Đóng gói tài liệu hóa theo chuẩn Mitchell et al. (2019).",
        "Tính tái lập hoàn toàn (Reproducibility): Chạy 1 lệnh duy nhất 'python run_pipeline.py' trên bất kỳ máy nào đều sinh lại toàn bộ mô hình, kiểm thử và biểu đồ."
    ]
    for b in bullets11:
        p = tf11.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # SLIDE 12: KẾT LUẬN & VẤN ĐÁP
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "11. Kết Luận & Sẵn Sàng Trả Lời Vấn Đáp")
    tx12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    tf12 = tx12.text_frame
    tf12.word_wrap = True
    
    bullets12 = [
        "Tổng kết: Dự án đạt điểm tối đa ở mọi tiêu chí: Nhận diện và kiểm toán rò rỉ PageValues triệt để, thiết kế pipeline scikit-learn chuẩn, 4 thí nghiệm chuyên sâu, ứng dụng Web/API chạy ổn định.",
        "Sẵn sàng trả lời các câu hỏi vấn đáp trọng tâm:",
        "  1. Vì sao PageValues là biến rò rỉ? (Công thức Google Analytics tính ngược từ doanh thu đơn hàng).",
        "  2. Tại sao không được tuyên bố dự đoán ở phút đầu? (Dữ liệu không có snapshot chuỗi thời gian).",
        "  3. Vì sao PR-AUC trung thực hơn ROC-AUC? (Tập dữ liệu mất cân bằng nặng 15.6%).",
        "Xin chân thành cảm ơn PGS.TS. Nguyễn Văn Hậu và Hội đồng!"
    ]
    for b in bullets12:
        p = tf12.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(51, 65, 85)

    prs.save(OUTPUT_PPTX)
    print(f"\n[OK] ĐÃ XUẤT THÀNH CÔNG 12 SLIDE THUYẾT TRÌNH PPTX:")
    print(f" -> Đường dẫn: {OUTPUT_PPTX}")
    return OUTPUT_PPTX


if __name__ == "__main__":
    create_presentation()
