import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from app_utils.data import load_csv, filter_df
from app_utils.db import load_storm, save_storm
from app_utils.kpis import apply_storm

st.title("🍽️ Alimentație")

df_all = load_csv("data/fitness_data.csv")
users = sorted(df_all["user"].unique())

user = st.selectbox("User", users)
min_d = df_all["date"].min().date()
max_d = df_all["date"].max().date()
start, end = st.date_input("Interval", (min_d, max_d))

storm_on = st.toggle("Storm ON/OFF (persistă)", value=load_storm(user))
save_storm(user, storm_on)

extra_meal = st.slider("Simulare: + calorii (masă extra)", 0, 1200, 0, 50)

df = filter_df(df_all, user, start, end)
df = apply_storm(df, storm_on)

df["cal_in_sim"] = df["calories_in"] + extra_meal
df["balance"] = df["cal_in_sim"] - df["calories_out"]

st.subheader("Tabel")
st.dataframe(df[["date","calories_in","cal_in_sim","calories_out","balance"]].sort_values("date"), use_container_width=True)

st.subheader("1) IN vs OUT")
fig = plt.figure()
plt.plot(df["date"], df["cal_in_sim"], label="IN (sim)")
plt.plot(df["date"], df["calories_out"], label="OUT")
plt.xticks(rotation=45); plt.legend(); plt.tight_layout()
st.pyplot(fig)

st.subheader("2) Balanță calorică")
fig = plt.figure()
plt.bar(df["date"], df["balance"])
plt.xticks(rotation=45); plt.tight_layout()
st.pyplot(fig)

st.subheader("3) Distribuție calorii IN (sim)")
fig = plt.figure()
sns.histplot(df["cal_in_sim"], bins=12, kde=True)
plt.tight_layout()
st.pyplot(fig)
