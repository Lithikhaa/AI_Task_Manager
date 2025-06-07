# main.py
import streamlit as st

# ✅ FIRST streamlit command
st.set_page_config(
    page_title="🤖 Advanced AI Task Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Only now import others
from utils import initialize_session_defaults
initialize_session_defaults()

from agent import AdvancedTaskAgent
from database import *
from ui_components import *
from analytics import create_advanced_dashboard
from email_reminder import handle_email_reminder
from datetime import datetime

def main():
    st.title(":robot_face: Advanced AI Task Manager")
    st.markdown("*Intelligent task management powered by AI*")

    initialize_session_defaults()

    agent = AdvancedTaskAgent()

    # Ensure database connection is alive before navigation
    from database import get_all_tasks
    _ = get_all_tasks()  # Force initial DB read to warm up cache/connection

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page:", [
        "📝 Add Task", "📋 All Tasks", "✅ Completed", "⏰ Overdue", "📊 Analytics"])

    if page == "📝 Add Task":
        show_add_task_page(agent)
    elif page == "📋 All Tasks":
        show_all_tasks_page(agent)
    elif page == "✅ Completed":
        show_completed_tasks_page()
    elif page == "⏰ Overdue":
        show_overdue_tasks_page()
    elif page == "📊 Analytics":
        create_advanced_dashboard()

    st.sidebar.markdown("---")
    st.sidebar.markdown("*Powered by NLP & ML intelligence*")

if __name__ == "__main__":
    main()
