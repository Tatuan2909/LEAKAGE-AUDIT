"""Module src/train.py.

Đảm nhiệm:
1. Huấn luyện các mô hình Baseline:
   - Dummy Classifier (đa số / prior)
   - Simple Logistic Regression (chỉ 4 thuộc tính hành vi)
2. Huấn luyện các mô hình Ngây thơ (Naive - BỊ RÒ RỈ DỮ LIỆU PAGEVALUES):
   - Naive Logistic Regression
   - Naive Random Forest Classifier
3. Huấn luyện các mô hình Trung thực (Honest - LOẠI BỎ HOÀN TOÀN BIẾN RÒ RỈ):
   - Honest Logistic Regression
   - Honest Random Forest Classifier
   - Honest Gradient Boosting Classifier (HistGradientBoostingClassifier)
4. Tối ưu tham số qua Stratified 5-Fold CV trên tập Train (scoring='average_precision').
5. Tối ưu ngưỡng phân biệt (Optimal Threshold) trên tập Validation để cân bằng Precision và Recall.
6. Lưu lại các pipeline hoàn chỉnh vào thư mục models/ phục vụ serving và tái lập.
"""

import os
import sys

# Đảm bảo thư mục gốc dự án nằm trong sys.path
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
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    precision_recall_curve,
    f1_score
)

from src.data import load_raw_data, audit_data_quality, get_train_val_test_split
from src.features import create_pipeline

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def find_best_threshold(y_true, y_probs):
    """Tìm ngưỡng quyết định tối ưu trên tập Validation tối đa hóa F1-score."""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_probs)
    f1_scores = []
    # thresholds có độ dài ít hơn precisions và recalls 1 phần tử
    for p, r in zip(precisions[:-1], recalls[:-1]):
        if (p + r) > 0:
            f1_scores.append(2 * p * r / (p + r))
        else:
            f1_scores.append(0.0)
    best_idx = int(np.argmax(f1_scores))
    best_th = float(thresholds[best_idx])
    best_f1 = float(f1_scores[best_idx])
    return best_th, best_f1


