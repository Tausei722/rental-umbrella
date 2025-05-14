from celery import shared_task
from django.core.mail import send_mail
from .models import CustomUser
from django.conf import settings
from email.mime.text import MIMEText
import smtplib
from datetime import datetime, timedelta

@shared_task
def check_reservation_status():
    now = datetime.now()
    due = now - timedelta(days=1)

    reservations = CustomUser.objects.filter(borrowed_umbrella__isnull=False,update_at__lte=due)

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD

    for reservation in reservations:
        # メール本文の作成
        email_body = """\
            こんにちは、{username} さん

            傘のレンタル状況を確認してください。

            24時間以上傘をレンタルしています。
            お時間あるときに傘置き場に返却をお願いします。

            このリンクの有効期限は1時間です。
            """
        
        email_body = email_body.format(
            username=reservation.username,

        )

        msg = MIMEText(email_body, "html")
        msg["Subject"] = "パスワードリセット"
        msg["From"] = smtp_user
        msg["To"] = reservation.email

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [reservation.email], msg.as_string())
            server.quit()
        except smtplib.SMTPException as e:
            f"できませんでした"
    return f"{reservations.count()} 件の通知を送信しました"