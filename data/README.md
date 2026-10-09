# Hồ Sơ Dữ Liệu: Online Shoppers Purchasing Intention Dataset

## 1. Thông Tin Nguồn & Giấy Phép
- **Tên bộ dữ liệu**: Online Shoppers Purchasing Intention Dataset
- **Nguồn chính thức**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset)
- **DOI**: [10.24432/C5F88Q](https://doi.org/10.24432/C5F88Q)
- **Giấy phép (License)**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Tác giả / Nhà nghiên cứu**: C. Okan Sakar, S. Olcay Polat, Mete Katircioglu, Yomi Kastro (2019).
- **Ngày thu thập / công bố**: 2019 (Dữ liệu thu thập từ các phiên duyệt web trên nền tảng thương mại điện tử trong thời gian 1 năm).
- **Ngày tải / xác minh trong dự án**: Tháng 09/2026 (hoặc tại thời điểm thiết lập dự án).

## 2. Thông Số Tệp & Tính Toàn Vẹn (Integrity Check)
- **Tên tệp**: `online_shoppers_intention.csv`
- **Dung lượng**: 1.072.063 bytes (~1.02 MB)
- **Định dạng**: CSV (Comma Separated Values), mã hóa UTF-8
- **Số dòng dữ liệu**: 12.330 dòng quan sát + 1 dòng tiêu đề
- **Số cột thuộc tính**: 18 cột (10 số thực/nguyên, 7 phân loại/boolean, 1 nhãn mục tiêu)
- **Mã băm MD5**: `cc6ec1db03b4f10f8de52c56ff48b085`
- **Mã băm SHA-256**: `b3055ee355f59134d851d32641183cb4a8b45def7124d2f50442a042f358e0d9`

## 3. Trích Dẫn Học Thuật (Citation)
```bibtex
@article{sakar2019real,
  title={Real-time prediction of online shoppers' purchasing intention using multilayer perceptron and LSTM recurrent neural networks},
  author={Sakar, C Okan and Polat, S Olcay and Katircioglu, Mete and Kastro, Yomi},
  journal={Neural Computing and Applications},
  volume={31},
  number={10},
  pages={6893--6908},
  year={2019},
  publisher={Springer}
}
```

## 4. Tuyên Bố Phạm Vi & Cảnh Báo Rò Rỉ Dữ Liệu (Crucial Leakage Audit Statement)
1. **Đơn vị quan sát**: Một phiên duyệt web đã được tổng hợp sau khi phiên kết thúc (`session-level aggregated summary`).
2. **Không gọi là dự đoán thời gian thực trong vài phút đầu**: Dữ liệu không chứa dấu thời gian sự kiện (`event-level snapshots` hay timestamp từng click chuột). Toàn bộ số lượng trang và thời lượng (`Administrative_Duration`, `ProductRelated_Duration`, v.v.) là tổng số tích lũy sau cả phiên. Do đó, bài toán là **phân loại phiên mua hàng sau khi tổng hợp phiên**.
3. **Cảnh báo về `PageValues` (Target Proxy Leakage)**:
   - Theo định nghĩa của Google Analytics: 
     $$\text{Page Value} = \frac{\text{Ecommerce Revenue} + \text{Total Goal Value}}{\text{Unique Pageviews of that Page}}$$
   - Biến `PageValues` tính toán dựa trên việc phiên đó có phát sinh doanh thu (`Revenue`) hay không. Do đó, `PageValues` mang thông tin của tương lai/kết quả (outcome-proxy feature).
   - Nếu đưa `PageValues` vào huấn luyện, mô hình rơi vào bẫy rò rỉ dữ liệu (shortcut learning), đạt độ chính xác ảo nhưng không có giá trị triển khai thực tế.
   - **Quy tắc bắt buộc**: Loại bỏ hoàn toàn `PageValues` khỏi mô hình chính (Honest Model).
