import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER")  # your Gmail address
SMTP_PASS = os.environ.get("SMTP_PASS")  # your Gmail App Password


def send_email(to_email: str, subject: str, body: str):
    if not (SMTP_USER and SMTP_PASS):
        raise RuntimeError("SMTP_USER/SMTP_PASS not set in environment.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)


if __name__ == "__main__":
    # Quick manual test (set env first)
    test_to = os.environ.get("TEST_TO", SMTP_USER)
    send_email(test_to, "Crypto-Alert test", "This is a test email from crypto-alert.")
    print("Email sent!")

