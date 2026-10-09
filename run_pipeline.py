"""Script tự động hóa toàn bộ quy trình từ dữ liệu thô đến đánh giá (End-to-End Pipeline).

Chạy lệnh:
    python run_pipeline.py
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def run_step(step_name, script_path):
    print("\n" + "=" * 60)
    print(f">> [BƯỚC] {step_name} ({script_path})")
    print("=" * 60)
    cmd = [sys.executable, script_path]
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    res = subprocess.run(cmd, cwd=BASE_DIR, env=env)
    if res.returncode != 0:
        print(f"\n[LỖI NGHIÊM TRỌNG] Bước {step_name} thất bại với mã lỗi {res.returncode}!")
        sys.exit(res.returncode)
    print(f">> [HOÀN TẤT] {step_name} thành công!")


def main():
    print("****************************************************************")
    print(" PROJECT 19: DỰ ĐOÁN PHIÊN MUA HÀNG VỚI KIỂM TOÁN RÒ RỈ")
    print(" REPRODUCIBLE END-TO-END PIPELINE RUNNER")
    print("****************************************************************")
    
    run_step("1. Kiểm tra tính toàn vẹn bộ dữ liệu thô", os.path.join(BASE_DIR, "data", "download_data.py"))
    run_step("2. Kiểm toán chất lượng và Stratified Split không rò rỉ", os.path.join(BASE_DIR, "src", "data.py"))
    run_step("3. Huấn luyện mô hình và tối ưu tham số trên Train", os.path.join(BASE_DIR, "src", "train.py"))
    run_step("4. Đánh giá trên Test và thực hiện 4 thí nghiệm", os.path.join(BASE_DIR, "src", "evaluate.py"))
    
    print("\n" + "=" * 60)
    print(">> [BƯỚC] 5. Đồng bộ đồ thị thực nghiệm sang static assets của Web...")
    print("=" * 60)
    src_fig = os.path.join(BASE_DIR, "reports", "figures")
    dst_fig = os.path.join(BASE_DIR, "app", "static", "figures")
    os.makedirs(dst_fig, exist_ok=True)
    for fname in os.listdir(src_fig):
        if fname.endswith(".png"):
            shutil.copy2(os.path.join(src_fig, fname), os.path.join(dst_fig, fname))
    print(f"Đã sao chép toàn bộ đồ thị sang {dst_fig}")

    run_step("6. Kiểm thử tự động Unit Tests & API Test Client", os.path.join(BASE_DIR, "test_api.py"))
    
    print("\n" + "*" * 64)
    print(" TẤT CẢ CÁC BƯỚC ĐÃ ĐƯỢC THỰC THI THÀNH CÔNG VÀ HOÀN TOÀN TÁI LẬP!")
    print(" Để khởi động ứng dụng Web & API, hãy chạy:")
    print("     python app/app.py")
    print(" Sau đó mở trình duyệt tại: http://127.0.0.1:5000")
    print("*" * 64)


if __name__ == "__main__":
    main()
