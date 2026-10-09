# Từ Điển Dữ Liệu (Data Dictionary)

Bộ dữ liệu: **Online Shoppers Purchasing Intention Dataset**  
Quy mô: 12.330 quan sát, 18 thuộc tính.

| STT | Tên thuộc tính | Kiểu dữ liệu | Đơn vị đo / Miền giá trị | Vai trò | Thời điểm khả dụng | Đánh giá rủi ro rò rỉ (Leakage Audit) & Quyết định |
|---|---|---|---|---|---|---|
| 1 | `Administrative` | Số nguyên (`int64`) | Số lượng trang $[0, 27]$ | Feature | Cuối phiên | **An toàn**: Số trang quản trị người dùng ghé thăm trong phiên. Giữ lại. |
| 2 | `Administrative_Duration` | Số thực (`float64`) | Giây (seconds) $[0, 3398.75]$ | Feature | Cuối phiên | **An toàn**: Tổng thời gian lưu lại tại trang quản trị. Giữ lại. |
| 3 | `Informational` | Số nguyên (`int64`) | Số lượng trang $[0, 24]$ | Feature | Cuối phiên | **An toàn**: Số trang thông tin (chính sách, giới thiệu, blog). Giữ lại. |
| 4 | `Informational_Duration` | Số thực (`float64`) | Giây (seconds) $[0, 2549.3]$ | Feature | Cuối phiên | **An toàn**: Tổng thời gian lưu lại tại trang thông tin. Giữ lại. |
| 5 | `ProductRelated` | Số nguyên (`int64`) | Số lượng trang $[0, 705]$ | Feature | Cuối phiên | **An toàn**: Số trang sản phẩm đã xem. Giữ lại. |
| 6 | `ProductRelated_Duration` | Số thực (`float64`) | Giây (seconds) $[0, 63973.52]$ | Feature | Cuối phiên | **An toàn**: Tổng thời gian xem sản phẩm. Giữ lại. |
| 7 | `BounceRates` | Số thực (`float64`) | Tỷ lệ $[0.0, 0.2]$ | Feature | Cuối phiên | **An toàn**: Tỷ lệ phần trăm khách truy cập vào trang và thoát ra ngay mà không kích hoạt yêu cầu nào khác. Giữ lại. |
| 8 | `ExitRates` | Số thực (`float64`) | Tỷ lệ $[0.0, 0.2]$ | Feature | Cuối phiên | **An toàn**: Tỷ lệ phần trăm số lượt xem trang là trang cuối cùng của phiên. Giữ lại. |
| 9 | `PageValues` | Số thực (`float64`) | Điểm giá trị USD $[0.0, 361.76]$ | Biến rò rỉ (Leakage Feature) | Sau khi chốt giao dịch | **RÒ RỈ DỮ LIỆU NGHIÊM TRỌNG (TARGET PROXY LEAKAGE)**: Theo công thức Google Analytics, `PageValues = (Giao dịch + Mục tiêu) / Lượt xem`. Biến này được gán giá trị sau khi có đơn hàng. **BẮT BUỘC LOẠI KHỎI MÔ HÌNH CHÍNH (Honest Model)**. Chỉ dùng để huấn luyện mô hình đối chứng ngây thơ (Naive Model). |
| 10 | `SpecialDay` | Số thực (`float64`) | Điểm số $[0.0, 1.0]$ | Feature | Thời điểm bắt đầu phiên | **An toàn**: Mức độ gần với các ngày lễ đặc biệt (ví dụ: Mother's Day, Valentine) tính theo hệ số lân cận. Giữ lại. |
| 11 | `Month` | Phân loại (`object/str`) | 10 tháng: Feb, Mar, May, June, Jul, Aug, Sep, Oct, Nov, Dec | Feature | Thời điểm bắt đầu phiên | **An toàn**: Tháng phát sinh phiên truy cập. Giữ lại. |
| 12 | `OperatingSystems` | Phân loại/Mã hóa (`int64`) | Mã danh mục $[1, 8]$ | Feature | Thời điểm bắt đầu phiên | **An toàn**: Hệ điều hành của thiết bị truy cập. Giữ lại. |
| 13 | `Browser` | Phân loại/Mã hóa (`int64`) | Mã danh mục $[1, 13]$ | Feature | Thời điểm bắt đầu phiên | **An toàn**: Trình duyệt web sử dụng. Giữ lại. |
| 14 | `Region` | Phân loại/Mã hóa (`int64`) | Mã danh mục $[1, 9]$ | Feature | Thời điểm bắt đầu phiên | **An toàn**: Khu vực địa lý của người dùng. Giữ lại. |
| 15 | `TrafficType` | Phân loại/Mã hóa (`int64`) | Mã danh mục $[1, 20]$ | Feature | Thời điểm bắt đầu phiên | **An toàn**: Nguồn lưu lượng (tìm kiếm, quảng cáo trực tiếp, banner, giới thiệu,...). Giữ lại. |
| 16 | `VisitorType` | Phân loại (`object/str`) | `Returning_Visitor`, `New_Visitor`, `Other` | Feature | Thời điểm bắt đầu phiên | **An toàn**: Loại khách truy cập (khách quen, khách mới, loại khác). Giữ lại. |
| 17 | `Weekend` | Nhị phân (`bool`) | `TRUE`, `FALSE` | Feature | Thời điểm bắt đầu phiên | **An toàn**: Phiên diễn ra vào cuối tuần (Thứ 7, CN) hay ngày trong tuần. Giữ lại. |
| 18 | `Revenue` | Nhị phân (`bool`) | `TRUE` (1.908), `FALSE` (10.422) | Target (Nhãn mục tiêu) | Sau khi kết thúc phiên | **Nhãn mục tiêu (Y)**: Phiên có dẫn tới giao dịch mua hàng hoàn tất hay không. Tỷ lệ dương 15.47%. |
