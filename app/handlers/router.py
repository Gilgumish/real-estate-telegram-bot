from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from app.keyboards import (
    get_language_keyboard,
    get_service_keyboard,
    get_room_keyboard,
    get_district_keyboard,
    get_budget_keyboard,
)
from app.texts import texts
from app.utils import filter_ads
from config import ADMIN_ID


import logging
logging.basicConfig(level=logging.INFO)

router = Router()

class Form(StatesGroup):
    language = State()
    service = State()
    rooms = State()
    districts = State()
    budget = State()
    confirm = State()

@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    await message.answer(texts["uk"]["select_language"], reply_markup=get_language_keyboard())
    await state.set_state(Form.language)

@router.callback_query(F.data == "go_back")
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

@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)

    await callback.message.delete()
    await callback.message.answer(texts[lang]["language_selected"])
    await callback.message.answer(texts[lang]["select_service"], reply_markup=get_service_keyboard(lang))
    await state.set_state(Form.service)
    await callback.answer()

@router.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split("_")[1]
    user_id = callback.from_user.id
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(service=service)

    await callback.message.delete()

    if service == "sell":
        await callback.bot.send_message(
            ADMIN_ID,
            f"🧾 Новий запит на продаж/оренду!\n"
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

@router.callback_query(F.data.startswith("room_"))
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

@router.callback_query(F.data == "rooms_done")
async def rooms_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    selected = data.get("rooms", [])
    rooms = ", ".join(selected) if selected else texts[lang]["no_rooms"]

    await state.update_data(rooms=[str(r) for r in selected], districts=[])
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["rooms_done"].format(rooms=rooms))
    await callback.message.answer(texts[lang]["select_districts"], reply_markup=get_district_keyboard(lang))
    await state.set_state(Form.districts)
    await callback.answer()

@router.callback_query(F.data.startswith("district_"))
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

@router.callback_query(F.data == "districts_done")
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

@router.callback_query(F.data.startswith("budget_"))
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
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise e
    await callback.answer()

@router.callback_query(F.data == "budget_done")
async def budget_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uk")
    selected = data.get("budget", [])

    budget = ', '.join(selected) if selected else texts[lang]["no_budget"]
    await callback.message.edit_reply_markup()
    await callback.message.answer(texts[lang]["budget_done"].format(budget=budget))

    filters = {
        "service": data.get("service"),
        "rooms": data.get("rooms", []),
        "districts": data.get("districts", []),
        "budget": data.get("budget", [])
    }

    matching_ads = filter_ads(filters)
    logging.info(f"➡️ Filters: {filters}")
    logging.info(f"➡️ Matching ads: {matching_ads}")

    if not matching_ads:
        await callback.message.answer(texts[lang]["no_results"])
        return

    for ad in matching_ads:
        caption = f"{ad[f'title_{lang}']}\n💰 {ad['price']}\n📍 {ad['district']}"
        await callback.message.answer_photo(photo=ad["photo"], caption=caption)

    await callback.answer()

@router.message(F.text.lower().startswith("🛉"))
async def reset_filters(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Фільтри скинуто. Почнемо знову!", reply_markup=ReplyKeyboardRemove())
    await message.answer(texts["uk"]["select_language"], reply_markup=get_language_keyboard())
    await state.set_state(Form.language)

@router.callback_query()
async def fallback_callback(callback: CallbackQuery):
    print("📩 НЕОБРОБЛЕНИЙ callback_data:", callback.data)
    await callback.answer("⚠️ Ця кнопка поки що не працює.")
