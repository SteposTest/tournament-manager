import asyncio

import uvicorn
import uvloop
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from src.api.bot.commands import set_bot_commands
from src.api.bot.handler import router as bot_router
from src.config import settings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

dispatcher = Dispatcher()

bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


async def main():
    """Run ASGI server with uvicorn and run bot dispatcher."""
    await set_bot_commands(bot)

    config = uvicorn.Config(
        app='src.config.asgi:application',
        host='0.0.0.0',
        port=80,
        loop='uvloop',
    )
    server = uvicorn.Server(config)

    server_future = server.serve()
    bot_future = dispatcher.start_polling(bot)
    configure_bot_router()

    await asyncio.gather(server_future, bot_future)


def configure_bot_router():
    """Add bot router to dispatcher."""
    dispatcher.include_router(bot_router)


if __name__ == '__main__':
    asyncio.run(main())
