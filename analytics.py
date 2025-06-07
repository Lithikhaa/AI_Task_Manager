# analytics.py
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from database import get_tasks_analytics, get_smart_recommendations, get_all_tasks


def create_advanced_dashboard():
    st.header("📊 Task Analytics Dashboard")
    analytics = get_tasks_analytics()
    recommendations = get_smart_recommendations()
    all_tasks_df = get_all_tasks()

    if all_tasks_df.empty:
        st.info("No tasks available to analyze.")
        return

    if recommendations:
        st.subheader("🎯 Smart Recommendations")
        for rec in recommendations:
            st.info(rec)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", analytics.get("total_tasks", 0))
    col2.metric("Completed", analytics.get("completed_tasks", 0))
    col3.metric("Pending", analytics.get("pending_tasks", 0))
    col4.metric("Overdue", analytics.get("overdue_tasks", 0))

    st.subheader("📁 Category Distribution")
    cat_counts = all_tasks_df['category'].value_counts()
    fig_cat = px.pie(values=cat_counts.values, names=cat_counts.index, title="Tasks by Category")
    st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("🎯 Priority Distribution")
    prio_counts = all_tasks_df['priority'].value_counts()
    fig_prio = px.bar(
        x=prio_counts.index,
        y=prio_counts.values,
        title="Tasks by Priority",
        color=prio_counts.index,
        color_discrete_map={"high": "red", "medium": "orange", "low": "green"}
    )
    st.plotly_chart(fig_prio, use_container_width=True)

    st.subheader("⏰ Time Estimation")
    col5, col6 = st.columns(2)
    col5.metric("Total Time (min)", analytics.get("total_estimated_time", 0))
    avg_time = all_tasks_df['estimated_duration'].mean()
    col6.metric("Average per Task (min)", f"{avg_time:.1f}")

    st.subheader("📝 Task Word Cloud")
    text = " ".join(all_tasks_df['task_name'].astype(str))
    if text.strip():
        wc = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No text available to generate word cloud.")
    recommendations = get_smart_recommendations()

    if recommendations:
        st.subheader("🎯 Smart Recommendations")
        for rec in recommendations:
            st.info(rec)
