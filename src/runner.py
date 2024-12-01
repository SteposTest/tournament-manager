import asyncio

import uvicorn
import uvloop
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from src.config import settings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

dispatcher = Dispatcher()

bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))


async def main():
    config = uvicorn.Config(
        app='src.config.asgi:application',
        host='0.0.0.0',
        port=80,
        loop='uvloop',
    )
    server = uvicorn.Server(config)

    server_future = server.serve()
    bot_future = dispatcher.start_polling(bot)

    await asyncio.gather(server_future, bot_future)


if __name__ == '__main__':
    asyncio.run(main())
