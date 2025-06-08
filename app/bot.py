import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.utils import filter_ads
from config import BOT_TOKEN, ADMIN_ID
from app.keyboards import (
    get_language_keyboard,
    get_service_keyboard,
    get_room_keyboard,
    get_district_keyboard,
    get_budget_keyboard,
    get_main_menu
)
from app.texts import texts

class Form(StatesGroup):
    language = State()
    service = State()
    rooms = State()
    districts = State()
    budget = State()
    confirm = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def start_handler(message: Message, state: FSMContext):
    if message.text == "/start":
        await message.answer(texts["uk"]["select_language"], reply_markup=get_language_keyboard())
        await state.set_state(Form.language)


@dp.callback_query(F.data == "go_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    data = await state.get_data()
    lang = data.get("lang", "uk")

    if current == Form.service:
        await state.set_state(Form.language)
        await callback.message.edit_text(texts["uk"]["select_language"], reply_markup=get_language_keyboard())
    elif current == Form.rooms:
        await state.set_state(Form.service)
        await callback.message.edit_text(texts[lang]["select_service"], reply_markup=get_service_keyboard(lang))

    await callback.answer()


@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)

    await callback.message.delete()
    await callback.message.answer(texts[lang]["language_selected"])
    await callback.message.answer(texts[lang]["select_service"], reply_markup=get_service_keyboard(lang))
    await state.set_state(Form.service)
    await callback.answer()


@dp.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split("_")[1]
    user_id = callback.from_user.id
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(service=service)

    await callback.message.delete()

    if service == "sell":
        await bot.send_message(
            ADMIN_ID,
            f"\U0001F9FE Новий запит на продаж/оренду!\n"
            f"Ім’я: {callback.from_user.full_name}\n"
            f"Username: @{callback.from_user.username or 'немає'}\n"
            f"ID: {user_id}"
        )
        confirm = "Дякуємо! Наш ріелтор зв'яжеться з вами." if lang == "uk" else "Thank you! Our agent will contact you."
        await callback.message.answer(confirm)
        await callback.answer()
        return

    await state.update_data(rooms=[])
    await callback.message.answer(texts[lang][service])
    await callback.message.answer(texts[lang]["select_rooms"], reply_markup=get_room_keyboard(lang))
    await state.set_state(Form.rooms)
    await callback.answer()


@dp.callback_query(F.data.startswith("room_"))
async def select_room(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    selected = data.get("rooms", [])
    room = callback.data.split("_")[1]

    if room in selected:
        selected.remove(room)
    else:
        selected.append(room)

    await state.update_data(rooms=selected)
    await callback.message.edit_reply_markup(reply_markup=get_room_keyboard(lang, selected))
    await callback.answer()


@dp.callback_query(F.data == "rooms_done")
async def rooms_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    selected = data.get("rooms", [])
    rooms = ", ".join(selected) if selected else texts[lang]["no_rooms"]

    await state.update_data(districts=[])
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["rooms_done"].format(rooms=rooms))
    await callback.message.answer(texts[lang]["select_districts"], reply_markup=get_district_keyboard(lang))
    await state.set_state(Form.districts)
    await callback.answer()


@dp.callback_query(F.data.startswith("district_"))
async def select_district(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    selected = data.get("districts", [])
    district = callback.data.split("_", 1)[1]

    if district in selected:
        selected.remove(district)
    else:
        selected.append(district)

    await state.update_data(districts=selected)
    await callback.message.edit_reply_markup(reply_markup=get_district_keyboard(lang, selected))
    await callback.answer()


@dp.callback_query(F.data == "districts_done")
async def districts_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    selected = data.get("districts", [])
    districts = ", ".join(selected) if selected else texts[lang]["no_districts"]

    await state.update_data(budget=[])
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["districts_done"].format(districts=districts))
    await callback.message.answer(texts[lang]["select_budget"], reply_markup=get_budget_keyboard(lang))
    await state.set_state(Form.budget)
    await callback.answer()


@dp.callback_query(F.data.startswith("budget_"))
async def select_budget(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    selected = data.get("budget", [])
    value = callback.data.split("_", 1)[1]

    if value in selected:
        selected.remove(value)
    else:
        selected.append(value)

    await state.update_data(budget=selected)

    try:
        await callback.message.edit_reply_markup(reply_markup=get_budget_keyboard(lang, selected))
    except Exception as e:
        print(f"⚠️ Не оновлено бюджет: {e}")
    await callback.answer()


@dp.callback_query(F.data == "budget_done")
async def budget_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uk")
    selected = data.get("budget", [])

    budget = ', '.join(selected) if selected else texts[lang]["no_budget"]
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["budget_done"].format(budget=budget))

    # 🧠 Збір фільтрів користувача
    filters = {
        "service": data.get("service"),
        "rooms": data.get("rooms", []),
        "districts": data.get("districts", []),
        "budget": data.get("budget", [])
    }

    matching_ads = filter_ads(filters)

    if not matching_ads:
        await callback.message.answer(texts[lang]["no_results"])
        return

    for ad in matching_ads:
        caption = f"{ad[f'title_{lang}']}\n💰 {ad['price']}\n📍 {ad['district']}"
        await callback.message.answer_photo(photo=ad["photo"], caption=caption)

    await callback.answer()


@dp.message(F.text.lower().startswith("🧹"))
async def reset_filters(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Фільтри скинуто. Почнемо знову!", reply_markup=ReplyKeyboardRemove())
    await message.answer(texts["uk"]["select_language"], reply_markup=get_language_keyboard())
    await state.set_state(Form.language)


async def main():
    async def on_startup(bot: Bot):
        print("✅ Бот запущено!")
    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
