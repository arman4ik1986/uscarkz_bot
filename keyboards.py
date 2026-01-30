from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from calculator import get_all_brands, get_models_by_brand


def brands_kb():
    buttons = [[KeyboardButton(text=b)] for b in get_all_brands()]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def models_kb(brand):
    buttons = [[KeyboardButton(text=m)] for m in get_models_by_brand(brand)]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Подобрать авто")],
        [KeyboardButton(text="📂 Мои заявки")]
    ],
    resize_keyboard=True
)

body_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Седан"), KeyboardButton(text="SUV")],
        [KeyboardButton(text="Электро")],
    ], resize_keyboard=True
)
