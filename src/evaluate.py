"""Module src/evaluate.py.

Thực hiện đánh giá một lần trung thực trên Test Set và thực hiện đầy đủ
BỐN THÍ NGHIỆM BẮT BUỘC theo đề bài:
1. Thí nghiệm 1: So sánh random stratified split ổn định qua seed (Stratified vs Unstratified).
2. Thí nghiệm 2: So sánh có / không PageValues (Leakage Audit & Feature Importance Shift).
3. Thí nghiệm 3: PR curve do mất cân bằng dữ liệu (so sánh PR curve vs ROC curve và No-skill baseline).
4. Thí nghiệm 4: Calibration curve (Reliability Diagram) và phân tích sai số (Error breakdown) theo VisitorType & Month.

Tất cả các biểu đồ trực quan hóa được lưu vào reports/figures/
Tất cả các bảng số liệu chi tiết được xuất thành models/experiment_results.json.
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
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    precision_recall_curve,
    roc_curve,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score
)
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from src.data import load_raw_data, audit_data_quality, get_train_val_test_split
from src.features import create_pipeline

FIGURES_DIR = os.path.join(BASE_DIR, "reports", "figures")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Cấu hình thẩm mỹ đồ thị khoa học
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8


def run_experiment_1_seed_stability(df_clean, seeds=[42, 100, 2024, 777, 999]):
    """Thí nghiệm 1: So sánh random stratified split ổn định qua seed.
    
    So sánh Stratified Split vs Unstratified Split trên 5 seed ngẫu nhiên.
    """
    print("\n[Thí nghiệm 1] Đang thực hiện kiểm tra tính ổn định của Stratified Split qua các seed...")
    results_strat = []
    results_unstrat = []
    
    for s in seeds:
        X_tr, _, X_te, y_tr, _, y_te, sinfo_s = get_train_val_test_split(df_clean, random_state=s, stratify=True)
        pipe_s = create_pipeline(LogisticRegression(max_iter=1000, random_state=s, class_weight='balanced'), mode='honest')
        pipe_s.fit(X_tr, y_tr)
        probs_s = pipe_s.predict_proba(X_te)[:, 1]
        pr_s = average_precision_score(y_te, probs_s)
        roc_s = roc_auc_score(y_te, probs_s)
        results_strat.append({
            'seed': s,
            'train_pos_rate': sinfo_s['train_pos_rate'],
            'test_pos_rate': sinfo_s['test_pos_rate'],
            'pr_auc': float(pr_s),
            'roc_auc': float(roc_s)
        })
        
        X_tr_u, _, X_te_u, y_tr_u, _, y_te_u, sinfo_u = get_train_val_test_split(df_clean, random_state=s, stratify=False)
        pipe_u = create_pipeline(LogisticRegression(max_iter=1000, random_state=s, class_weight='balanced'), mode='honest')
        pipe_u.fit(X_tr_u, y_tr_u)
        probs_u = pipe_u.predict_proba(X_te_u)[:, 1]
        pr_u = average_precision_score(y_te_u, probs_u)
        roc_u = roc_auc_score(y_te_u, probs_u)
        results_unstrat.append({
            'seed': s,
            'train_pos_rate': sinfo_u['train_pos_rate'],
            'test_pos_rate': sinfo_u['test_pos_rate'],
            'pr_auc': float(pr_u),
            'roc_auc': float(roc_u)
        })
        
    df_res_strat = pd.DataFrame(results_strat)
    df_res_unstrat = pd.DataFrame(results_unstrat)
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    x_axis = np.arange(len(seeds))
    width = 0.35
    axes[0].bar(x_axis - width/2, df_res_strat['test_pos_rate'] * 100, width, label='Stratified Test Pos %', color='#2563eb')
    axes[0].bar(x_axis + width/2, df_res_unstrat['test_pos_rate'] * 100, width, label='Unstratified Test Pos %', color='#f97316')
    axes[0].axhline(df_clean['Revenue'].mean() * 100, color='#dc2626', linestyle='--', label=f'True Dataset Mean ({df_clean["Revenue"].mean()*100:.2f}%)')
    axes[0].set_xticks(x_axis)
    axes[0].set_xticklabels([f"Seed {s}" for s in seeds])
    axes[0].set_ylabel("Tỷ lệ nhãn dương Positive Rate (%)", fontsize=11)
    axes[0].set_title("(A) Độ lệch tỷ lệ lớp qua các Seed (Stratified vs Unstratified)", fontsize=12, fontweight='bold')
    axes[0].legend(loc='lower right', frameon=True)
    axes[0].set_ylim(13, 18)
    
    axes[1].plot(seeds, df_res_strat['pr_auc'], marker='o', linewidth=2, color='#2563eb', label=f'Stratified (Mean: {df_res_strat["pr_auc"].mean():.4f} ± {df_res_strat["pr_auc"].std():.4f})')
    axes[1].plot(seeds, df_res_unstrat['pr_auc'], marker='s', linewidth=2, linestyle='--', color='#f97316', label=f'Unstratified (Mean: {df_res_unstrat["pr_auc"].mean():.4f} ± {df_res_unstrat["pr_auc"].std():.4f})')
    axes[1].set_xlabel("Random Seed", fontsize=11)
    axes[1].set_ylabel("PR-AUC trên Test Set", fontsize=11)
    axes[1].set_title("(B) Tính ổn định của Metric PR-AUC qua các Seed", fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', frameon=True)
    
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, "exp1_seed_stability.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f" -> Đã lưu biểu đồ: {fig_path}")
    
    return {
        'seeds': seeds,
        'stratified_results': results_strat,
        'unstratified_results': results_unstrat,
        'strat_pr_auc_mean': float(df_res_strat['pr_auc'].mean()),
        'strat_pr_auc_std': float(df_res_strat['pr_auc'].std()),
        'unstrat_pr_auc_mean': float(df_res_unstrat['pr_auc'].mean()),
        'unstrat_pr_auc_std': float(df_res_unstrat['pr_auc'].std())
    }


def run_experiment_2_leakage_audit(models_dict, X_test, y_test):
    """Thí nghiệm 2: So sánh có / không PageValues và phân tích rò rỉ."""
    print("\n[Thí nghiệm 2] Đang kiểm toán rò rỉ dữ liệu (Naive vs Honest Models)...")
    
    metrics = {}
    for key, model in models_dict.items():
        probs = model.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.5).astype(int)
        
        pr_auc = float(average_precision_score(y_test, probs))
        roc_auc = float(roc_auc_score(y_test, probs))
        prec = float(precision_score(y_test, preds, zero_division=0))
        rec = float(recall_score(y_test, preds, zero_division=0))
        f1 = float(f1_score(y_test, preds, zero_division=0))
        brier = float(brier_score_loss(y_test, probs))
        
        metrics[key] = {
            'pr_auc': pr_auc,
            'roc_auc': roc_auc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'brier_score': brier
        }
        print(f" -> {key:18s}: PR-AUC={pr_auc:.4f} | ROC-AUC={roc_auc:.4f} | F1={f1:.4f} | Brier={brier:.4f}")
        
    comp_labels = ['Logistic Regression', 'Random Forest']
    naive_pr = [metrics['naive_lr']['pr_auc'], metrics['naive_rf']['pr_auc']]
    honest_pr = [metrics['honest_lr']['pr_auc'], metrics['honest_rf']['pr_auc']]
    naive_roc = [metrics['naive_lr']['roc_auc'], metrics['naive_rf']['roc_auc']]
    honest_roc = [metrics['honest_lr']['roc_auc'], metrics['honest_rf']['roc_auc']]
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    x = np.arange(len(comp_labels))
    width = 0.35
    
    axes[0].bar(x - width/2, naive_pr, width, label='Naive (Có PageValues - Leakage)', color='#dc2626')
    axes[0].bar(x + width/2, honest_pr, width, label='Honest (Loại bỏ PageValues)', color='#16a34a')
    for i in range(len(x)):
        axes[0].text(x[i] - width/2, naive_pr[i] + 0.015, f"{naive_pr[i]:.3f}", ha='center', fontsize=9, fontweight='bold', color='#dc2626')
        axes[0].text(x[i] + width/2, honest_pr[i] + 0.015, f"{honest_pr[i]:.3f}", ha='center', fontsize=9, fontweight='bold', color='#16a34a')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(comp_labels, fontsize=11)
    axes[0].set_ylabel("PR-AUC (Độ chính xác trung bình)", fontsize=11)
    axes[0].set_title("(A) So sánh PR-AUC: Sự sụp đổ điểm số khi loại bỏ rò rỉ", fontsize=12, fontweight='bold')
    axes[0].set_ylim(0, 0.8)
    axes[0].legend(loc='upper right', frameon=True)
    
    axes[1].bar(x - width/2, naive_roc, width, label='Naive (Có PageValues - Leakage)', color='#dc2626')
    axes[1].bar(x + width/2, honest_roc, width, label='Honest (Loại bỏ PageValues)', color='#16a34a')
    for i in range(len(x)):
        axes[1].text(x[i] - width/2, naive_roc[i] + 0.015, f"{naive_roc[i]:.3f}", ha='center', fontsize=9, fontweight='bold', color='#dc2626')
        axes[1].text(x[i] + width/2, honest_roc[i] + 0.015, f"{honest_roc[i]:.3f}", ha='center', fontsize=9, fontweight='bold', color='#16a34a')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(comp_labels, fontsize=11)
    axes[1].set_ylabel("ROC-AUC", fontsize=11)
    axes[1].set_title("(B) So sánh ROC-AUC: Ảo tưởng hiệu năng trong mô hình ngây thơ", fontsize=12, fontweight='bold')
    axes[1].set_ylim(0, 1.05)
    axes[1].legend(loc='upper right', frameon=True)
    
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, "exp2_leakage_audit_comparison.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f" -> Đã lưu biểu đồ: {fig_path}")
    
    try:
        rf_naive_model = models_dict['naive_rf'].named_steps['classifier']
        rf_honest_model = models_dict['honest_rf'].named_steps['classifier']
        
        pre_naive = models_dict['naive_rf'].named_steps['preprocessor']
        pre_honest = models_dict['honest_rf'].named_steps['preprocessor']
        
        naive_cols = pre_naive.transformers_[0][2] + list(pre_naive.transformers_[1][1].get_feature_names_out(pre_naive.transformers_[1][2]))
        honest_cols = pre_honest.transformers_[0][2] + list(pre_honest.transformers_[1][1].get_feature_names_out(pre_honest.transformers_[1][2]))
        
        imp_naive = pd.Series(rf_naive_model.feature_importances_, index=naive_cols).sort_values(ascending=False).head(10)
        imp_honest = pd.Series(rf_honest_model.feature_importances_, index=honest_cols).sort_values(ascending=False).head(10)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
        sns.barplot(x=imp_naive.values, y=imp_naive.index, ax=axes[0], palette='Reds_r')
        axes[0].set_title("Top 10 Feature Importance: Naive RF (Rò rỉ PageValues)", fontsize=11, fontweight='bold')
        axes[0].set_xlabel("Tỷ trọng quan trọng (Gini Importance)")
        
        sns.barplot(x=imp_honest.values, y=imp_honest.index, ax=axes[1], palette='Greens_r')
        axes[1].set_title("Top 10 Feature Importance: Honest RF (Không PageValues)", fontsize=11, fontweight='bold')
        axes[1].set_xlabel("Tỷ trọng quan trọng (Gini Importance)")
        
        plt.tight_layout()
        fig_feat_path = os.path.join(FIGURES_DIR, "feature_importance_shift.png")
        plt.savefig(fig_feat_path, dpi=300)
        plt.close()
        print(f" -> Đã lưu biểu đồ: {fig_feat_path}")
    except Exception as e:
        print(f"Lưu ý: Không thể xuất biểu đồ feature importance: {e}")
        
    return metrics


def run_experiment_3_pr_vs_roc_curves(models_dict, X_test, y_test):
    """Thí nghiệm 3: Precision-Recall Curve do mất cân bằng dữ liệu."""
    print("\n[Thí nghiệm 3] Đang vẽ đường cong PR và ROC do mất cân bằng dữ liệu...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    no_skill_pr = float(y_test.mean())
    axes[0].plot([0, 1], [no_skill_pr, no_skill_pr], linestyle='--', color='#94a3b8', label=f'No-Skill Baseline ({no_skill_pr*100:.1f}%)')
    axes[1].plot([0, 1], [0, 1], linestyle='--', color='#94a3b8', label='No-Skill (AUC = 0.50)')
    
    curves_data = {}
    display_models = [
        ('honest_rf', 'Honest Random Forest', '#16a34a', '-'),
        ('honest_gb', 'Honest Gradient Boosting', '#2563eb', '-'),
        ('honest_lr', 'Honest Logistic Regression', '#8b5cf6', '-'),
        ('naive_rf', 'Naive RF (Leakage PageValues)', '#dc2626', '--'),
        ('baseline_lr', 'Baseline LR (4 biến)', '#f59e0b', ':')
    ]
    
    for key, label, col, style in display_models:
        if key not in models_dict:
            continue
        model = models_dict[key]
        probs = model.predict_proba(X_test)[:, 1]
        
        p, r, th_pr = precision_recall_curve(y_test, probs)
        pr_score = average_precision_score(y_test, probs)
        axes[0].plot(r, p, linestyle=style, color=col, linewidth=2, label=f"{label} (AP = {pr_score:.3f})")
        
        fpr, tpr, th_roc = roc_curve(y_test, probs)
        roc_score = roc_auc_score(y_test, probs)
        axes[1].plot(fpr, tpr, linestyle=style, color=col, linewidth=2, label=f"{label} (AUC = {roc_score:.3f})")
        
        curves_data[key] = {
            'pr_auc': float(pr_score),
            'roc_auc': float(roc_score)
        }
        
    axes[0].set_xlabel('Recall (Độ nhạy thu hồi)', fontsize=11)
    axes[0].set_ylabel('Precision (Độ chính xác xác nhận)', fontsize=11)
    axes[0].set_title('(A) Precision-Recall Curve (Trọng tâm lớp thiểu số 15.6%)', fontsize=12, fontweight='bold')
    axes[0].legend(loc='lower left', frameon=True, fontsize=9)
    axes[0].set_xlim([0.0, 1.0])
    axes[0].set_ylim([0.0, 1.05])
    
    axes[1].set_xlabel('False Positive Rate (1 - Specificity)', fontsize=11)
    axes[1].set_ylabel('True Positive Rate (Recall)', fontsize=11)
    axes[1].set_title('(B) Receiver Operating Characteristic (ROC Curve)', fontsize=12, fontweight='bold')
    axes[1].legend(loc='lower right', frameon=True, fontsize=9)
    axes[1].set_xlim([0.0, 1.0])
    axes[1].set_ylim([0.0, 1.05])
    
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, "exp3_pr_vs_roc_curve.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f" -> Đã lưu biểu đồ: {fig_path}")
    
    return curves_data


def run_experiment_4_calibration_and_error_breakdown(models_dict, X_test, y_test, df_test_raw):
    """Thí nghiệm 4: Calibration và phân tích sai số theo VisitorType và Month."""
    print("\n[Thí nghiệm 4] Đang kiểm tra Calibration và sai số theo nhóm khách hàng & tháng...")
    
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    ax.plot([0, 1], [0, 1], "k:", label="Hoàn hảo (Perfect Calibration)")
    
    calib_results = {}
    best_honest = models_dict['honest_rf']
    probs_rf = best_honest.predict_proba(X_test)[:, 1]
    frac_pos_rf, mean_prob_rf = calibration_curve(y_test, probs_rf, n_bins=10)
    brier_rf = brier_score_loss(y_test, probs_rf)
    ax.plot(mean_prob_rf, frac_pos_rf, "s-", color='#16a34a', linewidth=2, label=f"Honest Random Forest (Brier = {brier_rf:.4f})")
    calib_results['honest_rf'] = {'brier': float(brier_rf)}
    
    model_lr = models_dict['honest_lr']
    probs_lr = model_lr.predict_proba(X_test)[:, 1]
    frac_pos_lr, mean_prob_lr = calibration_curve(y_test, probs_lr, n_bins=10)
    brier_lr = brier_score_loss(y_test, probs_lr)
    ax.plot(mean_prob_lr, frac_pos_lr, "o-", color='#8b5cf6', linewidth=2, label=f"Honest Logistic Reg (Brier = {brier_lr:.4f})")
    calib_results['honest_lr'] = {'brier': float(brier_lr)}
    
    ax.set_ylabel("Tỷ lệ mẫu dương thực tế (Fraction of Positives)", fontsize=11)
    ax.set_xlabel("Xác suất dự đoán trung bình (Mean Predicted Probability)", fontsize=11)
    ax.set_title("Reliability Diagram: Đánh giá độ chuẩn xác xác suất (Calibration Curve)", fontsize=12, fontweight='bold')
    ax.legend(loc="lower right", frameon=True)
    ax.set_ylim([0.0, 1.05])
    
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, "exp4_calibration_curve.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f" -> Đã lưu biểu đồ: {fig_path}")
    
    test_eval_df = df_test_raw.copy()
    test_eval_df['y_true'] = y_test.values
    test_eval_df['pred_prob'] = probs_rf
    test_eval_df['pred_label'] = (probs_rf >= 0.5).astype(int)
    test_eval_df['correct'] = (test_eval_df['pred_label'] == test_eval_df['y_true']).astype(int)
    
    vt_breakdown = {}
    for vt in test_eval_df['VisitorType'].unique():
        sub = test_eval_df[test_eval_df['VisitorType'] == vt]
        prec = float(precision_score(sub['y_true'], sub['pred_label'], zero_division=0))
        rec = float(recall_score(sub['y_true'], sub['pred_label'], zero_division=0))
        f1 = float(f1_score(sub['y_true'], sub['pred_label'], zero_division=0))
        acc = float(sub['correct'].mean())
        vt_breakdown[vt] = {
            'count': len(sub),
            'pos_count': int(sub['y_true'].sum()),
            'pos_rate': float(sub['y_true'].mean()),
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1
        }
        
    month_breakdown = {}
    month_order = ['Feb', 'Mar', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months_in_test = [m for m in month_order if m in test_eval_df['Month'].values]
    
    for m in months_in_test:
        sub = test_eval_df[test_eval_df['Month'] == m]
        prec = float(precision_score(sub['y_true'], sub['pred_label'], zero_division=0))
        rec = float(recall_score(sub['y_true'], sub['pred_label'], zero_division=0))
        f1 = float(f1_score(sub['y_true'], sub['pred_label'], zero_division=0))
        acc = float(sub['correct'].mean())
        month_breakdown[m] = {
            'count': len(sub),
            'pos_count': int(sub['y_true'].sum()),
            'pos_rate': float(sub['y_true'].mean()),
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1
        }
        
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    m_names = list(month_breakdown.keys())
    m_f1 = [month_breakdown[m]['f1_score'] for m in m_names]
    m_rec = [month_breakdown[m]['recall'] for m in m_names]
    m_prec = [month_breakdown[m]['precision'] for m in m_names]
    
    x_m = np.arange(len(m_names))
    axes[0].plot(x_m, m_f1, marker='o', linewidth=2, color='#2563eb', label='F1-Score')
    axes[0].plot(x_m, m_rec, marker='s', linewidth=2, linestyle='--', color='#16a34a', label='Recall')
    axes[0].plot(x_m, m_prec, marker='^', linewidth=2, linestyle=':', color='#f59e0b', label='Precision')
    axes[0].set_xticks(x_m)
    axes[0].set_xticklabels(m_names)
    axes[0].set_xlabel('Tháng trong năm (Month)', fontsize=11)
    axes[0].set_ylabel('Chỉ số hiệu năng', fontsize=11)
    axes[0].set_title('(A) Hiệu năng mô hình Honest RF biến thiên theo Tháng', fontsize=12, fontweight='bold')
    axes[0].legend(loc='best', frameon=True)
    axes[0].set_ylim([0, 1.05])
    
    vt_names = list(vt_breakdown.keys())
    vt_f1 = [vt_breakdown[v]['f1_score'] for v in vt_names]
    vt_rec = [vt_breakdown[v]['recall'] for v in vt_names]
    vt_prec = [vt_breakdown[v]['precision'] for v in vt_names]
    
    x_v = np.arange(len(vt_names))
    width = 0.25
    axes[1].bar(x_v - width, vt_prec, width, label='Precision', color='#f59e0b')
    axes[1].bar(x_v, vt_rec, width, label='Recall', color='#16a34a')
    axes[1].bar(x_v + width, vt_f1, width, label='F1-Score', color='#2563eb')
    axes[1].set_xticks(x_v)
    axes[1].set_xticklabels([v.replace('_', ' ') for v in vt_names], fontsize=10)
    axes[1].set_ylabel('Chỉ số hiệu năng', fontsize=11)
    axes[1].set_title('(B) Hiệu năng mô hình Honest RF theo Loại khách truy cập', fontsize=12, fontweight='bold')
    axes[1].legend(loc='upper right', frameon=True)
    axes[1].set_ylim([0, 1.05])
    
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, "exp4_error_breakdown.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f" -> Đã lưu biểu đồ: {fig_path}")
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
    cm_honest = confusion_matrix(y_test, (probs_rf >= 0.5).astype(int))
    cm_naive = confusion_matrix(y_test, (models_dict['naive_rf'].predict_proba(X_test)[:, 1] >= 0.5).astype(int))
    
    sns.heatmap(cm_naive, annot=True, fmt='d', cmap='Reds', cbar=False, ax=axes[0])
    axes[0].set_title('Confusion Matrix: Naive RF (Rò rỉ PageValues)', fontsize=11, fontweight='bold')
    axes[0].set_xlabel('Predicted Label')
    axes[0].set_ylabel('True Label')
    
    sns.heatmap(cm_honest, annot=True, fmt='d', cmap='Greens', cbar=False, ax=axes[1])
    axes[1].set_title('Confusion Matrix: Honest RF (Không PageValues)', fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Predicted Label')
    axes[1].set_ylabel('True Label')
    
    plt.tight_layout()
    cm_path = os.path.join(FIGURES_DIR, "confusion_matrices.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f" -> Đã lưu biểu đồ: {cm_path}")
    
    return {
        'calibration': calib_results,
        'visitor_type_breakdown': vt_breakdown,
        'month_breakdown': month_breakdown
    }


def evaluate_all():
    print("=" * 60)
    print("BẮT ĐẦU QUY TRÌNH ĐÁNH GIÁ TRUNG THỰC VÀ THỰC HIỆN 4 THÍ NGHIỆM")
    print("=" * 60)
    
    test_file = os.path.join(MODELS_DIR, "test_dataset_frozen.csv")
    if not os.path.exists(test_file):
        raise FileNotFoundError("Chưa tìm thấy tập test đóng băng! Hãy chạy src/train.py trước.")
        
    test_df = pd.read_csv(test_file)
    y_test = test_df['Revenue'].astype(int)
    X_test = test_df.drop(columns=['Revenue'])
    
    models_dict = {
        'baseline_dummy': joblib.load(os.path.join(MODELS_DIR, "dummy_model.joblib")),
        'baseline_lr': joblib.load(os.path.join(MODELS_DIR, "pipeline_baseline_lr.joblib")),
        'naive_lr': joblib.load(os.path.join(MODELS_DIR, "pipeline_naive_lr.joblib")),
        'naive_rf': joblib.load(os.path.join(MODELS_DIR, "pipeline_naive_rf.joblib")),
        'honest_lr': joblib.load(os.path.join(MODELS_DIR, "pipeline_honest_lr.joblib")),
        'honest_rf': joblib.load(os.path.join(MODELS_DIR, "pipeline_honest_rf.joblib")),
        'honest_gb': joblib.load(os.path.join(MODELS_DIR, "pipeline_honest_gb.joblib")),
    }
    
    df_raw = load_raw_data()
    df_clean, _ = audit_data_quality(df_raw, drop_duplicates=True)
    
    exp1_out = run_experiment_1_seed_stability(df_clean)
    exp2_out = run_experiment_2_leakage_audit(models_dict, X_test, y_test)
    exp3_out = run_experiment_3_pr_vs_roc_curves(models_dict, X_test, y_test)
    exp4_out = run_experiment_4_calibration_and_error_breakdown(models_dict, X_test, y_test, test_df)
    
    all_results = {
        'experiment_1_seed_stability': exp1_out,
        'experiment_2_leakage_audit': exp2_out,
        'experiment_3_pr_vs_roc': exp3_out,
        'experiment_4_calibration_errors': exp4_out
    }
    
    results_path = os.path.join(MODELS_DIR, "experiment_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 60)
    print(f"HOÀN TẤT ĐÁNH GIÁ! Toàn bộ số liệu và đồ thị đã được lưu tại:")
    print(f" -> Số liệu JSON: {results_path}")
    print(f" -> Hình ảnh báo cáo: {FIGURES_DIR}")
    print("=" * 60)
    return all_results


if __name__ == "__main__":
    evaluate_all()
