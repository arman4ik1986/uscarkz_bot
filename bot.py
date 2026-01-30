import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, USD_TO_KZT
from keyboards import main_kb, brands_kb, models_kb
from states import SearchCar
from calculator import calculate_total
from copart_api import search_copart
from iaai_api import search_iaai
from database import init_db, save_request

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("🚗 Бот подбора авто из США", reply_markup=main_kb)

@dp.message(F.text == "🔍 Подобрать авто")
async def start_search(message: Message, state: FSMContext):
    await message.answer("Выберите марку:", reply_markup=brands_kb())
    await state.set_state(SearchCar.brand)
    
@dp.message(SearchCar.brand)
async def choose_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Выберите модель:", reply_markup=models_kb(message.text))
    await state.set_state(SearchCar.model)

@dp.message(SearchCar.model)
async def choose_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите год автомобиля:")
    await state.set_state(SearchCar.year)

@dp.message(SearchCar.year)
async def choose_year(message: Message, state: FSMContext):
    await state.update_data(year=int(message.text))
    await message.answer("Введите объём двигателя (куб.см):")
    await state.set_state(SearchCar.engine)

@dp.message(SearchCar.engine)
async def choose_engine(message: Message, state: FSMContext):
    await state.update_data(engine=int(message.text))
    await message.answer("Введите минимальную цену ($):")
    await state.set_state(SearchCar.min_price)

@dp.message(SearchCar.min_price)
async def choose_min_price(message: Message, state: FSMContext):
    await state.update_data(min_price=float(message.text))
    await message.answer("Введите максимальную цену ($):")
    await state.set_state(SearchCar.max_price)

@dp.message(SearchCar.max_price)
async def finish_search(message: Message, state: FSMContext):
    await state.update_data(max_price=float(message.text))
    data = await state.get_data()

    await message.answer("🔍 Ищу варианты на аукционах...")

    cars1 = await search_copart(data["brand"], data["model"], data["min_price"], data["max_price"])
    cars2 = await search_iaai(data["brand"], data["model"], data["min_price"], data["max_price"])
    cars = cars1 + cars2

    if not cars:
        await message.answer("❌ Ничего не найдено.")
        await state.clear()
        return

    text = f"🚗 {data['brand']} {data['model']}\n📍 Доставка: Алматы\n\n"

    for car in cars:
        auction_price = float(car["price"])

    total = calculate_total(
        auction_price_usd=auction_price,
        engine_cc=data["engine"],
        year=data["year"],
        miles_from_savannah=800,
        car_type="sedan"
    )

    caption = (
        f"🚗 {car['title']}\n"
        f"💰 Цена на аукционе: ${auction_price}\n"
        f"📦 Под ключ до Алматы: ${total}\n"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔎 Открыть лот", url=car["url"])]
        ]
    )

    # Если есть фото — отправляем фото
    if car.get("image"):
        await message.answer_photo(
            photo=car["image"],
            caption=caption,
            reply_markup=kb
        )
    else:
        await message.answer(
            caption,
            reply_markup=kb
        )


async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
