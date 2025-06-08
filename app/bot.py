import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.handlers.router import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    async def on_startup(bot: Bot):
        print("✅ Бот запущено!")

    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
