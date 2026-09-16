"""
Отправка email с паролями мастерам.
Использует Flask-Mail.
Поддерживает любой SMTP: Yandex, Gmail, Mail.ru, SendGrid и др.
"""
import os
from flask import Flask
from flask_mail import Mail, Message
from loguru import logger

# Глобальный экземпляр Mail
_mail = None


def init_mail(app: Flask) -> Mail:
    """Инициализирует Flask-Mail в приложении."""
    global _mail

    mail_server = os.getenv('MAIL_SERVER', 'smtp.yandex.ru')
    mail_port = int(os.getenv('MAIL_PORT', '465'))
    mail_use_ssl = os.getenv('MAIL_USE_SSL', 'true').lower() == 'true'
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'false').lower() == 'true'
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_sender = os.getenv('MAIL_DEFAULT_SENDER', mail_username)

    app.config['MAIL_SERVER'] = mail_server
    app.config['MAIL_PORT'] = mail_port
    app.config['MAIL_USE_SSL'] = mail_use_ssl
    app.config['MAIL_USE_TLS'] = mail_use_tls
    app.config['MAIL_USERNAME'] = mail_username
    app.config['MAIL_PASSWORD'] = mail_password
    app.config['MAIL_DEFAULT_SENDER'] = mail_sender

    _mail = Mail(app)

    logger.info(
        f"[Mail] Инициализирован SMTP: {mail_server}:{mail_port} "
        f"(SSL={mail_use_ssl}, TLS={mail_use_tls}, user={mail_username})"
    )

    if not mail_username or not mail_password:
        logger.warning("[Mail] MAIL_USERNAME или MAIL_PASSWORD не заданы в .env")

    return _mail


def send_master_password(to_email: str, password: str) -> bool:
    """
    Отправляет пароль мастера на email.
    Возвращает True, если письмо отправлено.
    """
    if _mail is None:
        logger.error("[Mail] Mail не инициализирован. Вызовите init_mail(app).")
        return False

    try:
        subject = "🔐 Ваш пароль для входа в кабинет мастера"

        body_text = f"""Здравствуйте!

Ваш пароль для входа в кабинет мастера:

    {password}

Сохраните его — он понадобится для входа.

Если вы не запрашивали пароль — проигнорируйте это письмо.

—
AI-ассистент тату-салона
"""

        body_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px;">
  <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <h2 style="color: #075e54; margin-top: 0;">Пароль для входа</h2>
    <p style="color: #333; font-size: 15px;">Ваш пароль для входа в кабинет мастера:</p>
    <div style="background: #f0f8f5; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
      <div style="font-size: 24px; letter-spacing: 2px; color: #075e54; font-weight: bold; font-family: monospace;">{password}</div>
    </div>
    <p style="color: #333; font-size: 15px;">Сохраните его — он понадобится для входа.</p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
    <p style="color: #999; font-size: 12px; margin: 0;">
      Если вы не запрашивали пароль — просто проигнорируйте это письмо.
    </p>
  </div>
</body>
</html>
"""

        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body_text,
            html=body_html,
        )

        _mail.send(msg)
        logger.info(f"[Mail] Пароль отправлен на {to_email}")
        return True

    except Exception as e:
        logger.error(f"[Mail] Ошибка отправки на {to_email}: {e}")
        return False