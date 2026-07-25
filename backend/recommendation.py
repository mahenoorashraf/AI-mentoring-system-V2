# recommendation.py
# -----------------------------------
# AI Recommendation Engine
# -----------------------------------

import pandas as pd
import os

# -------------------------------
# Load Data
# -------------------------------
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", "final_with_mentors.csv")

    df = pd.read_csv(file_path)
    print("✅ Data Loaded for Recommendations")
    return df


# -------------------------------
# Smart Recommendation Logic
# -------------------------------
def generate_recommendation(row):

    recs = []

    # 🎯 Category-based recommendations
    if row['Category'] == "Red":
        recs.append("Urgent mentoring required")
        recs.append("Weekly mentor sessions recommended")

    elif row['Category'] == "Yellow":
        recs.append("Regular improvement plan needed")

    elif row['Category'] == "Blue":
        recs.append("Focus on advanced skills")

    else:
        recs.append("Maintain excellent performance")

    # 🎯 Score-based insights
    if row['APS'] < 6:
        recs.append("Improve academic performance")

    if row['WWS'] < 5:
        recs.append("Focus on mental wellness & sleep")

    if row['PTMS'] < 5:
        recs.append("Improve productivity & reduce distractions")

    if row['CRS'] < 5:
        recs.append("Work on career planning & skills")

    # 🎯 Mentor-based suggestion
    recs.append(f"Assigned Mentor: {row['Assigned_Mentor']} ({row['Mentor_Expertise']})")

    return " | ".join(recs)


# -------------------------------
# Apply Recommendations
# -------------------------------
def apply_recommendations(df):
    df['Final_Recommendation'] = df.apply(generate_recommendation, axis=1)

    print("\n✅ Recommendations Generated")
    print(df[['student_id','Final_Recommendation']].head())

    return df


# -------------------------------
# Save Output
# -------------------------------
def save_output(df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, "..", "data", "final_recommendations.csv")

    df.to_csv(save_path, index=False)
    print("\n💾 Final recommendations file saved")


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    df = load_data()
    df = apply_recommendations(df)
    save_output(df)