# email_reminder.py
import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import atexit
import requests

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))

def send_email_via_brevo(api_key, sender_email, sender_name, recipient_email, recipient_name, subject, html_content):
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": recipient_email, "name": recipient_name}],
        "subject": subject,
        "htmlContent": html_content
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        return True
    else:
        raise Exception(f"Email failed: {response.status_code} - {response.text}")

def handle_email_reminder(task, notify_email, snooze_minutes, custom_message):
    try:
        task_title = task['task_name']
        due_datetime = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M:%S")
        send_time = due_datetime - timedelta(minutes=snooze_minutes)

        subject = f"{task_title} - Reminder"
        html_content = f"""
        <html>
            <body>
                <h2>🔔 Task Reminder</h2>
                <p><strong>Task:</strong> {task_title}</p>
                <p><strong>Due At:</strong> {due_datetime}</p>
                <p><strong>Message:</strong> {custom_message}</p>
                <hr>
                <p>⏰ Reminder scheduled {snooze_minutes} minutes before the deadline</p>
            </body>
        </html>
        """

        def send_now():
            send_email_via_brevo(
                api_key="replace the api key",
                sender_email="mailid@gmail.com",
                sender_name="Task Manager Bot",
                recipient_email=notify_email,
                recipient_name="User",
                subject=subject,
                html_content=html_content
            )

        if send_time > datetime.now():
            scheduler.add_job(send_now, trigger='date', run_date=send_time)
            st.success(f"✅ Reminder scheduled for {send_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            send_now()
            st.success("✅ Reminder sent immediately")

    except Exception as e:
        st.error(f"Failed to schedule reminder: {e}")
