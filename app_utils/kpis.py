import numpy as np

def apply_storm(df, storm_on: bool, steps_mult=0.8, hr_add=8):
    if not storm_on or df.empty:
        return df
    df = df.copy()
    df["steps"] = (df["steps"] * steps_mult).round().astype(int)
    df["avg_hr"] = (df["avg_hr"] + hr_add).round().astype(int)
    df["max_hr"] = (df["max_hr"] + hr_add).round().astype(int)
    return df

def compute_kpis(df):
    if df.empty:
        return {"cal_total": 0, "steps_avg": 0, "hr_avg": 0, "active_total": 0}

    return {
        "cal_total": int(df["calories_in"].sum()),
        "steps_avg": int(df["steps"].mean()),
        "hr_avg": int(df["avg_hr"].mean()),
        "active_total": int(df["active_min"].sum())
    }

def health_index(df, steps_target=10000, sleep_target=7.5, hr_max_target=85):
    if df.empty:
        return 0

    steps_score = np.clip((df["steps"].mean() / steps_target) * 100, 0, 100)
    sleep_score = np.clip((df["sleep_hours"].mean() / sleep_target) * 100, 0, 100)

    hr_mean = df["avg_hr"].mean()
    hr_score = np.clip(100 - max(0, hr_mean - hr_max_target) * 2, 0, 100)

    activity_score = np.clip((df["active_min"].mean() / 60) * 100, 0, 100)

    score = 0.35*steps_score + 0.25*sleep_score + 0.20*activity_score + 0.20*hr_score
    return int(round(score))
0