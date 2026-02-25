import os
import smtplib
from email.message import EmailMessage

host = "smtp.gmail.com"
port = 587

user = os.environ.get("SMTP_USER")
pw = os.environ.get("SMTP_PASS")
to_email = os.environ.get("TO_EMAIL")

msg = EmailMessage()
msg["Subject"] = "TEST ALERT — Clinician Monitor"
msg["From"] = user
msg["To"] = to_email
msg.set_content("If you see this, email sending works!")

with smtplib.SMTP(host, port, timeout=10) as s:
    s.starttls()
    s.login(user, pw)
    s.send_message(msg)

print("TEST EMAIL SENT SUCCESSFULLY")
