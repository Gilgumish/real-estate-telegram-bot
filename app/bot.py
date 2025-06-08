import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from config import BOT_TOKEN
from app.keyboards import get_language_keyboard, get_service_keyboard
from app.texts import texts


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def start_handler(message: Message):
    if message.text == "/start":
        await message.answer(texts["uk"]["select_language"], reply_markup=get_language_keyboard())


@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer(texts[lang]["language_selected"])
    await callback.message.answer(texts[lang]["select_service"], reply_markup=get_service_keyboard(lang))
    await callback.answer()


@dp.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery):
    await callback.message.delete()
    service = callback.data.split("_")[1]
    lang = "uk"  # тимчасово
    await callback.message.answer(texts[lang][service])
    await callback.answer()



async def main():
    async def on_startup(bot: Bot):
        print("✅ Бот запущено!")
    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
