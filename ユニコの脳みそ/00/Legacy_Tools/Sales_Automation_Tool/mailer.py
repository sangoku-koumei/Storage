
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_smtp(smtp_settings, to_email, subject, body):
    """
    SMTPを使ってメールを送信する
    smtp_settings: {
        "server": "smtp.gmail.com",
        "port": 587,
        "email": "user@res.com",
        "password": "app_password"
    }
    """
    msg = MIMEMultipart()
    msg['From'] = smtp_settings['email']
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Check Daily Limit
        from db import check_daily_limit
        is_safe, count = check_daily_limit(limit=30) # 安全のため30通/日に制限
        if not is_safe:
            return {"success": False, "message": f"Daily Limit Exceeded ({count}/30). Stop for today."}

        server = smtplib.SMTP(smtp_settings['server'], smtp_settings['port'])
        server.starttls()
        server.login(smtp_settings['email'], smtp_settings['password'])
        text = msg.as_string()
        server.sendmail(smtp_settings['email'], to_email, text)
        server.quit()
        return {"success": True, "message": "Sent successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}
