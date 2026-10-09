"""Module src/features.py.

Đảm nhiệm:
1. Định nghĩa danh sách các biến theo từng nhóm (Baseline, Honest, Naive).
2. Xây dựng scikit-learn ColumnTransformer và Pipeline:
   - StandardScaler cho các biến liên tục / số lượng.
   - OneHotEncoder cho các biến phân loại (handle_unknown='ignore').
3. Cung cấp hàm khởi tạo Pipeline hoàn chỉnh kết hợp Preprocessor và Classifier.
4. Đảm bảo quy tắc: Fit CHỈ trên tập Train, không bao giờ fit trên Val/Test.
"""

import sys
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASELINE_NUMERIC_FEATURES = [
    'ProductRelated',
    'ProductRelated_Duration',
    'BounceRates',
    'ExitRates'
]

HONEST_NUMERIC_FEATURES = [
    'Administrative',
    'Administrative_Duration',
    'Informational',
    'Informational_Duration',
    'ProductRelated',
    'ProductRelated_Duration',
    'BounceRates',
    'ExitRates',
    'SpecialDay'
]

HONEST_CATEGORICAL_FEATURES = [
    'Month',
    'OperatingSystems',
    'Browser',
    'Region',
    'TrafficType',
    'VisitorType',
    'Weekend'
]

NAIVE_NUMERIC_FEATURES = HONEST_NUMERIC_FEATURES + ['PageValues']
NAIVE_CATEGORICAL_FEATURES = HONEST_CATEGORICAL_FEATURES


def get_preprocessor(mode='honest'):
    """Tạo ColumnTransformer tiền xử lý chuẩn hóa và mã hóa one-hot.
    
    mode: 'honest', 'naive', hoặc 'baseline'
    """
    if mode == 'baseline':
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), BASELINE_NUMERIC_FEATURES)
            ],
            remainder='drop'
        )
    elif mode == 'naive':
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), NAIVE_NUMERIC_FEATURES),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), NAIVE_CATEGORICAL_FEATURES)
            ],
            remainder='drop'
        )
    elif mode == 'honest':
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), HONEST_NUMERIC_FEATURES),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), HONEST_CATEGORICAL_FEATURES)
            ],
            remainder='drop'
        )
    else:
        raise ValueError(f"Chế độ tiền xử lý không hợp lệ: {mode}")
        
    return preprocessor


def create_pipeline(classifier, mode='honest'):
    """Đóng gói Preprocessor và Classifier thành một Pipeline hoàn chỉnh."""
    preprocessor = get_preprocessor(mode=mode)
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', classifier)
    ])
    return pipeline


if __name__ == "__main__":
    from sklearn.linear_model import LogisticRegression
    pipe_honest = create_pipeline(LogisticRegression(), mode='honest')
    print("Khởi tạo Honest Pipeline thành công:")
    print(pipe_honest)
    
    pipe_naive = create_pipeline(LogisticRegression(), mode='naive')
    print("\nKhởi tạo Naive Pipeline thành công:")
    print(pipe_naive)
