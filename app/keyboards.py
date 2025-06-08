from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    return keyboard


def get_service_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Rent", callback_data="service_rent")],
            [InlineKeyboardButton(text="💸 Buy", callback_data="service_buy")],
            [InlineKeyboardButton(text="🧳 Rent/Sell property", callback_data="service_sell")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Орендувати квартиру", callback_data="service_rent")],
        [InlineKeyboardButton(text="💸 Купити квартиру", callback_data="service_buy")],
        [InlineKeyboardButton(text="🧳 Здати/Продати квартиру", callback_data="service_sell")]
    ])
