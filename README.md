# PROJECT 19: DỰ ĐOÁN PHIÊN MUA HÀNG VỚI KIỂM TOÁN RÒ RỈ (LEAKAGE AUDIT)

**Học phần:** HỌC MÁY CƠ BẢN (Mã lớp: 12523W.1)  
**Chủ đề:** Bài 7 — Rò rỉ dữ liệu, chia tập đúng và đánh giá trung thực  
**Giảng viên hướng dẫn:** PGS.TS. NGUYỄN VĂN HẬU  
**Hình thức:** Nhóm 02 sinh viên  

---

## 1. TỔNG QUAN ĐỀ TÀI & CẢNH BÁO QUAN TRỌNG

### 1.1 Bối cảnh thực tiễn & Câu hỏi nghiên cứu
- **Bối cảnh:** Nhóm marketing muốn phân loại các phiên duyệt web kết thúc bằng giao dịch (`Revenue = True`) để kích hoạt ưu đãi hoặc hỗ trợ khách hàng. Tuy nhiên, các hệ thống analytics thường tổng hợp dữ liệu sau khi phiên đóng, tạo ra rủi ro rò rỉ dữ liệu (data leakage) nghiêm trọng.
- **Câu hỏi nghiên cứu:** *Kết quả thay đổi thế nào khi loại các biến gần mục tiêu và mô tả đúng thời điểm dự đoán?*

### 1.2 Tuyên bố phạm vi bắt buộc (Non-negotiable Scope Statement)
1. **Đơn vị quan sát:** **Một phiên web đã được tổng hợp sau khi phiên kết thúc (End-of-Session Aggregate Summary)**.
2. **CẢNH BÁO VỀ THỜI ĐIỂM DỰ ĐOÁN:** Tuyệt đối **không gọi là dự đoán 'trong vài phút đầu'** vì dữ liệu hoàn toàn không có event-level snapshot hay timestamp chuỗi sự kiện. Các thuộc tính thời gian (ví dụ `ProductRelated_Duration`) là tổng tích lũy của cả phiên.
3. **KIỂM TOÁN RÒ RỈ BIẾN `PageValues` (Target Proxy Leakage):**
   - Theo công thức Google Analytics: 
     $$\text{Page Value} = \frac{\text{Ecommerce Revenue} + \text{Total Goal Value}}{\text{Unique Pageviews}}$$
   - Biến `PageValues` được tính toán ngược sau khi khách thanh toán thành công đơn hàng. Việc đưa biến này vào mô hình tạo ra **lối tắt học tập (shortcut learning)**, điểm số cao giả tạo nhưng vô dụng trong thực tế.
   - **Quy tắc bắt buộc:** Loại bỏ hoàn toàn `PageValues` khỏi mô hình chính (**Honest Model**). Chỉ dùng `PageValues` để huấn luyện mô hình ngây thơ (**Naive Model**) nhằm đối chứng và kiểm toán.

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```
Project Hoc May Co Ban/
│
├── data/
│   ├── README.md                      # Nguồn, checksum, giấy phép CC BY 4.0, trích dẫn
│   ├── data_dictionary.md             # Từ điển dữ liệu, vai trò, thời điểm khả dụng & rò rỉ
│   ├── download_data.py               # Script tải & kiểm tra toàn vẹn bộ dữ liệu
│   └── online_shoppers_intention.csv  # Bộ dữ liệu thô từ UCI (12.330 phiên)
│
├── src/
│   ├── __init__.py
│   ├── data.py                        # Khử 125 trùng lặp, chia Stratified Train/Val/Test
│   ├── features.py                    # Scikit-learn ColumnTransformer & Pipelines
│   ├── train.py                       # Huấn luyện Baseline, Naive, Honest với 5-Fold CV
│   └── evaluate.py                    # Thực hiện 4 thí nghiệm bắt buộc & xuất đồ thị
│
├── app/
│   ├── app.py                         # Flask Web Application & REST API serving
│   ├── templates/
│   │   └── index.html                 # Giao diện 3 màn hình chuẩn UI/UX
│   └── static/
│       ├── css/style.css              # Custom styling & hiệu ứng
│       ├── js/main.js                 # Xử lý client, presets demo & gọi API
│       └── figures/                   # Ảnh đồ thị phục vụ hiển thị trên Dashboard
│
├── models/
│   ├── pipeline_honest_best.joblib    # Mô hình trung thực phục vụ Serving
│   ├── pipeline_honest_rf.joblib      # Honest Random Forest Pipeline
│   ├── pipeline_honest_lr.joblib      # Honest Logistic Regression Pipeline
│   ├── pipeline_honest_gb.joblib      # Honest Gradient Boosting Pipeline
│   ├── pipeline_naive_rf.joblib       # Naive Random Forest Pipeline (Rò rỉ)
│   ├── pipeline_naive_lr.joblib       # Naive Logistic Regression Pipeline (Rò rỉ)
│   ├── pipeline_baseline_lr.joblib    # Baseline 4 biến hành vi
│   ├── dummy_model.joblib             # Baseline Dummy Majority Class
│   ├── test_dataset_frozen.csv        # Tập Test độc lập đã đóng băng
│   ├── experiment_results.json        # Dữ liệu chi tiết 4 thí nghiệm
│   ├── training_summary.json          # Tóm tắt quá trình huấn luyện
│   └── data_quality_report.json       # Báo cáo chất lượng dữ liệu
│
├── reports/
│   ├── figures/                       # 7 đồ thị thực nghiệm độ phân giải cao 300 DPI
│   ├── Bao_cao_Project_19_Chuyen_doi_mua_hang.docx  # Báo cáo chuẩn 13 mục
│   └── Slide_Thuyet_Trinh_Project_19.pptx           # 12 Slide thuyết trình bảo vệ
│
├── requirements.txt                   # Danh sách thư viện phụ thuộc
├── run_pipeline.py                    # Script chạy toàn bộ quy trình từ A đến Z
├── test_api.py                        # Kiểm thử tự động API và serving
└── README.md                          # Tài liệu hướng dẫn sử dụng toàn diện
```

