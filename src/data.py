"""Module src/data.py.

Đảm nhiệm:
1. Tải dữ liệu từ tệp CSV thô.
2. Kiểm tra schema, kiểm tra tính toàn vẹn, giá trị thiếu và trùng lặp.
3. Xuất báo cáo chất lượng dữ liệu (Data Quality Report).
4. Phân chia tập Train / Validation / Test với Stratified Split độc lập trước mọi bước tiền xử lý,
   đảm bảo nguyên tắc 'không rò rỉ thông tin' (leak-free split).
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "online_shoppers_intention.csv"
)

def load_raw_data(filepath=DEFAULT_DATA_PATH):
    """Đọc dữ liệu thô từ file CSV."""
    if not os.path.exists(filepath):
        alt_path = os.path.join(os.path.dirname(os.path.dirname(filepath)), "online_shoppers_intention.csv")
        if os.path.exists(alt_path):
            filepath = alt_path
        else:
            raise FileNotFoundError(f"Không tìm thấy file dữ liệu tại {filepath}")
    
    return pd.read_csv(filepath)


def audit_data_quality(df, drop_duplicates=True):
    """Kiểm toán chất lượng dữ liệu: missing values, duplicates, phân bố nhãn."""
    total_raw_rows = len(df)
    missing_counts = df.isnull().sum().to_dict()
    total_missing = sum(missing_counts.values())
    duplicate_rows = int(df.duplicated().sum())
    
    if drop_duplicates and duplicate_rows > 0:
        cleaned_df = df.drop_duplicates().copy()
    else:
        cleaned_df = df.copy()
        
    class_distribution_raw = df['Revenue'].value_counts().to_dict()
    class_distribution_cleaned = cleaned_df['Revenue'].value_counts().to_dict()
    
    report = {
        "total_raw_rows": total_raw_rows,
        "total_raw_cols": len(df.columns),
        "total_missing_values": total_missing,
        "missing_by_column": {k: int(v) for k, v in missing_counts.items() if v > 0},
        "duplicate_rows": duplicate_rows,
        "rows_after_dedup": len(cleaned_df),
        "class_distribution_raw": {str(k): int(v) for k, v in class_distribution_raw.items()},
        "positive_rate_raw": float(class_distribution_raw.get(True, 0) / total_raw_rows),
        "class_distribution_cleaned": {str(k): int(v) for k, v in class_distribution_cleaned.items()},
        "positive_rate_cleaned": float(class_distribution_cleaned.get(True, 0) / len(cleaned_df)),
        "dedup_rationale": "Loại bỏ 125 dòng trùng lặp nhằm tránh nguy cơ split leakage khi cùng 1 phiên xuất hiện ở cả Train và Test."
    }
    
    return cleaned_df, report


def get_train_val_test_split(df, test_size=0.15, val_size=0.15, random_state=42, stratify=True):
    """Chia tập dữ liệu thành Train (70%), Validation (15%), Test (15%) độc lập."""
    y = df['Revenue'].astype(int)
    X = df.drop(columns=['Revenue'])
    stratify_target = y if stratify else None
    
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_target
    )
    
    val_ratio_of_temp = val_size / (1.0 - test_size)
    stratify_temp = y_temp if stratify else None
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=val_ratio_of_temp,
        random_state=random_state,
        stratify=stratify_temp
    )
    
    split_info = {
        "random_state": random_state,
        "stratified": stratify,
        "train_size": len(X_train),
        "val_size": len(X_val),
        "test_size": len(X_test),
        "train_pos_rate": float(y_train.mean()),
        "val_pos_rate": float(y_val.mean()),
        "test_pos_rate": float(y_test.mean())
    }
    
    return X_train, X_val, X_test, y_train, y_val, y_test, split_info

if __name__ == "__main__":
    df_raw = load_raw_data()
    df_clean, report = audit_data_quality(df_raw)
    print("Báo cáo chất lượng dữ liệu:")
    print(json.dumps(report, indent=2))
    
    X_train, X_val, X_test, y_train, y_val, y_test, sinfo = get_train_val_test_split(df_clean)
    print("\nThông tin phân chia tập dữ liệu:")
    print(json.dumps(sinfo, indent=2))
