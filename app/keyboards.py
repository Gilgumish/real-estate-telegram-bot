from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton



def get_main_menu(lang: str = "uk") -> ReplyKeyboardMarkup:
    if lang == "uk":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🧹 Скинути фільтри")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Оберіть дію..."
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🧹 Reset filters")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Choose an action..."
        )


def get_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    return keyboard


def get_room_keyboard(lang: str, selected: list[str] = []) -> InlineKeyboardMarkup:
    def checked(val):
        return "✅" if val in selected else "👉"

    if lang == "en":
        next_btn = "✅ Next"
    else:
        next_btn = "✅ Далі"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{checked('1')} 1", callback_data="room_1")],
        [InlineKeyboardButton(text=f"{checked('2')} 2", callback_data="room_2")],
        [InlineKeyboardButton(text=f"{checked('3')} 3", callback_data="room_3")],
        [InlineKeyboardButton(text=f"{checked('4+')} 4+", callback_data="room_4+")],
        [InlineKeyboardButton(text=next_btn, callback_data="rooms_done")]
    ])


def get_district_keyboard(lang: str, selected: list[str] = []) -> InlineKeyboardMarkup:
    all_districts = {
        "uk": ["Центр", "Лук’янівка", "Позняки", "Оболонь", "Троєщина", "Дарниця", "Голосієво", "Шулявка"],
        "en": ["Center", "Lukyanivka", "Pozniaky", "Obolon", "Troieshchyna", "Darnytsia", "Holosiiv", "Shuliavka"]
    }

    def checked(val): return "✅" if val in selected else "👉"

    buttons = [
        [InlineKeyboardButton(text=f"{checked(d)} {d}", callback_data=f"district_{d}")]
        for d in all_districts[lang]
    ]
    buttons.append([InlineKeyboardButton(text="✅ Далі" if lang == "uk" else "✅ Next", callback_data="districts_done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_budget_keyboard(lang: str, selected: list[str] = []) -> InlineKeyboardMarkup:
    all_ranges = {
        "uk": ["До 15 тис.", "15-20 тис.", "20-25 тис.", "25-30 тис.", "30-35 тис.", "35-45 тис.", "45-60 тис.", "60+ тис."],
        "en": ["Up to 15k", "15-20k", "20-25k", "25-30k", "30-35k", "35-45k", "45-60k", "60k+"]
    }

    def checked(val): return "✅" if val in selected else "👉"

    buttons = [
        [InlineKeyboardButton(text=f"{checked(b)} {b}", callback_data=f"budget_{b}")]
        for b in all_ranges[lang]
    ]
    buttons.append([InlineKeyboardButton(text="✅ Готово" if lang == "uk" else "✅ Done", callback_data="budget_done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_service_keyboard(lang: str) -> InlineKeyboardMarkup:
    texts_btn = {
        "uk": ["Орендувати квартиру", "Купити квартиру", "Здати/Продати квартиру", "🔙 Назад"],
        "en": ["Rent a flat", "Buy a flat", "Sell a flat", "🔙 Back"]
    }
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 " + texts_btn[lang][0], callback_data="service_rent")],
        [InlineKeyboardButton(text="💰 " + texts_btn[lang][1], callback_data="service_buy")],
        [InlineKeyboardButton(text="🧾 " + texts_btn[lang][2], callback_data="service_sell")],
        [InlineKeyboardButton(text=texts_btn[lang][3], callback_data="go_back")]
    ])
