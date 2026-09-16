"""
Мультиплатформенная точка входа.
Запускает ядро с VK-адаптером.
Запуск: python main_multiplatform.py
"""
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from adapters.vk_adapter import VKAdapter
from core.handlers.message_handler import handle_incoming
from core.storage.leads import init_db

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))


async def main():
    if not VK_TOKEN or not GROUP_ID:
        logger.error("VK_TOKEN и GROUP_ID не заданы в .env")
        return

    # Инициализируем БД
    init_db()

    adapter = VKAdapter(VK_TOKEN, GROUP_ID)
    logger.info(f"Запуск ядра с адаптером: {adapter.platform_name}")
    await adapter.start(handle_incoming)


if __name__ == "__main__":
    asyncio.run(main())