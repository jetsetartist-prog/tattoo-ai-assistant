"""
Базовые интерфейсы для мультиплатформенной архитектуры.
Ядро работает только с этими абстракциями и не знает про VK/Telegram/WhatsApp.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable, Awaitable, Any


@dataclass
class Button:
    """Универсальная кнопка. Адаптер сам решает, как её отрисовать."""
    label: str
    payload: str = ""
    color: str = "default"


@dataclass
class IncomingMessage:
    """Универсальное входящее сообщение."""
    platform: str
    user_id: str
    chat_id: str
    text: str
    raw: Any = None


MessageHandler = Callable[[IncomingMessage, "MessageAdapter"], Awaitable[None]]


class MessageAdapter(ABC):
    """Интерфейс платформенного адаптера."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Имя платформы: 'vk', 'telegram', 'whatsapp'."""
        ...

    @abstractmethod
    async def send_message(
        self,
        chat_id: str,
        text: str,
        buttons: Optional[list[Button]] = None,
    ) -> None:
        """Отправить сообщение в чат."""
        ...

    @abstractmethod
    async def start(self, handler: MessageHandler) -> None:
        """Запустить получение событий."""
        ...
