# ui_components.py
import streamlit as st
from datetime import datetime
import json
from database import update_task, update_task_status, delete_task
import pandas as pd


def display_advanced_task_card(task):
    is_editing = st.session_state.get("edit_task_id") == task["task_id"]

    with st.container():
        if is_editing:
            with st.form(f"edit_form_{task['task_id']}"):
                new_name = st.text_input("Task Name", value=task['task_name'])
                new_category = st.text_input("Category", value=task['category'])
                new_priority = st.selectbox("Priority", ["high", "medium", "low"], index=["high", "medium", "low"].index(task['priority']))
                new_due_date = st.date_input("Due Date", datetime.strptime(task['due_date'], '%Y-%m-%d %H:%M:%S').date())
                new_due_time = st.time_input("Due Time", datetime.strptime(task['due_date'], '%Y-%m-%d %H:%M:%S').time())

                col1, col2 = st.columns(2)
                with col1:
                    prio_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
                    st.markdown(f"**{prio_icon} {task['task_name']}**")
                    st.caption(f"📁 {task['category']} • 📅 {task['due_date']}")
                    st.caption(f"⏱️ Est. {task['estimated_duration']} min • 🎯 {task['priority']}")

                    if task.get("ai_suggestions"):
                        try:
                            suggestions = json.loads(task["ai_suggestions"])
                            if suggestions:
                                with st.expander("🤖 Suggestions"):
                                    for s in suggestions:
                                        st.write("•", s)
                        except:
                            pass


                with col2:
                    if st.form_submit_button("💾 Save Changes"):
                        from database import update_task
                        new_due_datetime = datetime.combine(new_due_date, new_due_time)
                        if update_task(
                            task["task_id"],
                            new_name,
                            new_category,
                            new_priority,
                            new_due_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            task["tags"],
                            task["estimated_duration"],
                            task["ai_suggestions"],
                            task["context_keywords"]
                        ):
                            st.success("✅ Task updated")
                            st.session_state.edit_task_id = None
                            st.rerun()
                        else:
                            st.error("❌ Failed to update task")

                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.edit_task_id = None
                        st.rerun()

        else:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                prio_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
                st.markdown(f"**{prio_icon} {task['task_name']}**")
                st.caption(f"📁 {task['category']} • 📅 {task['due_date']}")
                st.caption(f"⏱️ Est. {task['estimated_duration']} min • 🎯 {task['priority']}")

                if task.get("ai_suggestions"):
                    try:
                        suggestions = json.loads(task["ai_suggestions"])
                        if suggestions:
                            with st.expander("🤖 Suggestions"):
                                for s in suggestions:
                                    st.write("•", s)
                    except:
                        pass

            with col2:
                if st.button("✅ Complete", key=f"complete_{task['task_id']}"):
                    if update_task_status(task['task_id'], 'completed'):
                        st.success("Marked complete")
                        st.rerun()
            with col3:
                if st.button("📝 Edit", key=f"edit_{task['task_id']}"):
                    st.session_state.edit_task_id = task['task_id']
                    st.rerun()
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{task['task_id']}"):
                    if delete_task(task['task_id']):
                        st.success("Task deleted")
                        st.rerun()


def show_completed_tasks_page():
    from database import get_completed_tasks
    st.header("✅ Completed Tasks")
    df = get_completed_tasks()
    if df.empty:
        st.info("No completed tasks yet.")
        return
    for _, task in df.iterrows():
        display_advanced_task_card(task)
        st.divider()


def show_overdue_tasks_page():
    from database import get_overdue_tasks
    st.header("⏰ Overdue Tasks")
    df = get_overdue_tasks()
    if df.empty:
        st.success("🎉 No overdue tasks!")
        return
    for _, task in df.iterrows():
        display_advanced_task_card(task)
        st.divider()


