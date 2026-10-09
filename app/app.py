"""Ứng dụng Web Flask & REST API cho Project 19: Dự đoán phiên mua hàng với kiểm toán rò rỉ.

Đảm bảo:
1. Tách biệt hoàn toàn offline training khỏi serving. Chỉ tải các pipeline đã đóng gói bằng joblib.
2. Endpoint API: POST /api/session-score.
3. Kiểm tra tính hợp lệ dữ liệu đầu vào (Validation & Out-of-bounds check).
4. Phân tích rò rỉ dữ liệu (Leakage Audit) khi phát hiện biến PageValues.
5. Cung cấp dữ liệu báo cáo và model card qua API /api/metrics.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import joblib
import pandas as pd
from flask import Flask, request, jsonify, render_template

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)

MODELS_DIR = os.path.join(BASE_DIR, "models")

print("Đang nạp các pipeline mô hình từ thư mục models/...")
try:
    HONEST_PIPELINE = joblib.load(os.path.join(MODELS_DIR, "pipeline_honest_best.joblib"))
    NAIVE_PIPELINE = joblib.load(os.path.join(MODELS_DIR, "pipeline_naive_rf.joblib"))
    
    with open(os.path.join(MODELS_DIR, "training_summary.json"), encoding="utf-8") as f:
        TRAIN_SUMMARY = json.load(f)
    with open(os.path.join(MODELS_DIR, "experiment_results.json"), encoding="utf-8") as f:
        EXP_RESULTS = json.load(f)
    with open(os.path.join(MODELS_DIR, "data_quality_report.json"), encoding="utf-8") as f:
        DATA_QUALITY = json.load(f)
    print("Nạp mô hình và cấu hình thành công!")
except Exception as e:
    print(f"Cảnh báo khi nạp mô hình: {e}")
    HONEST_PIPELINE = None
    NAIVE_PIPELINE = None
    TRAIN_SUMMARY = {}
    EXP_RESULTS = {}
    DATA_QUALITY = {}


VALID_BOUNDS = {
    'Administrative': (0, 30),
    'Administrative_Duration': (0.0, 5000.0),
    'Informational': (0, 30),
    'Informational_Duration': (0.0, 3500.0),
    'ProductRelated': (0, 1000),
    'ProductRelated_Duration': (0.0, 100000.0),
    'BounceRates': (0.0, 0.2),
    'ExitRates': (0.0, 0.2),
    'SpecialDay': (0.0, 1.0),
    'Month': ['Feb', 'Mar', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'OperatingSystems': list(range(1, 9)),
    'Browser': list(range(1, 14)),
    'Region': list(range(1, 10)),
    'TrafficType': list(range(1, 21)),
    'VisitorType': ['Returning_Visitor', 'New_Visitor', 'Other'],
    'Weekend': [True, False]
}


def validate_session_payload(data):
    """Kiểm tra schema và miền giá trị của payload đầu vào.
    
    Trả về (errors_list, warnings_list, cleaned_dict)
    """
    errors = []
    warnings = []
    cleaned = {}
    
    numeric_fields = [
        ('Administrative', int),
        ('Administrative_Duration', float),
        ('Informational', int),
        ('Informational_Duration', float),
        ('ProductRelated', int),
        ('ProductRelated_Duration', float),
        ('BounceRates', float),
        ('ExitRates', float),
        ('SpecialDay', float),
        ('OperatingSystems', int),
        ('Browser', int),
        ('Region', int),
        ('TrafficType', int),
    ]
    
    for field, f_type in numeric_fields:
        if field not in data:
            errors.append(f"Thiếu trường bắt buộc: '{field}'")
            continue
        try:
            val = f_type(data[field])
            cleaned[field] = val
            
            bounds = VALID_BOUNDS.get(field)
            if isinstance(bounds, tuple):
                min_v, max_v = bounds
                if val < min_v or val > max_v:
                    warnings.append(
                        f"Trường '{field}' có giá trị {val} nằm ngoài khoảng thông thường [{min_v}, {max_v}]."
                    )
            elif isinstance(bounds, list):
                if val not in bounds:
                    warnings.append(
                        f"Trường mã hóa '{field}' có giá trị {val} không nằm trong danh mục phổ biến {bounds}."
                    )
        except (ValueError, TypeError):
            errors.append(f"Trường '{field}' phải là kiểu số ({f_type.__name__}), nhận được: {data[field]}")
            
    if 'Month' not in data:
        errors.append("Thiếu trường bắt buộc: 'Month'")
    else:
        m_val = str(data['Month']).capitalize()
        if m_val.lower() == 'june':
            m_val = 'June'
        if m_val not in VALID_BOUNDS['Month']:
            errors.append(f"Trường 'Month' không hợp lệ: '{data['Month']}'. Các tháng được hỗ trợ: {VALID_BOUNDS['Month']}")
        else:
            cleaned['Month'] = m_val
            
    if 'VisitorType' not in data:
        errors.append("Thiếu trường bắt buộc: 'VisitorType'")
    else:
        vt = str(data['VisitorType']).strip()
        if vt not in VALID_BOUNDS['VisitorType']:
            errors.append(f"Trường 'VisitorType' không hợp lệ: '{vt}'. Hỗ trợ: {VALID_BOUNDS['VisitorType']}")
        else:
            cleaned['VisitorType'] = vt
            
    if 'Weekend' not in data:
        errors.append("Thiếu trường bắt buộc: 'Weekend'")
    else:
        w_raw = data['Weekend']
        if isinstance(w_raw, bool):
            cleaned['Weekend'] = w_raw
        elif str(w_raw).lower() in ['true', '1']:
            cleaned['Weekend'] = True
        elif str(w_raw).lower() in ['false', '0']:
            cleaned['Weekend'] = False
        else:
            errors.append(f"Trường 'Weekend' phải là giá trị boolean (True/False), nhận được: {w_raw}")
            
    if 'PageValues' in data and data['PageValues'] is not None and str(data['PageValues']).strip() != "":
        try:
            pv_val = float(data['PageValues'])
            cleaned['PageValues'] = pv_val
            if pv_val > 0:
                warnings.append(
                    f"[CẢNH BÁO KIỂM TOÁN RÒ RỈ]: Bạn đã nhập 'PageValues' = {pv_val}. "
                    "Biến này là biến HẬU KẾT QUẢ (Outcome Proxy) từ Google Analytics và BỊ CẤM trong mô hình chính. "
                    "Hệ thống sẽ chỉ dùng nó để minh họa mức độ sai lệch của mô hình ngây thơ!"
                )
        except (ValueError, TypeError):
            errors.append("Trường 'PageValues' phải là số thực.")
    else:
        cleaned['PageValues'] = 0.0

    return errors, warnings, cleaned


@app.route('/')
def home():
    """Trang chủ ứng dụng web 3 màn hình."""
    return render_template(
        'index.html',
        train_summary=TRAIN_SUMMARY,
        data_quality=DATA_QUALITY,
        bounds=VALID_BOUNDS
    )


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint kiểm tra trạng thái dịch vụ."""
    return jsonify({
        "status": "healthy",
        "service": "Online Shoppers Purchasing Intention Scoring API",
        "honest_model_loaded": HONEST_PIPELINE is not None,
        "naive_model_loaded": NAIVE_PIPELINE is not None,
        "best_honest_model": TRAIN_SUMMARY.get('best_model_name', 'Honest Random Forest')
    })


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Endpoint cung cấp số liệu thực nghiệm và báo cáo kiểm toán."""
    return jsonify({
        "experiment_results": EXP_RESULTS,
        "training_summary": TRAIN_SUMMARY,
        "data_quality": DATA_QUALITY
    })


@app.route('/api/session-score', methods=['POST'])
def score_session():
    """API tính điểm và dự đoán phiên mua hàng.
    
    Yêu cầu phương thức POST kèm JSON chứa thông tin phiên tổng hợp.
    """
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Content-Type phải là 'application/json'"
        }), 400
        
    payload = request.get_json()
    errors, warnings, cleaned = validate_session_payload(payload)
    
    if errors:
        return jsonify({
            "status": "error",
            "message": "Dữ liệu đầu vào không hợp lệ hoặc thiếu trường bắt buộc.",
            "errors": errors
        }), 422

    if HONEST_PIPELINE is None:
        return jsonify({
            "status": "error",
            "message": "Mô hình chưa được nạp. Vui lòng kiểm tra thư mục models/."
        }), 500

    input_df = pd.DataFrame([cleaned])
    
    honest_prob = float(HONEST_PIPELINE.predict_proba(input_df)[:, 1][0])
    threshold = float(TRAIN_SUMMARY.get('best_threshold', 0.518))
    honest_pred = bool(honest_prob >= threshold)
    
    if honest_prob >= 0.70:
        intent_level = "Rất cao (Very High Intent)"
        action_recommendation = "Ưu tiên hiển thị ưu đãi chốt đơn ngay hoặc hỗ trợ thanh toán nhanh."
    elif honest_prob >= 0.45:
        intent_level = "Trung bình - Khá (Moderate Intent)"
        action_recommendation = "Cung cấp mã giảm giá vận chuyển hoặc gợi ý đánh giá sản phẩm."
    elif honest_prob >= 0.20:
        intent_level = "Thấp (Browsing / Low Intent)"
        action_recommendation = "Gợi ý các mặt hàng phổ biến để kích thích thêm nhu cầu duyệt trang."
    else:
        intent_level = "Rất thấp / Khách rời trang (Very Low)"
        action_recommendation = "Không can thiệp quá mức để tránh làm phiền trải nghiệm người dùng."

    response = {
        "status": "success",
        "observation_unit": "Bản tóm tắt phiên duyệt web cuối phiên (End-of-Session Aggregate)",
        "prediction": {
            "will_purchase": honest_pred,
            "purchase_probability": round(honest_prob, 4),
            "purchase_probability_percentage": f"{honest_prob * 100:.2f}%",
            "decision_threshold": threshold,
            "intent_level": intent_level,
            "action_recommendation": action_recommendation
        },
        "model_audit_info": {
            "model_type": "Honest Random Forest (Trung thực)",
            "page_values_used": False,
            "audit_disclaimer": (
                "Mô hình được huấn luyện hoàn toàn không chứa thuộc tính PageValues "
                "để loại bỏ rò rỉ dữ liệu (Target Proxy Leakage). "
                "Điểm số phản ánh đúng hành vi thực tế của phiên duyệt."
            )
        },
        "warnings": warnings
    }

    has_custom_pv = 'PageValues' in payload and payload['PageValues'] not in [None, 0, "0", ""]
    if has_custom_pv and NAIVE_PIPELINE is not None:
        naive_prob = float(NAIVE_PIPELINE.predict_proba(input_df)[:, 1][0])
        naive_pred = bool(naive_prob >= 0.5)
        pv_val = cleaned.get('PageValues', 0.0)
        
        response["leakage_comparison"] = {
            "naive_probability": round(naive_prob, 4),
            "naive_probability_percentage": f"{naive_prob * 100:.2f}%",
            "naive_prediction": naive_pred,
            "page_values_provided": pv_val,
            "probability_inflation_delta": round(naive_prob - honest_prob, 4),
            "inflation_percentage": f"{(naive_prob - honest_prob) * 100:+.2f}%",
            "leakage_warning": (
                f"Ảo tưởng mô hình (Shortcut Learning): Biến PageValues={pv_val} khiến xác suất bị thổi phồng "
                f"từ {honest_prob*100:.1f}% lên {naive_prob*100:.1f}%. "
                "Tuyệt đối không sử dụng điểm số này trong môi trường sản xuất thực tế!"
            )
        }
        
    return jsonify(response), 200


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("KHỞI CHẠY HỆ THỐNG PHỤC VỤ DỰ ĐOÁN & KIỂM TOÁN RÒ RỈ (WEB & API)")
    print("Truy cập Web: http://127.0.0.1:5000")
    print("API Endpoint: POST http://127.0.0.1:5000/api/session-score")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=False)
