import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from config import BOT_TOKEN
from app.keyboards import get_language_keyboard, get_service_keyboard, get_room_keyboard
from app.texts import texts


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}



@dp.message()
async def start_handler(message: Message):
    if message.text == "/start":
        await message.answer(texts["uk"]["select_language"], reply_markup=get_language_keyboard())


@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    # 🔁 Зберігаємо мову одразу після вибору
    user_data[user_id] = {
        "lang": lang,
        "rooms": []
    }

    await callback.message.delete()
    await callback.message.answer(texts[lang]["language_selected"])
    await callback.message.answer(texts[lang]["select_service"], reply_markup=get_service_keyboard(lang))
    await callback.answer()



@dp.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery):
    await callback.message.delete()
    service = callback.data.split("_")[1]
    user_id = callback.from_user.id

    lang = user_data.get(user_id, {}).get("lang", "uk")

    await callback.message.answer(texts[lang][service])
    await callback.message.answer(texts[lang]["select_rooms"], reply_markup=get_room_keyboard(lang))
    await callback.answer()


@dp.callback_query(F.data.startswith("room_"))
async def select_room(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "uk")
    selected = user_data.get(user_id, {}).get("rooms", [])

    room = callback.data.split("_")[1]
    if room in selected:
        selected.remove(room)
    else:
        selected.append(room)

    user_data[user_id]["rooms"] = selected

    await callback.message.edit_reply_markup(reply_markup=get_room_keyboard(lang, selected))
    await callback.answer()


@dp.callback_query(F.data == "rooms_done")
async def rooms_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "uk")
    selected_rooms = user_data.get(user_id, {}).get("rooms", [])

    rooms = ', '.join(selected_rooms) if selected_rooms else texts[lang]["no_rooms"]
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["rooms_done"].format(rooms=rooms))
    await callback.answer()


async def main():
    async def on_startup(bot: Bot):
        print("✅ Бот запущено!")
    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
