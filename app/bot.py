import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from config import BOT_TOKEN
from app.keyboards import get_language_keyboard, get_service_keyboard, get_room_keyboard, get_district_keyboard, \
    get_budget_keyboard
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



from config import ADMIN_ID

@dp.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery):
    await callback.message.delete()
    service = callback.data.split("_")[1]
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "uk")

    if service == "sell":
        # 📩 Повідомлення адміну
        await bot.send_message(
            ADMIN_ID,
            f"🧾 Новий запит на продаж/оренду!\n"
            f"Ім’я: {callback.from_user.full_name}\n"
            f"Username: @{callback.from_user.username or 'немає'}\n"
            f"ID: {user_id}"
        )

        # ✅ Повідомлення користувачу
        confirm_text = "Дякуємо! Наш ріелтор зв'яжеться з вами найближчим часом." if lang == "uk" else \
                       "Thank you! Our agent will contact you shortly."
        await callback.message.answer(confirm_text)
        await callback.answer()
        return

    # Інша логіка (rent/buy)
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

    user_data[user_id]["districts"] = []
    await callback.message.answer(texts[lang]["select_districts"], reply_markup=get_district_keyboard(lang))
    await callback.answer()


@dp.callback_query(F.data.startswith("district_"))
async def select_district(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "uk")
    selected = user_data.get(user_id, {}).get("districts", [])

    district = callback.data.split("_", 1)[1]
    if district in selected:
        selected.remove(district)
    else:
        selected.append(district)

    user_data[user_id]["districts"] = selected

    await callback.message.edit_reply_markup(reply_markup=get_district_keyboard(lang, selected))
    await callback.answer()


@dp.callback_query(F.data == "districts_done")
async def districts_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "uk")
    selected = user_data.get(user_id, {}).get("districts", [])

    districts = ', '.join(selected) if selected else texts[lang]["no_districts"]
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["districts_done"].format(districts=districts))
    await callback.message.answer(
        texts[lang]["select_budget"],
        reply_markup=get_budget_keyboard(lang)
    )
    user_data[user_id]["budget"] = []


@dp.callback_query(F.data.startswith("budget_"))
async def select_budget(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "uk")
    selected = user_data[user_id].get("budget", [])

    value = callback.data.split("_", 1)[1]
    if value in selected:
        selected.remove(value)
    else:
        selected.append(value)

    user_data[user_id]["budget"] = selected

    try:
        await callback.message.edit_reply_markup(reply_markup=get_budget_keyboard(lang, selected))
    except Exception as e:
        print(f"⚠️ Не оновлено бюджет: {e}")

    await callback.answer()



@dp.callback_query(F.data == "budget_done")
async def budget_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "uk")
    selected = user_data[user_id].get("budget", [])

    budget = ', '.join(selected) if selected else texts[lang]["no_budget"]
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["budget_done"].format(budget=budget))
    await callback.answer()



async def main():
    async def on_startup(bot: Bot):
        print("✅ Бот запущено!")
    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
