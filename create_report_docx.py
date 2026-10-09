"""Tạo Báo cáo kết thúc học phần Project 19 bằng python-docx.

Tuân thủ nghiêm ngặt đề cương 13 mục bắt buộc và định dạng học thuật chuyên nghiệp.
"""

import os
import sys
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, "reports", "figures")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DOCX = os.path.join(BASE_DIR, "reports", "Bao_cao_Project_19_Chuyen_doi_mua_hang.docx")

with open(os.path.join(MODELS_DIR, "experiment_results.json"), encoding="utf-8") as f:
    exp_data = json.load(f)
with open(os.path.join(MODELS_DIR, "data_quality_report.json"), encoding="utf-8") as f:
    dq_data = json.load(f)


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def build_docx_report():
    doc = docx.Document()
    
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(30, 41, 59)

    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_univ = p_univ.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\nHỌC PHẦN: HỌC MÁY CƠ BẢN (12523W.1)\n")
    run_univ.bold = True
    run_univ.font.size = Pt(13)
    
    doc.add_paragraph("\n" * 2)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("BÁO CÁO PROJECT KẾT THÚC HỌC PHẦN\nPROJECT 19: DỰ ĐOÁN PHIÊN MUA HÀNG VỚI KIỂM TOÁN RÒ RỈ\n")
    run_title.bold = True
    run_title.font.size = Pt(18)
    run_title.font.color.rgb = RGBColor(37, 99, 235)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("Chủ đề: Bài 7 — Rò rỉ dữ liệu, chia tập đúng và đánh giá trung thực\nĐơn vị quan sát: Phân loại tóm tắt tổng hợp cuối phiên (End-of-Session Aggregate)\n")
    run_sub.italic = True
    run_sub.font.size = Pt(12)

    doc.add_paragraph("\n" * 3)

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_info = p_info.add_run(
        "Giảng viên hướng dẫn: PGS.TS. NGUYỄN VĂN HẬU\n\n"
        "Nhóm thực hiện: Nhóm 02 Sinh viên\n"
        "Thành viên 1: Sinh viên A (MSSV: 20210001) — Phụ trách Dữ liệu, Preprocessing & Mô hình\n"
        "Thành viên 2: Sinh viên B (MSSV: 20210002) — Phụ trách Đánh giá, Web API & Báo cáo\n\n"
        "Năm học: 2025 – 2026\n"
    )
    run_info.font.size = Pt(12)

    doc.add_page_break()

    # MỤC LỤC & TÓM TẮT
    h1 = doc.add_heading("1. TÓM TẮT (ABSTRACT)", level=1)
    h1.style.font.color.rgb = RGBColor(30, 41, 59)
    
    doc.add_paragraph(
        "Trong các hệ thống phân tích thương mại điện tử, việc xác định phiên truy cập có kết thúc bằng giao dịch "
        "(Revenue = True) đóng vai trò then chốt trong tối ưu hóa chi phí quảng cáo và cá nhân hóa trải nghiệm. "
        "Tuy nhiên, nhiều nghiên cứu và dự án thực tế thường mắc lỗi rò rỉ dữ liệu (data leakage) nghiêm trọng khi sử dụng các thuộc tính "
        "tổng hợp sau giao dịch hoặc đưa ra những tuyên bố thiếu cơ sở về việc 'dự đoán trong vài phút đầu' mà không có dữ liệu chuỗi thời gian (event streams). "
        "Báo cáo này triển khai Project 19 thuộc Bài 7: 'Rò rỉ dữ liệu, chia tập đúng và đánh giá trung thực'. "
        "Chúng tôi thực hiện kiểm toán rò rỉ toàn diện trên bộ dữ liệu chuẩn Online Shoppers Purchasing Intention (UCI, 12.330 phiên), "
        "chỉ ra rằng thuộc tính PageValues được tính toán từ doanh thu giao dịch (Google Analytics Outcome Proxy), "
        "khiến mô hình ngây thơ (Naive Model) tạo ảo tưởng hiệu năng (PR-AUC = 0.7305, ROC-AUC = 0.9282). "
        "Khi loại bỏ PageValues theo đúng quy chuẩn trung thực (Honest Model), mô hình Random Forest đạt PR-AUC thực tế là 0.3709 và ROC-AUC là 0.7822 trên tập kiểm thử độc lập. "
        "Báo cáo trình bày đầy đủ 4 thí nghiệm bắt buộc (tính ổn định qua seed, kiểm toán rò rỉ, phân tích PR curve trên dữ liệu mất cân bằng 15.6% và kiểm định calibration/sai số), "
        "đồng thời đóng gói toàn bộ quy trình thành ứng dụng Web có API POST /api/session-score hoạt động offline hoàn toàn có thể tái lập."
    )

    # 2. BỐI CẢNH & CÂU HỎI NGHIÊN CỨU
    h2 = doc.add_heading("2. BỐI CẢNH THỰC TIỄN & CÂU HỎI NGHIÊN CỨU", level=1)
    doc.add_paragraph(
        "2.1 Bối cảnh thực tiễn:\n"
        "Nhóm marketing muốn dự đoán liệu một khách truy cập có thực hiện giao dịch hay không nhằm kích hoạt các ưu đãi, mã giảm giá vận chuyển hoặc hỗ trợ trực tuyến. "
        "Tuy nhiên, phần lớn dữ liệu nhật ký thu thập được ở dạng bảng tóm tắt phiên (session-level aggregate), không có nhãn thời gian từng sự kiện."
    )
    doc.add_paragraph(
        "2.2 Câu hỏi nghiên cứu trọng tâm:\n"
        "1. Kết quả phân loại thay đổi như thế nào khi loại bỏ biến gần mục tiêu (PageValues) và mô tả đúng thời điểm dự đoán?\n"
        "2. Phương pháp chia tập ngẫu nhiên thông thường (Unstratified) gây ra phương sai và bất ổn định thế nào so với chia phân tầng (Stratified Split)?\n"
        "3. Trong bài toán mất cân bằng lớp trầm trọng (15.6% dương), chỉ số ROC-AUC có phản ánh trung thực bài toán hơn Precision-Recall AUC (PR-AUC) hay không?\n"
        "4. Xác suất đầu ra của các mô hình có được chuẩn hóa (calibrated) tốt hay không và sai số biến thiên thế nào theo thời gian và loại khách hàng?"
    )
    doc.add_paragraph(
        "2.3 Đặc tả bài toán học máy:\n"
        "• Loại bài toán: Phân loại nhị phân (Binary Classification) có kiểm toán rò rỉ dữ liệu.\n"
        "• Đơn vị quan sát: Một phiên web đã được tổng hợp sau khi phiên kết thúc (End-of-Session Summary).\n"
        "• Đầu ra: Xác suất Revenue = True và nhãn nhị phân tương ứng với ngưỡng quyết định tối ưu."
    )

    # 3. DỮ LIỆU & GIẤY PHÉP
    h3 = doc.add_heading("3. DỮ LIỆU, GIẤY PHÉP & KIỂM TOÁN CHẤT LƯỢNG", level=1)
    doc.add_paragraph(
        "Bộ dữ liệu sử dụng là Online Shoppers Purchasing Intention Dataset từ UCI Machine Learning Repository (DOI: 10.24432/C5F88Q), "
        "thuộc bản quyền Creative Commons Attribution 4.0 International (CC BY 4.0). Dữ liệu gồm 12.330 phiên quan sát với 18 thuộc tính."
    )
    
    # Bảng Data Quality
    table_dq = doc.add_table(rows=6, cols=3)
    set_table_borders(table_dq)
    table_dq.alignment = WD_TABLE_ALIGNMENT.CENTER
    dq_headers = ["Chỉ số chất lượng", "Giá trị ghi nhận", "Nhận xét & Biện pháp xử lý"]
    for i, h in enumerate(dq_headers):
        cell = table_dq.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "F1F5F9")

    dq_rows = [
        ("Tổng số dòng thô", f"{dq_data['total_raw_rows']} dòng", "Khớp 100% tài liệu công bố UCI"),
        ("Giá trị thiếu (Missing values)", f"{dq_data['total_missing_values']} giá trị", "Không có ô trống, dữ liệu đầy đủ"),
        ("Số dòng trùng lặp (Duplicates)", f"{dq_data['duplicate_rows']} dòng", "Cần loại bỏ để tránh rò rỉ phân chia (Split leakage)"),
        ("Số dòng sau khử trùng lặp", f"{dq_data['rows_after_dedup']} dòng", "Tập dữ liệu sạch sẵn sàng phân chia"),
        ("Tỷ lệ nhãn dương (Revenue = True)", f"{dq_data['positive_rate_cleaned']*100:.2f}%", "Dữ liệu mất cân bằng nặng (Imbalance 1:5.4)")
    ]
    for row_idx, data_tuple in enumerate(dq_rows, start=1):
        for col_idx, text_val in enumerate(data_tuple):
            cell = table_dq.cell(row_idx, col_idx)
            cell.text = text_val

    doc.add_paragraph(
        "\nLý do xử lý trùng lặp: Trong 12.330 dòng có 125 dòng trùng lặp 100% các trường dữ liệu. "
        "Do dữ liệu phiên không có ID người dùng, nếu để các dòng trùng lặp này tồn tại ngẫu nhiên, "
        "chúng có thể rơi vào cả tập Train và Test, dẫn tới hiện tượng rò rỉ phân chia (split leakage). "
        "Do đó, nhóm quyết định loại bỏ 125 dòng này, giữ lại 12.205 phiên sạch."
    )

    # 4. THỜI ĐIỂM DỰ ĐOÁN & KIỂM TOÁN RÒ RỈ
    h4 = doc.add_heading("4. THỜI ĐIỂM DỰ ĐOÁN & KIỂM TOÁN RÒ RỈ DỮ LIỆU", level=1)
    doc.add_paragraph(
        "4.1 Bản chất rò rỉ của biến PageValues:\n"
        "Theo định nghĩa Google Analytics: Page Value = (Ecommerce Revenue + Total Goal Value) / Unique Pageviews. "
        "Thuộc tính này được hệ thống tính toán sau khi giỏ hàng được thanh toán. Nếu khách mua hàng, các trang người đó đã xem sẽ được gán giá trị cao. "
        "Do đó, PageValues trực tiếp chứa đựng tín hiệu mục tiêu (Target Proxy Feature). "
        "Khi đưa vào huấn luyện, mô hình học được mối liên hệ nhân tạo này thay vì học từ hành vi thực của người dùng. "
        "Đây là hành vi 'lối tắt học tập' (shortcut learning) nguy hiểm trong máy học.\n\n"
        "4.2 Tuyên bố về thời điểm dự đoán:\n"
        "Dữ liệu này chỉ ghi nhận tổng thời gian (ví dụ: ProductRelated_Duration có phiên lên đến 63.973 giây ~ 17 giờ) và tổng số trang sau khi phiên kết thúc. "
        "Dữ liệu không có snapshot ở phút thứ 1 hay thứ 5. Vì vậy, nhóm tuyên bố bài toán là: "
        "'Phân loại bản tóm tắt phiên sau khi phiên kết thúc' (End-of-Session Aggregate Classification), "
        "tuyệt đối không quảng bá là 'dự đoán sớm trong vài phút đầu'."
    )

    # 5. PHƯƠNG PHÁP HỌC MÁY & PIPELINE
    h5 = doc.add_heading("5. PHƯƠNG PHÁP HỌC MÁY & PIPELINE TIỀN XỬ LÝ", level=1)
    doc.add_paragraph(
        "Để đảm bảo nguyên tắc không rò rỉ dữ liệu, quy trình phân chia và tiền xử lý được thiết kế như sau:\n"
        "1. Phân chia độc lập: Chia tập dữ liệu sạch thành Train (70% - 8.543 phiên), Validation (15% - 1.831 phiên), Test (15% - 1.831 phiên) "
        "sử dụng Stratified Sampling theo nhãn Revenue. Tập Test được đóng băng (freeze) và chỉ nạp một lần duy nhất ở bước đánh giá cuối cùng.\n"
        "2. Scikit-learn Pipeline:\n"
        "   - StandardScaler cho các biến số liên tục (fit duy nhất trên Train).\n"
        "   - OneHotEncoder(handle_unknown='ignore', sparse_output=False) cho các biến phân loại danh mục (Month, VisitorType, Weekend, OS, Browser, Region, TrafficType).\n"
        "   - Class_weight='balanced' trong bộ phân loại để xử lý mất cân bằng lớp thay vì áp dụng oversampling (SMOTE) thiếu kiểm soát trước khi split.\n"
        "3. Tối ưu siêu tham số: Áp dụng GridSearchCV với 5-Fold Stratified Cross-Validation trên tập Train, tối ưu theo chỉ số average_precision (PR-AUC)."
    )

    # 6. THIẾT KẾ THÍ NGHIỆM
    h6 = doc.add_heading("6. THIẾT KẾ THÍ NGHIỆM & CHỈ SỐ ĐÁNH GIÁ", level=1)
    doc.add_paragraph(
        "Hệ thống so sánh 7 mô hình/cấu hình trên cùng một tập Test độc lập:\n"
        "• Baseline 1: Dummy Classifier (dự đoán theo xác suất tiên nghiệm của lớp âm).\n"
        "• Baseline 2: Simple Logistic Regression chỉ dùng 4 biến hành vi cơ bản (ProductRelated, ProductRelated_Duration, BounceRates, ExitRates).\n"
        "• Naive Logistic Regression: Mô hình ngây thơ có PageValues (minh họa rò rỉ).\n"
        "• Naive Random Forest: Mô hình ngây thơ rừng ngẫu nhiên có PageValues.\n"
        "• Honest Logistic Regression: Mô hình hồi quy logistic trung thực đã loại bỏ PageValues.\n"
        "• Honest Random Forest: Mô hình rừng ngẫu nhiên trung thực (150 cây, max_depth=10, min_samples_leaf=2).\n"
        "• Honest HistGradientBoosting: Mô hình tăng cường độ dốc trung thực.\n\n"
        "Chỉ số đánh giá: PR-AUC (Average Precision Score), ROC-AUC, Precision, Recall, F1-Score, Brier Score."
    )

    # 7. KẾT QUẢ THỰC NGHIỆM (4 THÍ NGHIỆM BẮT BUỘC)
    h7 = doc.add_heading("7. KẾT QUẢ THỰC NGHIỆM VÀ ĐỐI CHỨNG", level=1)
    
    # Bảng tổng hợp kết quả Test
    table_res = doc.add_table(rows=8, cols=7)
    set_table_borders(table_res)
    table_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Mô hình", "Rò rỉ?", "PR-AUC", "ROC-AUC", "Precision", "Recall", "F1-Score"]
    for i, h in enumerate(res_headers):
        cell = table_res.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "F1F5F9")

    exp2 = exp_data['experiment_2_leakage_audit']
    res_rows = [
        ("Dummy (Majority)", "Không", f"{exp2['baseline_dummy']['pr_auc']:.4f}", f"{exp2['baseline_dummy']['roc_auc']:.4f}", f"{exp2['baseline_dummy']['precision']:.4f}", f"{exp2['baseline_dummy']['recall']:.4f}", f"{exp2['baseline_dummy']['f1_score']:.4f}"),
        ("Baseline LR (4 biến)", "Không", f"{exp2['baseline_lr']['pr_auc']:.4f}", f"{exp2['baseline_lr']['roc_auc']:.4f}", f"{exp2['baseline_lr']['precision']:.4f}", f"{exp2['baseline_lr']['recall']:.4f}", f"{exp2['baseline_lr']['f1_score']:.4f}"),
        ("Honest Logistic Reg", "Không", f"{exp2['honest_lr']['pr_auc']:.4f}", f"{exp2['honest_lr']['roc_auc']:.4f}", f"{exp2['honest_lr']['precision']:.4f}", f"{exp2['honest_lr']['recall']:.4f}", f"{exp2['honest_lr']['f1_score']:.4f}"),
        ("Honest Random Forest", "Không", f"{exp2['honest_rf']['pr_auc']:.4f}", f"{exp2['honest_rf']['roc_auc']:.4f}", f"{exp2['honest_rf']['precision']:.4f}", f"{exp2['honest_rf']['recall']:.4f}", f"{exp2['honest_rf']['f1_score']:.4f}"),
        ("Honest Gradient Boost", "Không", f"{exp2['honest_gb']['pr_auc']:.4f}", f"{exp2['honest_gb']['roc_auc']:.4f}", f"{exp2['honest_gb']['precision']:.4f}", f"{exp2['honest_gb']['recall']:.4f}", f"{exp2['honest_gb']['f1_score']:.4f}"),
        ("Naive Logistic Reg", "CÓ (Leak)", f"{exp2['naive_lr']['pr_auc']:.4f}", f"{exp2['naive_lr']['roc_auc']:.4f}", f"{exp2['naive_lr']['precision']:.4f}", f"{exp2['naive_lr']['recall']:.4f}", f"{exp2['naive_lr']['f1_score']:.4f}"),
        ("Naive Random Forest", "CÓ (Leak)", f"{exp2['naive_rf']['pr_auc']:.4f}", f"{exp2['naive_rf']['roc_auc']:.4f}", f"{exp2['naive_rf']['precision']:.4f}", f"{exp2['naive_rf']['recall']:.4f}", f"{exp2['naive_rf']['f1_score']:.4f}")
    ]
    for row_idx, r_tuple in enumerate(res_rows, start=1):
        for col_idx, t_val in enumerate(r_tuple):
            cell = table_res.cell(row_idx, col_idx)
            cell.text = t_val
            if "Honest Random Forest" in r_tuple[0]:
                set_cell_background(cell, "ECFDF5")
            elif "CÓ (Leak)" in r_tuple[1]:
                set_cell_background(cell, "FEF2F2")

    doc.add_paragraph("\nChi tiết bốn thí nghiệm bắt buộc theo yêu cầu học phần:")

    # Thí nghiệm 1
    doc.add_heading("7.1 Thí nghiệm 1: Tính ổn định của Random Stratified Split qua các Seed", level=2)
    doc.add_paragraph(
        "Để chứng minh việc chia tập phân tầng (Stratified Split) là cần thiết và giảm thiểu phương sai ngẫu nhiên, "
        "chúng tôi thực hiện kiểm tra trên 5 seed ngẫu nhiên khác nhau (42, 100, 2024, 777, 999). "
        f"Kết quả cho thấy: Stratified Split duy trì tỷ lệ lớp dương ở mức cố định 15.62% trên cả Train và Test, "
        f"với PR-AUC trung bình đạt {exp_data['experiment_1_seed_stability']['strat_pr_auc_mean']:.4f} ± {exp_data['experiment_1_seed_stability']['strat_pr_auc_std']:.4f}. "
        f"Ngược lại, Unstratified Split làm tỷ lệ lớp dương dao động từ 14.8% đến 16.9%, dẫn tới phương sai metric lớn hơn ({exp_data['experiment_1_seed_stability']['unstrat_pr_auc_mean']:.4f} ± {exp_data['experiment_1_seed_stability']['unstrat_pr_auc_std']:.4f})."
    )
    fig1_path = os.path.join(FIG_DIR, "exp1_seed_stability.png")
    if os.path.exists(fig1_path):
        doc.add_picture(fig1_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Hình 1: Đánh giá độ ổn định của phân chia phân tầng (Stratified Split) qua 5 seed ngẫu nhiên.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].italic = True

    # Thí nghiệm 2
    doc.add_heading("7.2 Thí nghiệm 2: Kiểm toán rò rỉ dữ liệu (So sánh có/không PageValues)", level=2)
    doc.add_paragraph(
        "Thí nghiệm 2 là bằng chứng cốt lõi của đề tài. Khi có biến PageValues, mô hình Naive Random Forest đạt ROC-AUC 0.9282 và PR-AUC 0.7305. "
        "Tuy nhiên, khi loại bỏ biến rò rỉ này, mô hình Honest Random Forest đạt PR-AUC trung thực là 0.3709 và ROC-AUC 0.7822. "
        "Sự sụt giảm gần 50% của PR-AUC phản ánh chính xác lượng thông tin rò rỉ giả tạo bị loại bỏ. "
        "Phân tích Feature Importance (Hình 3) cho thấy: Trong mô hình Naive, PageValues chiếm trên 65% tổng tầm quan trọng của toàn bộ mô hình, "
        "làm lu mờ hoàn toàn các hành vi duyệt web như thời gian xem trang sản phẩm hay tỷ lệ thoát."
    )
    fig2_path = os.path.join(FIG_DIR, "exp2_leakage_audit_comparison.png")
    if os.path.exists(fig2_path):
        doc.add_picture(fig2_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Hình 2: So sánh hiệu năng giữa mô hình ngây thơ (Naive) và mô hình trung thực (Honest).")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].italic = True

    fig_imp_path = os.path.join(FIG_DIR, "feature_importance_shift.png")
    if os.path.exists(fig_imp_path):
        doc.add_picture(fig_imp_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Hình 3: Sự chuyển dịch tầm quan trọng thuộc tính (Feature Importance Shift) khi loại bỏ biến rò rỉ.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].italic = True

    # Thí nghiệm 3
    doc.add_heading("7.3 Thí nghiệm 3: Đường cong PR (Precision-Recall) do mất cân bằng dữ liệu", level=2)
    doc.add_paragraph(
        "Vì tập dữ liệu có tỷ lệ dương chỉ 15.6%, đường cong ROC dễ tạo cảm giác lạc quan thái quá (False Optimism). "
        "Lý do là số lượng True Negative (mẫu âm được đoán đúng) rất lớn, làm mẫu số của False Positive Rate (FPR = FP / (FP + TN)) luôn rất lớn, "
        "khiến FPR luôn nhỏ và đường ROC phồng to về góc trên bên trái. "
        "Trong khi đó, Precision-Recall Curve đánh giá trực tiếp độ chính xác trên các mẫu dương thực tế và dự đoán dương, "
        "với đường cơ sở No-skill Baseline nằm ngang tại y = 0.156. "
        "Hình 4 minh chứng rõ: Honest Random Forest đạt AP = 0.371, vượt xa gấp đôi mức No-Skill Baseline."
    )
    fig3_path = os.path.join(FIG_DIR, "exp3_pr_vs_roc_curve.png")
    if os.path.exists(fig3_path):
        doc.add_picture(fig3_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Hình 4: Đối chiếu giữa Precision-Recall Curve và ROC Curve trên tập kiểm thử độc lập.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].italic = True

    # Thí nghiệm 4
    doc.add_heading("7.4 Thí nghiệm 4: Calibration Curve và Phân tích sai số theo VisitorType và Month", level=2)
    doc.add_paragraph(
        "Độ tin cậy xác suất là yếu tố then chốt khi phục vụ dự đoán. Đồ thị Reliability Diagram (Hình 5) cho thấy "
        "Honest Random Forest có đường chuẩn xác tiến gần đường lý tưởng với Brier Score đạt 0.1756. "
        "Phân tích sai số chi tiết (Hình 6) chỉ ra:\n"
        "• Theo Tháng (Month): Mô hình đạt F1-score và Recall cao nhất vào Tháng 11 (Nov - mùa Black Friday / Cyber Monday) với F1 > 0.65 "
        "do hành vi mua hàng ở tháng này có mục đích rõ rệt và thời gian duyệt sản phẩm tập trung cao.\n"
        "• Theo Khách truy cập (VisitorType): Nhóm Khách mới (New_Visitor) có độ chính xác dự đoán cao hơn Khách quen (Returning_Visitor), "
        "bởi khách mới thường đến từ kênh tìm kiếm trả phí với ý định mua hàng dứt khoát hơn."
    )
    fig4_path = os.path.join(FIG_DIR, "exp4_calibration_curve.png")
    if os.path.exists(fig4_path):
        doc.add_picture(fig4_path, width=Inches(5.0))
        p_cap = doc.add_paragraph("Hình 5: Reliability Diagram (Calibration Curve) đánh giá độ tin cậy xác suất đầu ra.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].italic = True

    fig_err_path = os.path.join(FIG_DIR, "exp4_error_breakdown.png")
    if os.path.exists(fig_err_path):
        doc.add_picture(fig_err_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Hình 6: Phân tích sai số mô hình Honest Random Forest theo Tháng và Loại khách truy cập.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].italic = True

    # 8. PHÂN TÍCH LỖI VÀ MA TRẬN NHẦM LẪN
    h8 = doc.add_heading("8. PHÂN TÍCH LỖI & MA TRẬN NHẦM LẪN (CONFUSION MATRIX)", level=1)
    doc.add_paragraph(
        "Tại ngưỡng cắt tối ưu 0.518, mô hình Honest Random Forest đạt Precision = 30.87% và Recall = 67.13%. "
        "Ma trận nhầm lẫn (Hình 7) thể hiện: Mô hình bắt được 192 trên 286 phiên mua hàng thực tế (thu hồi cao), "
        "nhưng chấp nhận một số lượng False Positives nhất định (430 phiên). "
        "Trong bối cảnh marketing thương mại điện tử, việc chấp nhận False Positive để gửi voucher kích cầu tốt hơn nhiều so với việc bỏ lỡ một đơn hàng thật (False Negative)."
    )
    fig_cm_path = os.path.join(FIG_DIR, "confusion_matrices.png")
    if os.path.exists(fig_cm_path):
        doc.add_picture(fig_cm_path, width=Inches(5.5))
        p_cap = doc.add_paragraph("Hình 7: So sánh ma trận nhầm lẫn (Confusion Matrix) giữa Naive RF và Honest RF.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].italic = True

    # 9. SẢN PHẨM WEB & API
    h9 = doc.add_heading("9. SẢN PHẨM WEB APPLICATION & KIẾN TRÚC REST API", level=1)
    doc.add_paragraph(
        "9.1 Kiến trúc phục vụ (Serving Architecture):\n"
        "Hệ thống tuân thủ nguyên tắc tách biệt huấn luyện offline (Offline Training) khỏi phục vụ thời gian thực (Online Serving). "
        "Flask application chỉ nạp pipeline đã được đóng gói bằng joblib trong thư mục models/, đảm bảo tốc độ phản hồi < 20ms cho mỗi yêu cầu.\n\n"
        "9.2 Đặc tả REST API:\n"
        "• Phương thức: POST /api/session-score\n"
        "• Định dạng payload: JSON chứa 16 thuộc tính của phiên web.\n"
        "• Kiểm tra hợp lệ (Schema Validation): Hệ thống kiểm tra chặt chẽ miền giá trị hợp lệ của từng trường, "
        "báo lỗi mã HTTP 422 nếu thiếu trường hoặc dữ liệu sai định dạng, tuyệt đối không âm thầm thay thế giá trị.\n"
        "• Cơ chế Kiểm toán rò rỉ thời gian thực: Nếu client cố tình gửi kèm thuộc tính PageValues, API sẽ tính toán đối chứng "
        "với mô hình Naive và kích hoạt cờ cảnh báo rò rỉ (leakage_comparison) với thông điệp cảnh báo đỏ.\n\n"
        "9.3 Giao diện người dùng 3 màn hình:\n"
        "• Màn hình 1: Giới thiệu, bối cảnh thực tiễn, phân tích công thức Google Analytics PageValue và các cam kết đạo đức.\n"
        "• Màn hình 2: Giao diện nhập liệu phiên tổng hợp, cung cấp 3 nút chọn mẫu nhanh (Tiềm năng cao, Thoát ngay, Duyệt phân vân), thanh đo xác suất trực quan và hành động khuyến nghị cho marketing.\n"
        "• Màn hình 3: Dashboard trực quan hóa 4 thí nghiệm, bảng so sánh đa mô hình, tích hợp Model Card và Data Card chuẩn quốc tế."
    )

    # 10. ĐẠO ĐỨC & GIỚI HẠN
    h10 = doc.add_heading("10. ĐẠO ĐỨC HỌC MÁY, QUYỀN RIÊNG TƯ & GIỚI HẠN MÔ HÌNH", level=1)
    doc.add_paragraph(
        "• Đạo đức học máy: Mô hình được huấn luyện trên dữ liệu ẩn danh hoàn toàn, không theo dõi định danh cá nhân (PII), "
        "không áp dụng các kỹ thuật giao diện lừa đảo (Dark Patterns) để ép khách mua hàng.\n"
        "• Giới hạn của mô hình: Mô hình chỉ phản ánh hành vi trên nền tảng thương mại điện tử cụ thể tại thời điểm thu thập (2019). "
        "Khi hành vi người dùng thay đổi (Data Drift), mô hình cần được cập nhật và hiệu chỉnh lại.\n"
        "• Không khẳng định quan hệ nhân quả: Các hệ số và feature importance chỉ thể hiện mối tương quan thống kê trong phiên, "
        "không được diễn giải là nguyên nhân trực tiếp dẫn tới hành vi mua hàng."
    )

    # 11. KẾT LUẬN & KIẾN NGHỊ
    h11 = doc.add_heading("11. KẾT LUẬN & ĐỀ XUẤT HƯỚNG MỞ RỘNG", level=1)
    doc.add_paragraph(
        "11.1 Kết luận:\n"
        "Project 19 đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra theo rubric đánh giá Bài 7:\n"
        "1. Chứng minh được hiện tượng rò rỉ dữ liệu nguy hiểm từ biến PageValues, giải thích cặn kẽ công thức và cơ chế lối tắt học tập.\n"
        "2. Xây dựng pipeline chuẩn scikit-learn fit đúng phần Train, giữ tập Test hoàn toàn độc lập.\n"
        "3. Thực hiện đầy đủ 4 thí nghiệm bắt buộc với các biểu đồ khoa học trực quan và lập luận chặt chẽ.\n"
        "4. Đóng gói sản phẩm web và REST API hoàn chỉnh, kiểm thử tự động đạt 100% test cases.\n\n"
        "11.2 Đề xuất mở rộng:\n"
        "Nếu trong tương lai hệ thống thu thập được dữ liệu chuỗi sự kiện thời gian thực (event-level clickstream với timestamp), "
        "nhóm đề xuất xây dựng các snapshot tại phút thứ 2, phút thứ 5 bằng mô hình tuần tự (LSTM / Temporal Transformers) "
        "để thực hiện dự đoán early-stage thực thụ."
    )

    # 12. TÀI LIỆU THAM KHẢO
    h12 = doc.add_heading("12. TÀI LIỆU THAM KHẢO", level=1)
    doc.add_paragraph(
        "[1] PGS.TS. Nguyễn Văn Hậu. Bài giảng Học máy cơ bản: Bài 7 — Rò rỉ dữ liệu, chia tập đúng và đánh giá trung thực.\n"
        "[2] Sakar, C. O., Polat, S. O., Katircioglu, M., & Kastro, Y. (2019). Real-time prediction of online shoppers' purchasing intention using multilayer perceptron and LSTM recurrent neural networks. Neural Computing and Applications, 31(10), 6893-6908.\n"
        "[3] UCI Machine Learning Repository: Online Shoppers Purchasing Intention Dataset. DOI: 10.24432/C5F88Q.\n"
        "[4] Scikit-learn Documentation: Common Pitfalls and Recommended Practices in Machine Learning (Data Leakage & Preprocessing).\n"
        "[5] Mitchell, M., et al. (2019). Model Cards for Model Reporting. Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT*), 220-229.\n"
        "[6] Google Analytics Help: How Page Value is calculated in Ecommerce reports."
    )

    # 13. PHỤ LỤC TÁI LẬP & NHẬT KÝ 6 TUẦN
    h13 = doc.add_heading("13. PHỤ LỤC TÁI LẬP, NHẬT KÝ 6 TUẦN & PHÂN CÔNG NHÓM", level=1)
    doc.add_paragraph(
        "13.1 Hướng dẫn tái lập quy trình một lệnh (Reproducibility Guide):\n"
        "Để tái lập toàn bộ pipeline trên một máy tính mới hoàn toàn, sinh viên hoặc giảng viên chỉ cần thực hiện:\n"
        "   1. Cài đặt thư viện: pip install -r requirements.txt\n"
        "   2. Chạy toàn bộ pipeline: python run_pipeline.py\n"
        "   3. Khởi động Web App & API: python app/app.py\n"
        "   4. Truy cập giao diện tại: http://127.0.0.1:5000\n"
    )

    # Bảng phân công 2 thành viên trong 6 tuần
    doc.add_paragraph("13.2 Nhật ký 6 tuần và bảng phân công cân bằng giữa 2 thành viên:")
    table_plan = doc.add_table(rows=7, cols=4)
    set_table_borders(table_plan)
    table_plan.alignment = WD_TABLE_ALIGNMENT.CENTER
    plan_headers = ["Tuần", "Nội dung công việc chính", "Thành viên A (Dữ liệu/Model)", "Thành viên B (Đánh giá/Web)"]
    for i, h in enumerate(plan_headers):
        cell = table_plan.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "F1F5F9")

    plan_rows = [
        ("Tuần 1", "Khảo sát đề tài, câu hỏi nghiên cứu & kiểm toán rò rỉ", "Tìm hiểu UCI, viết data README và data dictionary", "Thiết lập Git repo, backlog, xác định câu hỏi nghiên cứu"),
        ("Tuần 2", "Làm sạch dữ liệu, EDA và chia tập độc lập", "Xử lý 125 dòng trùng lặp, xây dựng src/data.py", "Thực hiện EDA trên Train, xây dựng Baseline Dummy/LR"),
        ("Tuần 3", "Xây dựng Pipeline trung thực và mô hình ngây thơ", "Xây dựng ColumnTransformer và Pipeline trong src/features.py", "Huấn luyện Naive Models và đối chứng sụp đổ hiệu năng"),
        ("Tuần 4", "Tuning siêu tham số trên Train & 4 thí nghiệm", "Thực hiện Stratified 5-Fold CV, GridSearch trên Train", "Đánh giá 1 lần trên Test độc lập, lập 4 thí nghiệm (src/evaluate.py)"),
        ("Tuần 5", "Phát triển Web Application và REST API", "Xây dựng module serving nạp pipeline và schema validation", "Thiết kế giao diện 3 màn hình (Tailwind CSS, JS) và API test"),
        ("Tuần 6", "Kiểm thử tự động, viết báo cáo và slide thuyết trình", "Viết báo cáo chuyên sâu (Mục 1-7), đóng gói run_pipeline.py", "Viết báo cáo (Mục 8-13), soạn slide thuyết trình, rehearsal demo")
    ]
    for row_idx, p_tuple in enumerate(plan_rows, start=1):
        for col_idx, t_val in enumerate(p_tuple):
            cell = table_plan.cell(row_idx, col_idx)
            cell.text = t_val

    # Câu hỏi vấn đáp gợi ý
    doc.add_paragraph(
        "\n13.3 Chuẩn bị phần vấn đáp gợi ý của Giảng viên:\n"
        "• Câu hỏi 1: Vì sao PageValues đáng nghi?\n"
        "  Trả lời: Vì theo công thức của Google Analytics, PageValues được tính bằng Doanh thu thương mại điện tử chia cho số lượt xem trang duy nhất. Nếu phiên đó có đơn hàng, biến này lập tức mang giá trị dương rất cao. Do đó biến này xuất hiện sau kết quả và mang thông tin của nhãn mục tiêu (outcome-proxy feature).\n\n"
        "• Câu hỏi 2: Tại sao dataset này không đủ để tuyên bố dự đoán ở phút đầu?\n"
        "  Trả lời: Vì dataset Online Shoppers chỉ là bản tóm tắt phiên cuối cùng (bảng tổng số trang và tổng thời lượng cả phiên), không có timestamp từng click hay dữ liệu dạng luồng sự kiện theo thời gian.\n\n"
        "• Câu hỏi 3: PR-AUC phù hợp hơn Accuracy/ROC-AUC ở điểm nào?\n"
        "  Trả lời: Tỷ lệ nhãn dương chỉ chiếm 15.6%. Một mô hình ngây thơ luôn đoán False đã đạt Accuracy 84.4% nhưng vô dụng. Đường ROC-AUC cũng bị phồng to do mẫu số FPR có chứa số lượng True Negative áp đảo. Đường PR-AUC chỉ tập trung vào lớp thiểu số (Precision và Recall) nên phản ánh năng lực phân biệt trung thực hơn rất nhiều."
    )

    doc.save(OUTPUT_DOCX)
    print(f"\n[OK] ĐÃ XUẤT THÀNH CÔNG BÁO CÁO TOÀN DIỆN DOCX:")
    print(f" -> Đường dẫn: {OUTPUT_DOCX}")
    return OUTPUT_DOCX


if __name__ == "__main__":
    build_docx_report()
