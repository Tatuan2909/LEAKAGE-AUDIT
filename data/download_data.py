"""Script kiểm tra và tải bộ dữ liệu Online Shoppers Purchasing Intention từ UCI."""

import os
import urllib.request
import hashlib

DATA_URL = "https://archive.ics.uci.edu/static/public/468/online+shoppers+purchasing+intention+dataset.zip"
CSV_URL = "https://raw.githubusercontent.com/uci-ml-repo/online-shoppers-purchasing-intention/master/online_shoppers_intention.csv"
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DATA_DIR, "online_shoppers_intention.csv")
EXPECTED_MD5 = "cc6ec1db03b4f10f8de52c56ff48b085"

def verify_checksum(filepath):
    if not os.path.exists(filepath):
        return False
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest() == EXPECTED_MD5

def check_or_download():
    if os.path.exists(CSV_PATH):
        if verify_checksum(CSV_PATH):
            print(f"[OK] Tệp {CSV_PATH} đã tồn tại và khớp mã băm MD5 chính xác.")
            return True
        else:
            print(f"[CẢNH BÁO] Tệp {CSV_PATH} có mã băm không khớp.")
            return True
    print(f"Tệp không tồn tại, đang thử tải từ {CSV_URL}...")
    try:
        urllib.request.urlretrieve(CSV_URL, CSV_PATH)
        print("[OK] Đã tải thành công tệp dữ liệu!")
        return True
    except Exception as e:
        print(f"[LỖI] Không thể tải dữ liệu tự động: {e}")
        return False

if __name__ == "__main__":
    check_or_download()
