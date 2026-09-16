"""
Тест отправки письма через Flask-Mail.
Запуск: python test_mail.py
"""
from dotenv import load_dotenv
from flask import Flask
from loguru import logger

from core.auth.mailer import init_mail, send_login_code

load_dotenv()

# Создаём Flask-приложение
app = Flask(__name__)
init_mail(app)

# Тест: отправляем код на ваш же email
test_email = "staffpm@yandex.ru"
test_code = "123456"

print(f"\n📧 Отправляю тестовый код на {test_email}...")
print(f"🔑 Код: {test_code}\n")

with app.app_context():
    result = send_login_code(test_email, test_code)

if result:
    print("✅ Письмо отправлено. Проверьте почту (и папку «Спам»).")
else:
    print("❌ Ошибка отправки. Смотрите лог выше.")