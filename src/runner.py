import asyncio
from importlib import import_module

import uvicorn
import uvloop
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from src.api.bot.representation import set_bot_representation
from src.config import settings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

dispatcher = Dispatcher()

telegram_bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


async def main():
    """Run ASGI server with uvicorn and run bot dispatcher."""
    config = uvicorn.Config(
        app='src.config.asgi:application',
        host='0.0.0.0',
        port=80,
        loop='uvloop',
    )
    server = uvicorn.Server(config)

    server_future = server.serve()
    bot_future = configure_bot()

    await asyncio.gather(server_future, bot_future)


async def configure_bot():
    """Add bot router to dispatcher."""
    dispatcher.include_router(import_module('src.api.bot.handler').router)
    await set_bot_representation(telegram_bot)
    await dispatcher.start_polling(telegram_bot)


if __name__ == '__main__':
    asyncio.run(main())
