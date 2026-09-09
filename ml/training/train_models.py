import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.preprocessing.pipeline import (
    PreprocessingPipeline,
    split_dataset,
    RAINFALL_FEATURES,
    FLOOD_FEATURES
)

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

def train_and_evaluate():
    data_path = os.path.join(BASE_DIR, "ml", "datasets", "disaster_training_data.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found at {data_path}. Run generate_dataset.py first.")
        
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Dataset loaded with {len(df)} records and {len(df.columns)} columns.")
    
    models_dir = os.path.join(BASE_DIR, "ml", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    metrics_summary = {
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_samples": len(df),
        "data_provenance": "Physically-Modeled Synthetic Meteorological & Hydrological Prototype",
        "models": {}
    }
    
    # --------------------------------------------------------------------------
    # 1. RAINFALL MODELS (Classifier & Continuous Regressor)
    # --------------------------------------------------------------------------
    print("\n" + "="*70)
    print("STAGE 1: TRAINING HEAVY RAINFALL PREDICTION MODELS")
    print("="*70)
    
    rain_preprocessor = PreprocessingPipeline(RAINFALL_FEATURES, name="rainfall_preprocessor")
    clean_df = rain_preprocessor.clean_raw_dataframe(df)
    
    X_rain = clean_df[RAINFALL_FEATURES]
    y_rain_cat = clean_df["rainfall_category"]
    y_rain_num = clean_df["predicted_rainfall_6h_mm"]
    
    # Stratified Split for Classification
    X_tr_c, X_te_c, y_tr_c, y_te_c = split_dataset(X_rain, y_rain_cat, test_size=0.2, random_state=42, stratify=y_rain_cat)
    # Matching Split for Regression
    X_tr_r, X_te_r, y_tr_r, y_te_r = split_dataset(X_rain, y_rain_num, test_size=0.2, random_state=42)
    
    # Fit & Save Preprocessor
    rain_preprocessor.fit(X_tr_c)
    rain_preprocessor_path = os.path.join(models_dir, "rainfall_preprocessor.joblib")
    rain_preprocessor.save(rain_preprocessor_path)
    
    X_tr_c_sc = rain_preprocessor.transform(X_tr_c)
    X_te_c_sc = rain_preprocessor.transform(X_te_c)
    X_tr_r_sc = rain_preprocessor.transform(X_tr_r)
    X_te_r_sc = rain_preprocessor.transform(X_te_r)
    
    # Model 1A: Baseline Logistic Regression
    print("Training Baseline: LogisticRegression...")
    log_reg = LogisticRegression(max_iter=1000, random_state=42)
    log_reg.fit(X_tr_c_sc, y_tr_c)
    y_pred_log = log_reg.predict(X_te_c_sc)
    acc_log = accuracy_score(y_te_c, y_pred_log)
    print(f"  -> LogisticRegression Test Accuracy: {acc_log:.4f}")
    
    # Model 1B: Primary RandomForestClassifier
    print("Training Primary: RandomForestClassifier...")
    rf_rain_clf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, class_weight="balanced")
    rf_rain_clf.fit(X_tr_c_sc, y_tr_c)
    y_pred_rf = rf_rain_clf.predict(X_te_c_sc)
    
    acc_rf = accuracy_score(y_te_c, y_pred_rf)
    prec_rf = precision_score(y_te_c, y_pred_rf, average="weighted", zero_division=0)
    rec_rf = recall_score(y_te_c, y_pred_rf, average="weighted", zero_division=0)
    f1_rf = f1_score(y_te_c, y_pred_rf, average="weighted", zero_division=0)
    cm_rf = confusion_matrix(y_te_c, y_pred_rf, labels=rf_rain_clf.classes_).tolist()
    
    print(f"  -> RandomForestClassifier Test Accuracy: {acc_rf:.4f}")
    print(f"  -> Precision (Weighted): {prec_rf:.4f} | Recall: {rec_rf:.4f} | F1: {f1_rf:.4f}")
    
    rain_clf_path = os.path.join(models_dir, "rainfall_classifier.joblib")
    joblib.dump(rf_rain_clf, rain_clf_path)
    print(f"Saved Rainfall Classifier to: {rain_clf_path}")
    
    # Model 1C: Rainfall Regressor (predicted mm)
    print("Training Continuous: RandomForestRegressor...")
    rf_rain_reg = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    rf_rain_reg.fit(X_tr_r_sc, y_tr_r)
    y_pred_reg = rf_rain_reg.predict(X_te_r_sc)
    
    mae_rain = mean_absolute_error(y_te_r, y_pred_reg)
    rmse_rain = np.sqrt(mean_squared_error(y_te_r, y_pred_reg))
    r2_rain = r2_score(y_te_r, y_pred_reg)
    
    print(f"  -> RandomForestRegressor MAE: {mae_rain:.2f} mm | RMSE: {rmse_rain:.2f} mm | R2: {r2_rain:.4f}")
    
    rain_reg_path = os.path.join(models_dir, "rainfall_regressor.joblib")
    joblib.dump(rf_rain_reg, rain_reg_path)
    print(f"Saved Rainfall Regressor to: {rain_reg_path}")
    
    metrics_summary["models"]["rainfall_classifier"] = {
        "model_type": "RandomForestClassifier",
        "classes": list(rf_rain_clf.classes_),
        "accuracy": round(acc_rf, 4),
        "precision_weighted": round(prec_rf, 4),
        "recall_weighted": round(rec_rf, 4),
        "f1_weighted": round(f1_rf, 4),
        "confusion_matrix": cm_rf,
        "baseline_comparison": {
            "model_type": "LogisticRegression",
            "accuracy": round(acc_log, 4)
        }
    }
    
    metrics_summary["models"]["rainfall_regressor"] = {
        "model_type": "RandomForestRegressor",
        "mae_mm": round(mae_rain, 2),
        "rmse_mm": round(rmse_rain, 2),
        "r2_score": round(r2_rain, 4)
    }

    # --------------------------------------------------------------------------
    # 2. FLOOD INUNDATION MODELS (Classifier & Water Depth Regressor)
    # --------------------------------------------------------------------------
    print("\n" + "="*70)
    print("STAGE 2: TRAINING FLOOD INUNDATION RISK MODELS")
    print("="*70)
    
    clean_df["rainfall_intensity_mm_h"] = clean_df["rainfall_1h"]
    clean_df["cumulative_rainfall_24h"] = clean_df["rainfall_24h"]
    
    flood_preprocessor = PreprocessingPipeline(FLOOD_FEATURES, name="flood_preprocessor")
    X_flood = clean_df[FLOOD_FEATURES]
    y_flood_cat = clean_df["flood_risk_level"]
    y_flood_depth = clean_df["water_depth_m"]
    
    X_tr_fc, X_te_fc, y_tr_fc, y_te_fc = split_dataset(X_flood, y_flood_cat, test_size=0.2, random_state=42, stratify=y_flood_cat)
    X_tr_fd, X_te_fd, y_tr_fd, y_te_fd = split_dataset(X_flood, y_flood_depth, test_size=0.2, random_state=42)
    
    flood_preprocessor.fit(X_tr_fc)
    flood_preprocessor_path = os.path.join(models_dir, "flood_preprocessor.joblib")
    flood_preprocessor.save(flood_preprocessor_path)
    
    X_tr_fc_sc = flood_preprocessor.transform(X_tr_fc)
    X_te_fc_sc = flood_preprocessor.transform(X_te_fc)
    X_tr_fd_sc = flood_preprocessor.transform(X_tr_fd)
    X_te_fd_sc = flood_preprocessor.transform(X_te_fd)
    
    # Model 2A: Comparison Baseline Gradient Boosting
    print("Training Comparison: GradientBoostingClassifier...")
    gb_flood = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    gb_flood.fit(X_tr_fc_sc, y_tr_fc)
    y_pred_gb = gb_flood.predict(X_te_fc_sc)
    acc_gb = accuracy_score(y_te_fc, y_pred_gb)
    print(f"  -> GradientBoostingClassifier Test Accuracy: {acc_gb:.4f}")
    
    # Model 2B: Primary RandomForestClassifier for Flood Risk
    print("Training Primary: RandomForestClassifier for Flood Risk...")
    rf_flood_clf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, class_weight="balanced")
    rf_flood_clf.fit(X_tr_fc_sc, y_tr_fc)
    y_pred_f_rf = rf_flood_clf.predict(X_te_fc_sc)
    
    acc_f_rf = accuracy_score(y_te_fc, y_pred_f_rf)
    prec_f_rf = precision_score(y_te_fc, y_pred_f_rf, average="weighted", zero_division=0)
    rec_f_rf = recall_score(y_te_fc, y_pred_f_rf, average="weighted", zero_division=0)
    f1_f_rf = f1_score(y_te_fc, y_pred_f_rf, average="weighted", zero_division=0)
    cm_f_rf = confusion_matrix(y_te_fc, y_pred_f_rf, labels=rf_flood_clf.classes_).tolist()
    
    print(f"  -> RandomForestClassifier Test Accuracy: {acc_f_rf:.4f}")
    print(f"  -> Precision (Weighted): {prec_f_rf:.4f} | Recall: {rec_f_rf:.4f} | F1: {f1_f_rf:.4f}")
    
    flood_clf_path = os.path.join(models_dir, "flood_classifier.joblib")
    joblib.dump(rf_flood_clf, flood_clf_path)
    print(f"Saved Flood Classifier to: {flood_clf_path}")
    
    # Model 2C: Inundation Depth Regressor
    print("Training Inundation Depth: RandomForestRegressor...")
    rf_flood_reg = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_flood_reg.fit(X_tr_fd_sc, y_tr_fd)
    y_pred_fd = rf_flood_reg.predict(X_te_fd_sc)
    
    mae_flood = mean_absolute_error(y_te_fd, y_pred_fd)
    rmse_flood = np.sqrt(mean_squared_error(y_te_fd, y_pred_fd))
    r2_flood = r2_score(y_te_fd, y_pred_fd)
    
    print(f"  -> Inundation Depth MAE: {mae_flood:.2f} m | RMSE: {rmse_flood:.2f} m | R2: {r2_flood:.4f}")
    
    flood_depth_path = os.path.join(models_dir, "flood_depth_regressor.joblib")
    joblib.dump(rf_flood_reg, flood_depth_path)
    print(f"Saved Flood Depth Regressor to: {flood_depth_path}")
    
    metrics_summary["models"]["flood_classifier"] = {
        "model_type": "RandomForestClassifier",
        "classes": list(rf_flood_clf.classes_),
        "accuracy": round(acc_f_rf, 4),
        "precision_weighted": round(prec_f_rf, 4),
        "recall_weighted": round(rec_f_rf, 4),
        "f1_weighted": round(f1_f_rf, 4),
        "confusion_matrix": cm_f_rf,
        "baseline_comparison": {
            "model_type": "GradientBoostingClassifier",
            "accuracy": round(acc_gb, 4)
        }
    }
    
    metrics_summary["models"]["flood_depth_regressor"] = {
        "model_type": "RandomForestRegressor",
        "mae_meters": round(mae_flood, 2),
        "rmse_meters": round(rmse_flood, 2),
        "r2_score": round(r2_flood, 4)
    }
    
    # Save Metrics File
    metrics_file = os.path.join(models_dir, "model_metrics.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"\nSaved Comprehensive Model Metrics to: {metrics_file}")
    print("\nTraining & Serialization Completed Successfully!")

if __name__ == "__main__":
    train_and_evaluate()
