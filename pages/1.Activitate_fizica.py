import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from app_utils.data import load_csv, filter_df
from app_utils.db import load_storm, save_storm
from app_utils.kpis import apply_storm

st.title("🏃 Activitate fizică")

df_all = load_csv("data/fitness_data.csv")
users = sorted(df_all["user"].unique())

user = st.selectbox("User", users)
min_d = df_all["date"].min().date()
max_d = df_all["date"].max().date()
start, end = st.date_input("Interval", (min_d, max_d))

storm_on = st.toggle("Storm ON/OFF (persistă)", value=load_storm(user))
save_storm(user, storm_on)    # salvează  alegerea în DB → persistă la următoarea rulare.

adjust = st.slider("Simulare: ajustare pași (%)", -50, 50, 0, 5)

df = filter_df(df_all, user, start, end)
df = apply_storm(df, storm_on)

df["steps_sim"] = (df["steps"] * (1 + adjust/100)).round().astype(int)

st.subheader("Tabel")
st.dataframe(df[["date","steps","steps_sim","distance_km","active_min","workout_type"]].sort_values("date"), use_container_width=True)

st.subheader("1) Pași (sim) în timp")
fig = plt.figure()
plt.plot(df["date"], df["steps_sim"])
plt.xticks(rotation=45); plt.tight_layout()
st.pyplot(fig)

st.subheader("2) Distanță (km) pe zile")
fig = plt.figure()
plt.bar(df["date"], df["distance_km"])
plt.xticks(rotation=45); plt.tight_layout()
st.pyplot(fig)

st.subheader("3) Pași vs timp activ")
fig = plt.figure()
sns.scatterplot(data=df, x="steps_sim", y="active_min", hue="workout_type")
plt.tight_layout()
st.pyplot(fig)
