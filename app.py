import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from app_utils.data import load_csv, filter_df
from app_utils.db import init_db, load_settings, save_settings, load_storm, save_storm
from app_utils.kpis import apply_storm, compute_kpis, health_index

st.set_page_config(page_title="Fitness & Health Tracker", layout="wide")
init_db()                               # Initializeaza baza de date SQLite

df_all = load_csv("data/fitness_data.csv")   # citește fișierul CSV într-un DataFrame
users = sorted(df_all["user"].unique().tolist())   # Extrage utilizatorii existenti

st.sidebar.title("Filtre & Setări")   # pune titlul in sidebar
user = st.sidebar.selectbox("User", users)  # permite alegera utilizatorului

min_date = df_all["date"].min().date()
max_date = df_all["date"].max().date()
start, end = st.sidebar.date_input("Interval", (min_date, max_date))

# Setari persistente (SQLite)
settings = load_settings(user)
storm_default = load_storm(user)

storm_on = st.sidebar.toggle("Storm ON/OFF (persistă)", value=storm_default)
save_storm(user, storm_on) # salveaza alegerea in DB -> persista la urmatoarea rulare

steps_target = st.sidebar.slider("Țintă pași/zi (persistă)", 3000, 20000, int(settings["steps_target"]), 500)
sleep_target = st.sidebar.slider("Țintă somn (ore) (persistă)", 5.0, 10.0, float(settings["sleep_target"]), 0.5)
hr_max_target = st.sidebar.slider("Țintă puls mediu max (persistă)", 60, 120, int(settings["hr_max_target"]), 1)
save_settings(user, steps_target, sleep_target, hr_max_target)

df = filter_df(df_all, user, start, end)
df = apply_storm(df, storm_on)

# KPI -uri
k = compute_kpis(df)         # intoarce un dictionar cu indicatori agregati(calorii, pasi)
hi = health_index(df, steps_target, sleep_target, hr_max_target)
def hi_badge(hi: int):             #  Health Index cu culoare + mesaj (verde/galben/roșu)
    if hi >= 80:
        return "✅ Excelent", "green"
    elif hi >= 60:
        return "⚠️ OK", "orange"
    return "🛑 Atenție", "red"

hi_label, hi_color = hi_badge(hi)

st.title("💪 Fitness & Health Tracker — Overview")
st.caption(
    "Dashboard interactiv cu filtrare per user, simulare Storm și persistență setări în SQLite."
)

c1, c2, c3, c4, c5 = st.columns(5, gap="large")                  #  KPI-uri formatate frumos (cu separatori)
c1.metric("Calorii totale", f"{k['cal_total']:,}".replace(",", " "))
c2.metric("Pași medii", f"{k['steps_avg']:,}".replace(",", " "))
c3.metric("Puls mediu", f"{k['hr_avg']}")
c4.metric("Timp activ (min)", f"{k['active_total']:,}".replace(",", " "))
c5.metric("Health Index", f"{hi}/100", help=hi_label)           # adauga  feedback vizual,afișeaza  Health Index în KPI-uri.



st.markdown("### 🧠 Status sănătate")

st.markdown(
    f"<span style='color:{hi_color}; font-weight:700; font-size:18px;'>{hi_label}</span>",
    unsafe_allow_html=True
)


st.divider()

colA, colB = st.columns(2)

with colA:
    with st.container(border=True):
        st.subheader("Pași în timp")      #Graficul devine „profesionist” și mai ușor de interpretat.
        df_plot = df.sort_values("date").copy()         #sortare după dată
        df_plot["steps_ma7"] = df_plot["steps"].rolling(7, min_periods=1).mean()  #media mobilă pe 7 zile

        fig = plt.figure()
        plt.plot(df_plot["date"], df_plot["steps"], alpha=0.35, label="Pași (zilnic)")
        plt.plot(df_plot["date"], df_plot["steps_ma7"], linewidth=2.5, label="Medie mobilă 7 zile")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        st.pyplot(fig)



with colB:
    with st.container(border=True):
        st.subheader("Distribuție puls mediu")
        fig = plt.figure()
        sns.histplot(df["avg_hr"], bins=12, kde=True)  # histograma
        plt.tight_layout()
        st.pyplot(fig)


st.markdown("## 📌 Rezumat rapid")
st.caption("Cele mai importante repere din intervalul selectat")

if df.empty:
    st.info("Nu există date pentru filtrele selectate.")
else:
    df_s = df.sort_values("date").copy()

    best_steps = df_s.loc[df_s["steps"].idxmax()]
    worst_steps = df_s.loc[df_s["steps"].idxmin()]

    best_sleep = df_s.loc[df_s["sleep_quality"].idxmax()]
    worst_sleep = df_s.loc[df_s["sleep_quality"].idxmin()]

    cA, cB, cC, cD = st.columns(4)

    cA.metric("🏆 Ziua cu MAX pași", f"{int(best_steps['steps']):,}".replace(",", " "))
    cA.caption(f"{best_steps['date'].date()} • {best_steps['workout_type']}")

    cB.metric("🧊 Ziua cu MIN pași", f"{int(worst_steps['steps']):,}".replace(",", " "))
    cB.caption(f"{worst_steps['date'].date()} • {worst_steps['workout_type']}")

    cC.metric("😴 Cea mai bună calitate somn", f"{int(best_sleep['sleep_quality'])}/100")
    cC.caption(f"{best_sleep['date'].date()} • {best_sleep['sleep_hours']} ore")

    cD.metric("⚠️ Cea mai slabă calitate somn", f"{int(worst_sleep['sleep_quality'])}/100")
    cD.caption(f"{worst_sleep['date'].date()} • {worst_sleep['sleep_hours']} ore")

high_hr_days = (df["max_hr"] >= 170).sum()       #alertă puls mare
if high_hr_days > 0:
    st.warning(f"Au fost detectate {high_hr_days} zile cu max_hr ≥ 170 (efort ridicat).")


st.dataframe(df.sort_values("date", ascending=False).head(30), width="stretch")