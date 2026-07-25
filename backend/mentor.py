import pandas as pd
import os

# =====================================================
# LOAD DATA
# =====================================================
def load_data():

    base_dir = os.path.dirname(os.path.abspath(__file__))

    student_path = os.path.join(base_dir, "..", "data", "students.csv")
    mentor_path = os.path.join(base_dir, "..", "data", "mentors.csv")

    students = pd.read_csv(student_path)
    mentors = pd.read_csv(mentor_path)

    print("✅ Data Loaded Successfully")

    return students, mentors


# =====================================================
# FAIR USAGE TRACKING
# =====================================================
mentor_usage = {}


# =====================================================
# SMART SCORING ENGINE (UPGRADED)
# =====================================================
def calculate_score(student, mentor):

    score = 0

    stress = student["stress_level"]
    productivity = student["productivity_score"]
    engagement = student["engagement_score"]
    wellbeing = student["mental_wellbeing"]

    mentor_type = mentor["mentor_type"]
    expertise = mentor["expertise"]

    # =========================
    # WELLNESS MATCHING
    # =========================
    if stress >= 7 or wellbeing <= 4:
        if "Wellness" in mentor_type:
            score += 6

    # =========================
    # ACADEMIC SUPPORT
    # =========================
    if productivity < 60:
        if "Academic" in mentor_type:
            score += 5

    # =========================
    # CAREER SUPPORT
    # =========================
    if engagement < 60:
        if "Career" in mentor_type:
            score += 5

    # =========================
    # EXTRA INTELLIGENCE BOOST
    # =========================
    if stress >= 8 and "Wellness" in mentor_type:
        score += 2

    if productivity >= 80 and "Career" in mentor_type:
        score += 1

    # =========================
    # AVAILABILITY FACTOR
    # =========================
    score += mentor["availability_hours"] * 0.5

    # =========================
    # FAIRNESS PENALTY (IMPORTANT)
    # =========================
    used = mentor_usage.get(mentor["mentor_name"], 0)
    score -= used * 1.5

    return score


# =====================================================
# MENTOR MATCHING ENGINE
# =====================================================
def match_mentor(student, mentors_df):

    df = mentors_df.copy()

    df = df.dropna()

    # compute score
    df["score"] = df.apply(lambda m: calculate_score(student, m), axis=1)

    # sort best first
    df = df.sort_values(by="score", ascending=False)

    best = df.iloc[0]

    name = best["mentor_name"]

    # update fairness usage
    mentor_usage[name] = mentor_usage.get(name, 0) + 1

    return {
        "mentor_name": best["mentor_name"],
        "mentor_type": best["mentor_type"],
        "expertise": best["expertise"],
        "score": float(best["score"])
    }


# =====================================================
# APPLY TO ALL STUDENTS
# =====================================================
def apply_matching(students, mentors):

    results = []

    print("\n🚀 Running SMART Mentor Matching...\n")

    for _, student in students.iterrows():

        match = match_mentor(student, mentors)

        results.append(match)

    students["Assigned_Mentor"] = [r["mentor_name"] for r in results]
    students["Mentor_Type"] = [r["mentor_type"] for r in results]
    students["Mentor_Expertise"] = [r["expertise"] for r in results]

    print("✅ Matching Completed Successfully\n")

    print(students[["student_id", "Assigned_Mentor", "Mentor_Type"]].head())

    return students


# =====================================================
# SAVE OUTPUT
# =====================================================
def save_output(df):

    base_dir = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_dir, "..", "data", "final_with_mentors.csv")

    df.to_csv(path, index=False)

    print("\n💾 Saved at:", path)


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":

    print("\n🤖 AI Mentor System Started\n")

    students, mentors = load_data()

    students = apply_matching(students, mentors)

    save_output(students)

    print("\n🎯 System Completed Successfully\n")