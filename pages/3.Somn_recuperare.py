import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from app_utils.data import load_csv, filter_df
from app_utils.db import load_storm, save_storm
from app_utils.kpis import apply_storm

st.title("😴 Somn & recuperare")

df_all = load_csv("data/fitness_data.csv")
users = sorted(df_all["user"].unique())

user = st.selectbox("User", users)
min_d = df_all["date"].min().date()
max_d = df_all["date"].max().date()
start, end = st.date_input("Interval", (min_d, max_d))

storm_on = st.toggle("Storm ON/OFF (persistă)", value=load_storm(user))
save_storm(user, storm_on)

q_min = st.slider("Prag minim calitate somn", 35, 100, 70, 1)

df = filter_df(df_all, user, start, end)
df = apply_storm(df, storm_on)

bad = df[df["sleep_quality"] < q_min][["date","sleep_hours","sleep_quality","avg_hr"]].sort_values("date")

st.subheader("Tabel (zile sub prag)")
st.dataframe(bad, use_container_width=True)

st.subheader("1) Ore somn")
fig = plt.figure()
plt.plot(df["date"], df["sleep_hours"])
plt.xticks(rotation=45); plt.tight_layout()
st.pyplot(fig)

st.subheader("2) Calitate somn")
fig = plt.figure()
plt.bar(df["date"], df["sleep_quality"])
plt.xticks(rotation=45); plt.tight_layout()
st.pyplot(fig)

st.subheader("3) Somn vs puls mediu")
fig = plt.figure()
sns.scatterplot(data=df, x="sleep_hours", y="avg_hr")
plt.tight_layout()
st.pyplot(fig)
