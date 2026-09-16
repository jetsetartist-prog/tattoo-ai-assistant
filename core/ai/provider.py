"""
AI-провайдер: абстракция над GigaChat/OpenAI.
Пока использует GigaChat (для России). Позже можно добавить другие.
"""
import os
import uuid
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from loguru import logger
import requests

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

# GigaChat
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat-Pro")

SYSTEM_PROMPT = """Ты дружелюбный AI-ассистент тату-салона.

О салоне:
- Стили: графика, реализм, япония, нью-скул, олдскул, минимализм, орнаменты
- Эскиз — от 2000₽
- Маленькая (до 10 см) — от 5000₽
- Средняя (10-20 см) — от 10000₽
- Большая (20+ см) — от 20000₽

Отвечай кратко (до 300 символов), дружелюбно, на «ты». Используй эмодзи 😊
Если клиент хочет записаться — направь к кнопке «Записаться».
"""

# История диалогов (в памяти; позже можно перенести в БД)
_conversation_history: Dict[str, List[Dict]] = {}

# Кэш токена
_token_cache: Optional[str] = None
_token_expires: Optional[datetime] = None


def _get_conversation(user_key: str) -> List[Dict]:
    return _conversation_history.get(user_key, [])


def _add_to_conversation(user_key: str, role: str, content: str) -> None:
    if user_key not in _conversation_history:
        _conversation_history[user_key] = []
    _conversation_history[user_key].append({"role": role, "content": content})
    if len(_conversation_history[user_key]) > 10:
        _conversation_history[user_key] = _conversation_history[user_key][-10:]


def _get_gigachat_token() -> Optional[str]:
    global _token_cache, _token_expires
    import base64

    if _token_cache and _token_expires and datetime.now() < _token_expires:
        return _token_cache

    auth_string = None
    if GIGACHAT_CREDENTIALS:
        auth_string = GIGACHAT_CREDENTIALS
    elif GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET:
        creds = f"{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}"
        auth_string = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
    else:
        logger.warning("[AI] GigaChat credentials не настроены")
        return None

    try:
        headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
        }
        response = requests.post(
            GIGACHAT_AUTH_URL,
            headers=headers,
            data="scope=GIGACHAT_API_PERS",
            timeout=10,
            verify=False,
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                _token_cache = token
                _token_expires = datetime.now() + timedelta(minutes=25)
                return token
        logger.error(f"[AI] GigaChat auth error: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"[AI] Ошибка получения токена: {e}")
        return None


def get_ai_response(user_message: str, user_key: str) -> Optional[str]:
    """Получить ответ от AI. user_key — уникальный идентификатор (platform:user_id)."""
    token = _get_gigachat_token()
    if not token:
        return None

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in _get_conversation(user_key):
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "model": GIGACHAT_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False,
        }
        response = requests.post(
            GIGACHAT_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=15,
            verify=False,
        )
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("choices", [{}])[0].get("message", {}).get("content")
            if ai_response:
                _add_to_conversation(user_key, "user", user_message)
                _add_to_conversation(user_key, "assistant", ai_response)
                return ai_response
        logger.error(f"[AI] GigaChat error: {response.status_code} — {response.text[:200]}")
        return None
    except Exception as e:
        logger.error(f"[AI] Ошибка: {e}")
        return None


def clear_conversation(user_key: str) -> None:
    """Очистить историю диалога пользователя."""
    if user_key in _conversation_history:
        del _conversation_history[user_key]