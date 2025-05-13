import streamlit as st
import pandas as pd
from datetime import datetime, date
import altair as alt

# Load or create study log
def load_data():
    try:
        return pd.read_csv("study_log.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Subject", "Topic", "Duration"])

# Save study log
def save_data(df):
    df.to_csv("study_log.csv", index=False)

# Add new entry
def add_entry(subject, topic, duration):
    df = load_data()
    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Subject": subject,
        "Topic": topic,
        "Duration": duration
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_data(df)

# Topic recommendation
def recommend_topic():
    df = load_data()
    if df.empty:
        return "No data yet. Start logging your study sessions!"
    topic_counts = df["Topic"].value_counts()
    least_studied = topic_counts.idxmin()
    return f"📌 You should revise: **{least_studied}** (studied least)"

# --- Streamlit UI ---
st.set_page_config(page_title="AI Study Assistant", layout="wide")
st.title("📚 AI-Based Personal Study Assistant")

# Tab navigation
tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Study", "📊 Analytics", "🎯 Recommendation", "⬇️ Export"])

# --- Tab 1: Study Logger ---
with tab1:
    st.subheader("Log Your Study Session")
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")
    duration = st.slider("Duration (minutes)", 10, 180, 30)
    goal = st.number_input("🎯 Daily Study Goal (in minutes)", min_value=10, max_value=600, value=120)

    if st.button("✅ Save Study Log"):
        if subject and topic:
            add_entry(subject, topic, duration)
            st.success("✅ Study session saved!")
        else:
            st.warning("Please fill all fields.")

    # Show daily goal progress
    df = load_data()
    today = date.today().strftime("%Y-%m-%d")
    today_data = df[df["Date"] == today]
    today_total = today_data["Duration"].astype(int).sum()

    st.progress(min(today_total / goal, 1.0))
    st.write(f"🕒 Studied today: {today_total} / {goal} minutes")

# --- Tab 2: Analytics ---
with tab2:
    st.subheader("📊 Study Analytics")
    df = load_data()
    if df.empty:
        st.info("No study data available.")
    else:
        # Subject-wise total
        df["Duration"] = df["Duration"].astype(int)
        subject_totals = df.groupby("Subject")["Duration"].sum().reset_index()

        st.markdown("**⏱️ Time Spent per Subject:**")
        st.dataframe(subject_totals)

        # Time trend
        df["Date"] = pd.to_datetime(df["Date"])
        daily_totals = df.groupby("Date")["Duration"].sum().reset_index()

        chart = alt.Chart(daily_totals).mark_bar().encode(
            x="Date:T",
            y="Duration:Q"
        ).properties(title="📅 Study Time per Day")

        st.altair_chart(chart, use_container_width=True)

# --- Tab 3: Recommendation ---
with tab3:
    st.subheader("🎯 What to Study Next?")
    suggestion = recommend_topic()
    st.markdown(suggestion)

# --- Tab 4: Export ---
with tab4:
    st.subheader("⬇️ Download Study Log")
    df = load_data()
    if not df.empty:
        st.download_button("Download as CSV", df.to_csv(index=False), "study_log.csv", "text/csv")
    else:
        st.info("No data to export.")