def train_all_models(random_state=42):
    print("=" * 60)
    print("BẮT ĐẦU QUY TRÌNH HUẤN LUYỆN MÔ HÌNH (OFFLINE TRAINING PIPELINE)")
    print("=" * 60)
    
    df_raw = load_raw_data()
    df_clean, audit_rep = audit_data_quality(df_raw, drop_duplicates=True)
    with open(os.path.join(MODELS_DIR, "data_quality_report.json"), "w", encoding="utf-8") as f:
        json.dump(audit_rep, f, indent=2, ensure_ascii=False)
    print(f"[1/5] Dữ liệu sau khử trùng lặp: {len(df_clean)} dòng. Đã lưu báo cáo chất lượng dữ liệu.")
    
    X_train, X_val, X_test, y_train, y_val, y_test, sinfo = get_train_val_test_split(
        df_clean, test_size=0.15, val_size=0.15, random_state=random_state, stratify=True
    )
    test_df = pd.concat([X_test, y_test.rename("Revenue")], axis=1)
    test_df.to_csv(os.path.join(MODELS_DIR, "test_dataset_frozen.csv"), index=False)
    val_df = pd.concat([X_val, y_val.rename("Revenue")], axis=1)
    val_df.to_csv(os.path.join(MODELS_DIR, "val_dataset_frozen.csv"), index=False)
    print(f"[2/5] Đã chia tập độc lập: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    cv_stratified = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    trained_artifacts = {}
    
    print("\n[3/5] Huấn luyện các mô hình Baseline...")
    dummy = DummyClassifier(strategy='prior')
    dummy.fit(X_train, y_train)
    dummy_val_probs = dummy.predict_proba(X_val)[:, 1]
    dummy_pr_auc = float(average_precision_score(y_val, dummy_val_probs))
    dummy_roc_auc = float(roc_auc_score(y_val, dummy_val_probs))
    joblib.dump(dummy, os.path.join(MODELS_DIR, "dummy_model.joblib"))
    trained_artifacts['baseline_dummy'] = {
        'name': 'Baseline: Dummy (Majority Class)',
        'val_pr_auc': dummy_pr_auc,
        'val_roc_auc': dummy_roc_auc,
        'threshold': 0.5
    }
    print(f" -> Dummy Classifier: Val PR-AUC = {dummy_pr_auc:.4f}, ROC-AUC = {dummy_roc_auc:.4f}")
    
    base_lr_pipe = create_pipeline(
        LogisticRegression(max_iter=1000, random_state=random_state, class_weight='balanced'),
        mode='baseline'
    )
    base_lr_pipe.fit(X_train, y_train)
    base_lr_val_probs = base_lr_pipe.predict_proba(X_val)[:, 1]
    base_lr_pr_auc = float(average_precision_score(y_val, base_lr_val_probs))
    base_lr_roc_auc = float(roc_auc_score(y_val, base_lr_val_probs))
    joblib.dump(base_lr_pipe, os.path.join(MODELS_DIR, "pipeline_baseline_lr.joblib"))
    trained_artifacts['baseline_lr'] = {
        'name': 'Baseline: Logistic Regression (4 biến hành vi)',
        'val_pr_auc': base_lr_pr_auc,
        'val_roc_auc': base_lr_roc_auc,
        'threshold': 0.5
    }
    print(f" -> Simple Baseline LR: Val PR-AUC = {base_lr_pr_auc:.4f}, ROC-AUC = {base_lr_roc_auc:.4f}")
    
    print("\n[4/5] Huấn luyện các mô hình Ngây thơ (Naive - Rò rỉ PageValues)...")
    naive_lr_pipe = create_pipeline(
        LogisticRegression(max_iter=1000, random_state=random_state, class_weight='balanced'),
        mode='naive'
    )
    naive_lr_pipe.fit(X_train, y_train)
    naive_lr_val_probs = naive_lr_pipe.predict_proba(X_val)[:, 1]
    naive_lr_pr_auc = float(average_precision_score(y_val, naive_lr_val_probs))
    naive_lr_roc_auc = float(roc_auc_score(y_val, naive_lr_val_probs))
    joblib.dump(naive_lr_pipe, os.path.join(MODELS_DIR, "pipeline_naive_lr.joblib"))
    trained_artifacts['naive_lr'] = {
        'name': 'Naive LR (Có biến rò rỉ PageValues)',
        'val_pr_auc': naive_lr_pr_auc,
        'val_roc_auc': naive_lr_roc_auc,
        'threshold': 0.5
    }
    print(f" -> Naive LR: Val PR-AUC = {naive_lr_pr_auc:.4f}, ROC-AUC = {naive_lr_roc_auc:.4f}")
    
    naive_rf_pipe = create_pipeline(
        RandomForestClassifier(n_estimators=100, max_depth=8, random_state=random_state, class_weight='balanced'),
        mode='naive'
    )
    naive_rf_pipe.fit(X_train, y_train)
    naive_rf_val_probs = naive_rf_pipe.predict_proba(X_val)[:, 1]
    naive_rf_pr_auc = float(average_precision_score(y_val, naive_rf_val_probs))
    naive_rf_roc_auc = float(roc_auc_score(y_val, naive_rf_val_probs))
    joblib.dump(naive_rf_pipe, os.path.join(MODELS_DIR, "pipeline_naive_rf.joblib"))
    trained_artifacts['naive_rf'] = {
        'name': 'Naive RF (Có biến rò rỉ PageValues)',
        'val_pr_auc': naive_rf_pr_auc,
        'val_roc_auc': naive_rf_roc_auc,
        'threshold': 0.5
    }
    print(f" -> Naive RF: Val PR-AUC = {naive_rf_pr_auc:.4f}, ROC-AUC = {naive_rf_roc_auc:.4f}")
    
    print("\n[5/5] Huấn luyện và tinh chỉnh các mô hình Trung thực (Honest - Không rò rỉ)...")
    honest_lr_base = create_pipeline(
        LogisticRegression(max_iter=1000, random_state=random_state, class_weight='balanced'),
        mode='honest'
    )
    param_grid_lr = {
        'classifier__C': [0.01, 0.1, 1.0, 10.0]
    }
    grid_lr = GridSearchCV(
        honest_lr_base,
        param_grid_lr,
        cv=cv_stratified,
        scoring='average_precision',
        n_jobs=-1
    )
    grid_lr.fit(X_train, y_train)
    honest_lr_best = grid_lr.best_estimator_
    honest_lr_val_probs = honest_lr_best.predict_proba(X_val)[:, 1]
    honest_lr_pr_auc = float(average_precision_score(y_val, honest_lr_val_probs))
    honest_lr_roc_auc = float(roc_auc_score(y_val, honest_lr_val_probs))
    th_lr, f1_lr = find_best_threshold(y_val, honest_lr_val_probs)
    joblib.dump(honest_lr_best, os.path.join(MODELS_DIR, "pipeline_honest_lr.joblib"))
    trained_artifacts['honest_lr'] = {
        'name': 'Honest Logistic Regression (Không PageValues)',
        'best_params': grid_lr.best_params_,
        'val_pr_auc': honest_lr_pr_auc,
        'val_roc_auc': honest_lr_roc_auc,
        'best_threshold': th_lr,
        'best_f1_val': f1_lr
    }
    print(f" -> Honest LR: Val PR-AUC = {honest_lr_pr_auc:.4f}, ROC-AUC = {honest_lr_roc_auc:.4f}, Best Threshold = {th_lr:.3f}")
    
    honest_rf_base = create_pipeline(
        RandomForestClassifier(n_estimators=150, random_state=random_state, class_weight='balanced'),
        mode='honest'
    )
    param_grid_rf = {
        'classifier__max_depth': [6, 10, 14],
        'classifier__min_samples_leaf': [2, 5]
    }
    grid_rf = GridSearchCV(
        honest_rf_base,
        param_grid_rf,
        cv=cv_stratified,
        scoring='average_precision',
        n_jobs=-1
    )
    grid_rf.fit(X_train, y_train)
    honest_rf_best = grid_rf.best_estimator_
    honest_rf_val_probs = honest_rf_best.predict_proba(X_val)[:, 1]
    honest_rf_pr_auc = float(average_precision_score(y_val, honest_rf_val_probs))
    honest_rf_roc_auc = float(roc_auc_score(y_val, honest_rf_val_probs))
    th_rf, f1_rf = find_best_threshold(y_val, honest_rf_val_probs)
    joblib.dump(honest_rf_best, os.path.join(MODELS_DIR, "pipeline_honest_rf.joblib"))
    trained_artifacts['honest_rf'] = {
        'name': 'Honest Random Forest (Không PageValues)',
        'best_params': grid_rf.best_params_,
        'val_pr_auc': honest_rf_pr_auc,
        'val_roc_auc': honest_rf_roc_auc,
        'best_threshold': th_rf,
        'best_f1_val': f1_rf
    }
    print(f" -> Honest RF: Val PR-AUC = {honest_rf_pr_auc:.4f}, ROC-AUC = {honest_rf_roc_auc:.4f}, Best Threshold = {th_rf:.3f}")
    
    honest_gb_base = create_pipeline(
        HistGradientBoostingClassifier(random_state=random_state, class_weight='balanced', max_iter=100),
        mode='honest'
    )
    honest_gb_base.fit(X_train, y_train)
    honest_gb_val_probs = honest_gb_base.predict_proba(X_val)[:, 1]
    honest_gb_pr_auc = float(average_precision_score(y_val, honest_gb_val_probs))
    honest_gb_roc_auc = float(roc_auc_score(y_val, honest_gb_val_probs))
    th_gb, f1_gb = find_best_threshold(y_val, honest_gb_val_probs)
    joblib.dump(honest_gb_base, os.path.join(MODELS_DIR, "pipeline_honest_gb.joblib"))
    trained_artifacts['honest_gb'] = {
        'name': 'Honest HistGradientBoosting (Không PageValues)',
        'val_pr_auc': honest_gb_pr_auc,
        'val_roc_auc': honest_gb_roc_auc,
        'best_threshold': th_gb,
        'best_f1_val': f1_gb
    }
    print(f" -> Honest Gradient Boosting: Val PR-AUC = {honest_gb_pr_auc:.4f}, ROC-AUC = {honest_gb_roc_auc:.4f}, Best Threshold = {th_gb:.3f}")
    
    honest_candidates = [
        ('honest_rf', honest_rf_pr_auc, honest_rf_best, th_rf),
        ('honest_gb', honest_gb_pr_auc, honest_gb_base, th_gb),
        ('honest_lr', honest_lr_pr_auc, honest_lr_best, th_lr)
    ]
    honest_candidates.sort(key=lambda x: x[1], reverse=True)
    best_honest_key, best_honest_prauc, best_honest_pipeline, best_honest_th = honest_candidates[0]
    
    joblib.dump(best_honest_pipeline, os.path.join(MODELS_DIR, "pipeline_honest_best.joblib"))
    
    summary_info = {
        'best_model_key': best_honest_key,
        'best_model_name': trained_artifacts[best_honest_key]['name'],
        'best_threshold': best_honest_th,
        'val_pr_auc': best_honest_prauc,
        'trained_artifacts': trained_artifacts
    }
    
    with open(os.path.join(MODELS_DIR, "training_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_info, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 60)
    print(f"MÔ HÌNH TRUNG THỰC TỐT NHẤT: {trained_artifacts[best_honest_key]['name']}")
    print(f"Validation PR-AUC: {best_honest_prauc:.4f} | Optimal Threshold: {best_honest_th:.3f}")
    print("Toàn bộ pipeline và cấu hình đã được lưu an toàn tại thư mục models/.")
    print("=" * 60)
    return summary_info


if __name__ == "__main__":
    train_all_models()
