import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ChatJoinRequest


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

router = Router()


@router.chat_join_request()
async def notify_join_request(request: ChatJoinRequest, bot: Bot) -> None:
    """Написать заявителю; заявка остаётся без изменений."""
    try:
        await bot.send_message(
            chat_id=request.from_user.id,
            text="Для принятия заявки запустите бота: @Video_BoxBot",
        )
    except TelegramForbiddenError:
        # Telegram запрещает боту первым начинать личный диалог с пользователем.
        logger.info(
            "Не удалось написать пользователю %s: он не запускал бота или запретил сообщения.",
            request.from_user.id,
        )
    except TelegramBadRequest:
        logger.exception(
            "Telegram отклонил личное сообщение пользователю %s.",
            request.from_user.id,
        )
    except TelegramAPIError:
        logger.exception(
            "Ошибка Telegram API при отправке сообщения пользователю %s.",
            request.from_user.id,
        )


async def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        token_file = Path(__file__).with_name("token.txt")
        if token_file.is_file():
            token = token_file.read_text(encoding="utf-8").strip()

    if not token:
        raise RuntimeError(
            "Токен не задан: установите переменную BOT_TOKEN "
            "или создайте token.txt рядом с main.py."
        )

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    # Бот только уведомляет заявителя и никогда не одобряет/отклоняет заявки.
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
