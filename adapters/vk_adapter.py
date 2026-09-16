"""
VK-адаптер. Оборачивает VK-код в интерфейс MessageAdapter.
Логика переподключения перенесена из старого src/main.py.
"""
import asyncio
import time
from typing import Optional
from loguru import logger
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.exceptions import VkApiError, ApiError
from requests.exceptions import ReadTimeout, ConnectionError, RequestException

from core.messaging.base import MessageAdapter, IncomingMessage, Button, MessageHandler


class VKAdapter(MessageAdapter):
    def __init__(self, token: str, group_id: int):
        self.token = token
        self.group_id = group_id
        self.vk_session = VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id, wait=25)
        logger.info(f"[VK] Адаптер инициализирован, группа {group_id}")

    @property
    def platform_name(self) -> str:
        return "vk"

    def _buttons_to_keyboard(self, buttons: list[Button]) -> str:
        """Превращает универсальные кнопки в VK-клавиатуру."""
        keyboard = VkKeyboard(one_time=False)
        for i, btn in enumerate(buttons):
            if i > 0 and i % 3 == 0:
                keyboard.add_line()
            color_map = {
                "primary": VkKeyboardColor.PRIMARY,
                "secondary": VkKeyboardColor.SECONDARY,
                "danger": VkKeyboardColor.NEGATIVE,
                "default": VkKeyboardColor.SECONDARY,
            }
            keyboard.add_button(
                btn.label,
                color=color_map.get(btn.color, VkKeyboardColor.SECONDARY),
            )
        return keyboard.get_keyboard()

    async def send_message(
        self,
        chat_id: str,
        text: str,
        buttons: Optional[list[Button]] = None,
    ) -> None:
        """Отправка сообщения. chat_id для VK — это peer_id."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_sync, chat_id, text, buttons)
        except Exception as e:
            logger.error(f"[VK] Ошибка отправки в {chat_id}: {e}")

    def _send_sync(self, chat_id: str, text: str, buttons: Optional[list[Button]] = None):
        """Синхронная отправка (VK API синхронный)."""
        params = {
            "peer_id": int(chat_id),
            "message": text,
            "random_id": get_random_id(),
        }
        if buttons:
            params["keyboard"] = self._buttons_to_keyboard(buttons)
        self.vk.messages.send(**params)

    async def start(self, handler: MessageHandler) -> None:
        """Запуск longpoll. Логика переподключения — как в старом main.py."""
        logger.info("[VK] Слушаем события...")
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def _sync_listener():
            """Синхронный слушатель с автопереподключением."""
            max_attempts = 10
            reconnect_delay = 5

            while True:
                try:
                    reconnect_attempt = 0
                    reconnect_delay = 5

                    for event in self.longpoll.listen():
                        if event.type != VkBotEventType.MESSAGE_NEW:
                            continue
                        if event.message.get("out") == 1:
                            continue
                        loop.call_soon_threadsafe(queue.put_nowait, event)

                except (ReadTimeout, ConnectionError, RequestException) as e:
                    reconnect_attempt += 1
                    logger.warning(f"[VK] Сетевая ошибка ({reconnect_attempt}/{max_attempts}): {e}")
                    if reconnect_attempt >= max_attempts:
                        logger.error("[VK] Слишком много ошибок, пауза 60 сек")
                        time.sleep(60)
                        reconnect_attempt = 0
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, 60)
                    try:
                        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id, wait=25)
                        logger.info("[VK] Переподключение успешно")
                    except Exception as re:
                        logger.error(f"[VK] Ошибка переподключения: {re}")

                except (VkApiError, ApiError) as e:
                    reconnect_attempt += 1
                    logger.warning(f"[VK] Ошибка VK API ({reconnect_attempt}/{max_attempts}): {e}")
                    if reconnect_attempt >= max_attempts:
                        logger.error("[VK] Слишком много ошибок, пауза 60 сек")
                        time.sleep(60)
                        reconnect_attempt = 0
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, 60)

                except Exception as e:
                    reconnect_attempt += 1
                    logger.error(f"[VK] Критическая ошибка ({reconnect_attempt}/{max_attempts}): {e}")
                    if reconnect_attempt >= max_attempts:
                        logger.error("[VK] Слишком много ошибок, пауза 60 сек")
                        time.sleep(60)
                        reconnect_attempt = 0
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, 60)
                    try:
                        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id, wait=25)
                    except Exception as re:
                        logger.error(f"[VK] Ошибка переподключения: {re}")

        # Запускаем синхронный слушатель в отдельном потоке
        loop.run_in_executor(None, _sync_listener)

        # Асинхронно обрабатываем очередь
        while True:
            event = await queue.get()
            msg = IncomingMessage(
                platform="vk",
                user_id=str(event.message["from_id"]),
                chat_id=str(event.message.get("peer_id", event.message["from_id"])),
                text=event.message.get("text", "").strip(),
                raw=event.obj,
            )
            if not msg.text:
                continue
            try:
                await handler(msg, self)
            except Exception as e:
                logger.error(f"[VK] Ошибка в handler: {e}", exc_info=True)