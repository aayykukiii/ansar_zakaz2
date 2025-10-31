from aiogram import Bot, Dispatcher
import logging
import asyncio
from config import TOKEN
from handlers import router
from database.db import on_startup


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await on_startup()
    await dp.start_polling(bot)
    


if __name__ == "__main__":
    asyncio.run(main())