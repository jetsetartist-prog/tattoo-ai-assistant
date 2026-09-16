"""
Хранение сессий мастеров и генерация паролей.
"""
import secrets
import string
import time
from typing import Optional

# {session_token: {"email": ..., "expires_at": timestamp}}
_sessions: dict = {}

SESSION_TTL_SECONDS = 7 * 24 * 3600   # 7 дней


def generate_password() -> str:
    """
    Генерирует читаемый пароль формата 'Tattoo-A7k9-Mn2p'.
    Легко диктовать по телефону, но достаточно безопасно.
    """
    part1 = secrets.choice(string.ascii_uppercase) + "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(3)
    )
    part2 = secrets.choice(string.ascii_uppercase) + "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(3)
    )
    return f"Tattoo-{part1}-{part2}"


def create_session(email: str) -> str:
    """Создаёт сессию и возвращает токен."""
    token = secrets.token_urlsafe(32)
    _sessions[token] = {
        "email": email.lower(),
        "expires_at": time.time() + SESSION_TTL_SECONDS,
    }
    return token


def get_session(token: str) -> Optional[str]:
    """Возвращает email по токену сессии, если она жива."""
    entry = _sessions.get(token)
    if not entry:
        return None
    if time.time() > entry["expires_at"]:
        del _sessions[token]
        return None
    return entry["email"]


def destroy_session(token: str) -> None:
    """Удаляет сессию (выход)."""
    _sessions.pop(token, None)