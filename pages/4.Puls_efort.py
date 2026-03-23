import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from app_utils.data import load_csv, filter_df
from app_utils.db import load_storm, save_storm
from app_utils.kpis import apply_storm

st.title("❤️ Puls & efort")

df_all = load_csv("data/fitness_data.csv")
users = sorted(df_all["user"].unique())

user = st.selectbox("User", users)
min_d = df_all["date"].min().date()
max_d = df_all["date"].max().date()
start, end = st.date_input("Interval", (min_d, max_d))

storm_on = st.toggle("Storm ON/OFF (persistă)", value=load_storm(user))
save_storm(user, storm_on)

hr_thresh = st.slider("Prag max HR (alertă)", 120, 195, 170, 1)

df = filter_df(df_all, user, start, end)
df = apply_storm(df, storm_on)

alerts = df[df["max_hr"] > hr_thresh][["date","avg_hr","max_hr","workout_type"]].sort_values("date")

st.subheader("Tabel (alertă max_hr)")
st.dataframe(alerts, use_container_width=True)

st.subheader("1) Puls mediu în timp")
fig = plt.figure()
plt.plot(df["date"], df["avg_hr"])
plt.xticks(rotation=45); plt.tight_layout()
st.pyplot(fig)

st.subheader("2) Puls maxim în timp")
fig = plt.figure()
plt.plot(df["date"], df["max_hr"])
plt.xticks(rotation=45); plt.tight_layout()
st.pyplot(fig)

st.subheader("3) Max HR vs minute active")
fig = plt.figure()
sns.scatterplot(data=df, x="active_min", y="max_hr", hue="workout_type")
plt.tight_layout()
st.pyplot(fig)