---

## 3. HƯỚNG DẪN CÀI ĐẶT & CHẠY DỰ ÁN TỪ MÁY MỚI (REPRODUCIBILITY)

### Bước 1: Chuẩn bị môi trường
Yêu cầu Python 3.10 hoặc 3.11. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

### Bước 2: Tái lập toàn bộ quy trình bằng một lệnh duy nhất
Chạy lệnh sau để tự động thực hiện: kiểm tra dữ liệu, lọc trùng lặp, chia tập độc lập, huấn luyện mô hình, thực hiện 4 thí nghiệm, xuất đồ thị và chạy kiểm thử tự động:
```bash
python run_pipeline.py
```

### Bước 3: Khởi động Ứng dụng Web & REST API
```bash
python app/app.py
```
- Mở trình duyệt tại: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- REST API Endpoint: `POST http://127.0.0.1:5000/api/session-score`

---

## 4. BỐN THÍ NGHIỆM BẮT BUỘC & KẾT QUẢ THỰC NGHIỆM

Toàn bộ các mô hình được đánh giá trên cùng một tập **Test độc lập đóng băng** gồm 1.831 phiên (286 phiên mua hàng thực tế):

| Mô hình | Rò rỉ PageValues? | PR-AUC (Average Precision) | ROC-AUC | Precision | Recall | F1-Score | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Dummy (Majority)** | Không | 0.1562 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.1318 |
| **Baseline LR (4 biến)** | Không | 0.2882 | 0.7088 | 0.2304 | 0.7587 | 0.3534 | 0.2241 |
| **Honest Logistic Reg** | Không | 0.3278 | 0.7460 | 0.2643 | 0.7448 | 0.3901 | 0.2117 |
| **Honest Random Forest** | **Không** | **0.3709** | **0.7822** | **0.3087** | **0.6713** | **0.4229** | **0.1756** |
| **Honest Gradient Boost** | Không | 0.3730 | 0.7853 | 0.3311 | 0.6818 | 0.4457 | 0.1659 |
| **Naive Logistic Reg** | **CÓ (Rò rỉ)** | 0.6728 | 0.9085 | 0.5011 | 0.8042 | 0.6174 | 0.1214 |
| **Naive Random Forest** | **CÓ (Rò rỉ)** | **0.7305** | **0.9282** | 0.5469 | 0.8566 | 0.6676 | 0.1157 |

