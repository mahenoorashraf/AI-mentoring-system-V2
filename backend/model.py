# =====================================================
# AI MENTOR - FINAL CLEAN PRODUCTION MODEL
# =====================================================

import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from imblearn.over_sampling import SMOTE


# =====================================================
# OUTPUT DIRECTORY
# =====================================================

def get_output_dir():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


# =====================================================
# LOAD DATA
# =====================================================

def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "..", "data", "final_output.csv")

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    print("\n🚀 AI Mentor Model Training Started")
    print(df.shape)

    return df


# =====================================================
# PREPROCESSING
# =====================================================

def preprocess(df):

    df = df.drop_duplicates()
    df = df.dropna()

    if df["Category"].dtype == "object":
        le = LabelEncoder()
        df["Category"] = le.fit_transform(df["Category"])

    print("✅ Preprocessing Done")

    return df


# =====================================================
# FEATURE SELECTION (NO LEAKAGE)
# =====================================================

def split_data(df):

    y = df["Category"]
    X = df.drop(columns=["Category"])

    drop_cols = [
        "student_id",
        "name",
        "Cluster",
        "APS",
        "WWS",
        "PTMS",
        "CRS",
        "SRI"
    ]

    for col in drop_cols:
        if col in X.columns:
            X = X.drop(columns=[col])

    X = X.select_dtypes(include=["int64", "float64"])

    return X, y


# =====================================================
# MODEL TRAINING
# =====================================================

def train_model(X_train, y_train):

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)

    print("🔥 Model Training Completed")

    return model


# =====================================================
# CHARTS (FULL FIXED)
# =====================================================

def generate_charts(df, X, model, output_dir):

    sns.set_theme(style="whitegrid")

    # =====================
    # PIE CHART
    # =====================
    plt.figure(figsize=(6,6))

    df["Category"].value_counts().plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90,
        colors=["#ff9999", "#66b3ff", "#99ff99"]
    )

    plt.title("Student Category Distribution")
    plt.savefig(os.path.join(output_dir, "category_pie.png"))
    plt.close()


    # =====================
    # SAFE HEATMAP
    # =====================
    numeric_df = df.select_dtypes(include=["int64", "float64"])

    if numeric_df.shape[1] > 1:

        plt.figure(figsize=(10,6))

        sns.heatmap(numeric_df.corr(), cmap="coolwarm", annot=False)

        plt.title("Feature Correlation Heatmap")
        plt.savefig(os.path.join(output_dir, "heatmap.png"))
        plt.close()


    # =====================
    # FEATURE IMPORTANCE (FIXED WARNING)
    # =====================
    plt.figure(figsize=(8,5))

    importance = model.feature_importances_

    feat_df = pd.DataFrame({
        "feature": X.columns,
        "importance": importance
    }).sort_values(by="importance", ascending=True)

    sns.barplot(
        data=feat_df,
        x="importance",
        y="feature"
    )

    plt.title("Feature Importance")
    plt.savefig(os.path.join(output_dir, "feature_importance.png"))
    plt.close()


    # =====================
    # CONFUSION MATRIX
    # =====================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_global,
        test_size=0.2,
        stratify=y_global,
        random_state=42
    )

    y_pred = model.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")

    plt.title("Confusion Matrix")
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"))
    plt.close()


# =====================================================
# GLOBAL VARIABLE FIX (IMPORTANT)
# =====================================================

y_global = None


# =====================================================
# MAIN PIPELINE
# =====================================================

def main():

    global y_global

    output_dir = get_output_dir()

    df = load_data()
    df = preprocess(df)

    X, y = split_data(df)

    y_global = y

    print("\n📌 Features Used:", list(X.columns))

    # =====================
    # SCALING (FIXED - NO WARNING)
    # =====================
    scaler = StandardScaler()

    X_scaled = pd.DataFrame(
        scaler.fit_transform(X),
        columns=X.columns
    )

    # =====================
    # TRAIN TEST SPLIT
    # =====================
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print("\n📊 Before SMOTE:")
    print(y_train.value_counts())

    # =====================
    # SMOTE (FIXED)
    # =====================
    smote = SMOTE(
        random_state=42,
        k_neighbors=2
    )

    X_train_res, y_train_res = smote.fit_resample(
        pd.DataFrame(X_train, columns=X.columns),
        y_train
    )

    print("\n📊 After SMOTE:")
    print(pd.Series(y_train_res).value_counts())

    # =====================
    # MODEL TRAINING
    # =====================
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train_res, y_train_res)

    print("🔥 Model Training Completed")

    # =====================
    # EVALUATION
    # =====================
    y_pred = model.predict(X_test)

    print("\n📊 Accuracy:", accuracy_score(y_test, y_pred))

    print("\n📊 Classification Report:\n")
    print(classification_report(y_test, y_pred))

    # =====================
    # CHARTS
    # =====================
    generate_charts(df, X, model, output_dir)

    print("\n📊 All charts saved in 'outputs' folder")
    print("\n🎯 Training Completed Successfully")


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    main()