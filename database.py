# database.py
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st


import sqlite3
import pandas as pd
from datetime import datetime

# Global connection object to be initialized lazily
conn = None

def get_connection():
    """
    Lazy-initialize a cached database connection with table creation.
    Ensures that st.cache_resource is only called after set_page_config.
    """
    global conn
    if conn is None:
        import streamlit as st

        @st.cache_resource
        def init_database():
            c = sqlite3.connect("advanced_tasks.db", check_same_thread=False)
            cur = c.cursor()

            # Table for tasks
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT,
                    category TEXT,
                    priority TEXT,
                    due_date TEXT,
                    status TEXT,
                    tags TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    estimated_duration INTEGER,
                    ai_suggestions TEXT,
                    context_keywords TEXT
                )
            ''')

            # Table for analytics
            cur.execute('''
                CREATE TABLE IF NOT EXISTS task_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    completed_tasks INTEGER,
                    productivity_score REAL,
                    category_performance TEXT
                )
            ''')

            c.commit()
            return c

        conn = init_database()

    return conn



def add_advanced_task(task_data):
    """
    Add a new task to the database using validated data from the agent.
    """
    try:
        c = get_connection().cursor()
        c.execute('''
            INSERT INTO tasks (
                task_name, category, priority, due_date, status, tags,
                estimated_duration, ai_suggestions, context_keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data["task_name"],
            task_data["category"],
            task_data["priority"],
            task_data["due_date"],
            task_data["status"],
            task_data["tags"],
            int(task_data["estimated_duration"]),
            str(task_data["ai_suggestions"]),
            str(task_data["context_keywords"])
        ))
        get_connection().commit()
        return True

    except Exception as e:
        import streamlit as st
        st.error(f"Error adding task: {e}")
        return False


def update_task(task_id, name, category, priority, due_date, tags, duration, suggestions, keywords):
    try:
        c = get_connection().cursor()
        c.execute('''UPDATE tasks SET
            task_name = ?, category = ?, priority = ?, due_date = ?,
            tags = ?, estimated_duration = ?, ai_suggestions = ?, context_keywords = ?
            WHERE task_id = ?''', (
            name, category, priority, due_date, tags,
            duration, suggestions, keywords, task_id
        ))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating task: {e}")
        return False

def delete_task(task_id):
    try:
        c = get_connection().cursor()
        c.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting task: {e}")
        return False

def update_task_status(task_id, status):
    try:
        c = get_connection().cursor()
        c.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating task status: {e}")
        return False


def get_all_tasks():
    try:
        conn = get_connection()
        return pd.read_sql_query(
            "SELECT * FROM tasks WHERE status != 'completed' ORDER BY due_date ASC", conn
        )
    except Exception as e:
        print(f"[get_all_tasks] Error: {e}")
        return pd.DataFrame()


def get_completed_tasks():
    try:
        conn = get_connection()
        return pd.read_sql_query("SELECT * FROM tasks WHERE status = 'completed' ORDER BY created_at DESC", conn)
    except Exception as e:
        print(f"[get_completed_tasks] Error: {e}")
        return pd.DataFrame()

def get_overdue_tasks():
    try:
        conn = get_connection()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return pd.read_sql_query("SELECT * FROM tasks WHERE due_date < ? AND status != 'completed'", conn, params=(now,))
    except Exception as e:
        print(f"[get_overdue_tasks] Error: {e}")
        return pd.DataFrame()


def get_pending_tasks():
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return pd.read_sql_query("SELECT * FROM tasks WHERE status = 'pending' AND due_date >= ?", conn, params=(now,))
    except:
        return pd.DataFrame()

def get_smart_recommendations():
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM tasks", conn)

        if df.empty:
            return []

        recos = []

        overdue = df[
            (df['status'] != 'completed') &
            (pd.to_datetime(df['due_date']) < datetime.now())
        ]
        high_priority = df[
            (df['status'] != 'completed') &
            (df['priority'] == 'high')
        ]
        total_est_time = df[df['status'] != 'completed']['estimated_duration'].sum()

        if len(overdue) > 0:
            recos.append(f"⏰ You have {len(overdue)} overdue tasks. Prioritize completing them first.")

        if total_est_time > 300:
            recos.append("⏱️ Your pending tasks require significant time. Consider prioritizing the most important ones.")

        if len(high_priority) > 0:
            recos.append(f"🔥 You have {len(high_priority)} high priority tasks pending.")

        return recos

    except Exception as e:
        print(f"[get_smart_recommendations] Error: {e}")
        return []


def get_tasks_analytics():
    try:
        query = """
            SELECT 
                task_id,
                task_name,
                status,
                due_date,
                estimated_duration
            FROM tasks
        """
        df = pd.read_sql_query(query, get_connection())

        if df.empty:
            return {}

        return {
            "total_estimated_time": df['estimated_duration'].sum(),
            "completed_tasks": len(df[df['status'] == 'completed']),
            "pending_tasks": len(df[df['status'] == 'pending']),
            "overdue_tasks": len(get_overdue_tasks()),
            "total_tasks": len(df)
        }
    except Exception as e:
        st.error(f"Analytics error: {e}")
        return {}