### Ý nghĩa 4 thí nghiệm:
1. **Thí nghiệm 1 (Ổn định Stratified Split):** Phân chia Stratified bảo toàn tỷ lệ dương 15.62% cố định qua 5 seed (42, 100, 2024, 777, 999), ngăn chặn phương sai lớn so với Unstratified Split.
2. **Thí nghiệm 2 (Kiểm toán rò rỉ PageValues):** Điểm số PR-AUC sụt giảm gần 50% (từ 0.7305 xuống 0.3709) khi loại bỏ PageValues. Đồ thị Feature Importance chứng minh PageValues chiếm trên 65% trọng số trong Naive RF, che mờ hoàn toàn hành vi thực của người dùng.
3. **Thí nghiệm 3 (PR Curve trên dữ liệu mất cân bằng):** Tỷ lệ dương chỉ 15.6% khiến ROC Curve bị thổi phồng bởi số lượng True Negative quá lớn (ROC-AUC ~0.78-0.93). PR Curve với No-skill baseline = 0.156 phản ánh năng lực phân biệt trung thực hơn.
4. **Thí nghiệm 4 (Calibration & Sai số theo nhóm):** Brier Score đạt 0.1756. Sai số mô hình thấp nhất và F1-Score cao nhất vào tháng 11 (Nov - mùa mua sắm Black Friday) và ở nhóm khách hàng mới (New Visitor).

---

## 5. SẢN PHẨM WEB & REST API

### 5.1 Giao diện 3 màn hình (Web UI):
- **Màn hình 1 (Bối cảnh & Kiểm toán):** Giới thiệu đề tài, công thức Google Analytics và các nguyên tắc đạo đức.
- **Màn hình 2 (Thao tác dự đoán & Chấm điểm phiên):** Form nhập liệu chia 3 nhóm logic, 3 nút preset dữ liệu thử nghiệm nhanh, thanh đo xác suất trực quan, hành động gợi ý cho marketing và phát hiện cảnh báo đỏ nếu người dùng thử đưa `PageValues` vào.
- **Màn hình 3 (Dashboard 4 Thí nghiệm & Model Card):** Bảng so sánh 7 mô hình, hiển thị trực quan các đồ thị thí nghiệm, Model Card và Data Card chuẩn Mitchell et al. (2019).

### 5.2 Đặc tả REST API:
- **Endpoint:** `POST /api/session-score`
- **Ví dụ Request Payload:**
```json
{
  "Administrative": 3,
  "Administrative_Duration": 80.0,
  "Informational": 1,
  "Informational_Duration": 25.0,
  "ProductRelated": 30,
  "ProductRelated_Duration": 1500.0,
  "BounceRates": 0.005,
  "ExitRates": 0.02,
  "SpecialDay": 0.0,
  "Month": "Nov",
  "OperatingSystems": 2,
  "Browser": 2,
  "Region": 1,
  "TrafficType": 2,
  "VisitorType": "Returning_Visitor",
  "Weekend": false
}
```
- **Ví dụ Response Payload:**
```json
{
  "status": "success",
  "observation_unit": "Bản tóm tắt phiên duyệt web cuối phiên (End-of-Session Aggregate)",
  "prediction": {
    "will_purchase": true,
    "purchase_probability": 0.7414,
    "purchase_probability_percentage": "74.14%",
    "decision_threshold": 0.518,
    "intent_level": "Rất cao (Very High Intent)",
    "action_recommendation": "Ưu tiên hiển thị ưu đãi chốt đơn ngay hoặc hỗ trợ thanh toán nhanh."
  },
  "model_audit_info": {
    "model_type": "Honest Random Forest (Trung thực)",
    "page_values_used": false,
    "audit_disclaimer": "Mô hình được huấn luyện hoàn toàn không chứa thuộc tính PageValues để loại bỏ rò rỉ dữ liệu."
  }
}
```

---

## 6. HỒ SƠ BÀN GIAO & PHÂN CÔNG NHÓM

- **Báo cáo kết thúc học phần:** [`reports/Bao_cao_Project_19_Chuyen_doi_mua_hang.docx`](file:///c:/Users/ACXSAB/Desktop/Project%20Hoc%20May%20Co%20Ban/reports/Bao_cao_Project_19_Chuyen_doi_mua_hang.docx) (Đầy đủ 13 mục theo rubric).
- **Slide thuyết trình:** [`reports/Slide_Thuyet_Trinh_Project_19.pptx`](file:///c:/Users/ACXSAB/Desktop/Project%20Hoc%20May%20Co%20Ban/reports/Slide_Thuyet_Trinh_Project_19.pptx) (12 slide chuẩn hóa cho buổi bảo vệ 12-15 phút).
- **Phân công 2 thành viên:**
  - **Thành viên 1:** Phụ trách kiểm toán dữ liệu, khử trùng lặp, chia tập độc lập, xây dựng pipeline scikit-learn, huấn luyện và tối ưu siêu tham số.
  - **Thành viên 2:** Phụ trách thiết kế 4 thí nghiệm, đánh giá Test đóng băng, phát triển Web Flask & REST API, viết báo cáo và slide thuyết trình.