def show_all_tasks_page(agent):
    from database import get_all_tasks
    from datetime import datetime, timedelta

    st.header("📋 All Tasks")

    # 👉 Horizontal filters like in uimai.py
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority", ["All", "high", "medium", "low"], index=0
        )
    with col2:
        category_filter = st.selectbox(
            "Filter by Category", ["All"] + list(agent.categories.keys()), index=0
        )
    with col3:
        date_filter = st.selectbox(
            "Filter by Date", ["All", "Today", "This Week", "This Month", "Overdue"], index=0
        )

    df = get_all_tasks()
    if df.empty:
        st.info("No tasks found.")
        return

    filtered_df = df.copy()

    # Apply filters
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df["priority"] == priority_filter]

    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    if date_filter != "All":
        now = datetime.now()
        today = now.date()

        if date_filter == "Today":
            filtered_df = filtered_df[
                pd.to_datetime(filtered_df["due_date"]).dt.date == today
            ]
        elif date_filter == "This Week":
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            filtered_df = filtered_df[
                (pd.to_datetime(filtered_df["due_date"]).dt.date >= week_start)
                & (pd.to_datetime(filtered_df["due_date"]).dt.date <= week_end)
            ]
        elif date_filter == "This Month":
            filtered_df = filtered_df[
                pd.to_datetime(filtered_df["due_date"]).dt.month == today.month
            ]
        elif date_filter == "Overdue":
            filtered_df = filtered_df[
                pd.to_datetime(filtered_df["due_date"]) < now
            ]

    st.markdown(f"**Found {len(filtered_df)} tasks**")

    for _, task in filtered_df.iterrows():
        display_advanced_task_card(task)
        st.divider()

def show_add_task_page(agent):
    from database import add_advanced_task
    from datetime import datetime

    st.header("📝 Add New Task")

    # ✅ Step 1: Handle "clear" request BEFORE widgets render
    if st.session_state.get("clear_flag", False):
        st.session_state["task_input"] = ""
        st.session_state["manual_date"] = datetime.today()
        st.session_state["manual_time"] = datetime.now().time()
        st.session_state["estimated_time"] = 0
        st.session_state["show_notify"] = False
        st.session_state["last_task"] = None
        st.session_state["clear_flag"] = False
        st.rerun()

    # ✅ Step 2: Ensure all default session keys are initialized
    for key, default in {
        "task_input": "",
        "manual_date": datetime.today(),
        "manual_time": datetime.now().time(),
        "estimated_time": 0,
        "show_notify": False,
        "last_task": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # ✅ Step 3: Task Input Form
    with st.form("add_task_form", clear_on_submit=False):
        desc = st.text_area("Task Description", key="task_input", help="Describe the task")
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Category", ["autodetect"] + list(agent.categories.keys()) + ["other"])
        with col2:
            priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)

        manual_date = st.date_input("Due Date", key="manual_date")
        manual_time = st.time_input("Due Time", key="manual_time")
        estimate = st.number_input("Estimated Duration (min)", min_value=0, max_value=1440, key="estimated_time")

        col_submit, col_clear = st.columns([3, 1])
        with col_submit:
            submit = st.form_submit_button("🚀 Add Task")
        with col_clear:
            clear = st.form_submit_button("🧹 Clear")

        if clear:
            st.session_state["clear_flag"] = True
            st.rerun()

        if submit:
            if not desc.strip():
                st.error("Task description required")
                return

            if category == "autodetect":
                parsed = agent.parse_advanced_natural_language(desc, forced_priority=priority)
            else:
                parsed = agent.parse_advanced_natural_language(desc, forced_category=category, forced_priority=priority)

            parsed["due_date"] = datetime.combine(manual_date, manual_time).strftime('%Y-%m-%d %H:%M:%S')
            if estimate > 0:
                parsed["estimated_duration"] = estimate

            if add_advanced_task(parsed):
                st.session_state["show_notify"] = True
                st.session_state["last_task"] = parsed
                st.success("Task added")

    # ✅ Notify Me Section appears AFTER task is added
    if st.session_state.get("show_notify") and st.session_state.get("last_task"):
        with st.expander("🔔 Notify Me", expanded=False):
            with st.form("notify_me_form"):
                notify_email = st.text_input("Recipient Email", placeholder="Enter your email")
                snooze_minutes = st.number_input("Snooze (minutes before due)", min_value=1, max_value=1440, value=15)
                custom_message = st.text_area("Custom Message", placeholder="e.g. Don’t forget this task!")

                if st.form_submit_button("📧 Schedule Email Reminder"):
                    from email_reminder import handle_email_reminder
                    handle_email_reminder(
                        task=st.session_state["last_task"],
                        notify_email=notify_email,
                        snooze_minutes=snooze_minutes,
                        custom_message=custom_message
                    )
                    st.success("Reminder scheduled!")
                    st.session_state["show_notify"] = False
                    st.session_state["last_task"] = None
