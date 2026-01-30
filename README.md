
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "8024944878:AAEXjUgJe-nq-j7wDHYzJ7x1pZ9jdaZDokE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== КУРС ДОЛЛАРА (можешь менять) ======
USD_TO_KZT = 480

# ====== СОСТОЯНИЯ ======
class CalcCar(StatesGroup):
    price = State()
    engine = State()
    year = State()

# ====== КНОПКИ ======
kb_start = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Рассчитать авто")]],
    resize_keyboard=True
)

# ====== СТАРТ ======
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🚗 Бот расчёта авто из США в Казахстан\n\nНажми кнопку ниже 👇",
        reply_markup=kb_start
    )

# ====== ЗАПУСК РАСЧЁТА ======
@dp.message(F.text == "Рассчитать авто")
async def calc_start(message: Message, state: FSMContext):
    await message.answer("Введите цену автомобиля на аукционе в $:")
    await state.set_state(CalcCar.price)

# ====== ЦЕНА АВТО ======
@dp.message(CalcCar.price)
async def get_price(message: Message, state: FSMContext):
    await state.update_data(price=float(message.text))
    await message.answer("Объём двигателя (например 2.0):")
    await state.set_state(CalcCar.engine)

# ====== ДВИГАТЕЛЬ ======
@dp.message(CalcCar.engine)
async def get_engine(message: Message, state: FSMContext):
    await state.update_data(engine=float(message.text))
    await message.answer("Год выпуска авто:")
    await state.set_state(CalcCar.year)

# ====== ГОД И РАСЧЁТ ======
@dp.message(CalcCar.year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=int(message.text))
    data = await state.get_data()

    price = data["price"]
    engine = data["engine"]
    year = data["year"]

    # ==== ПРИМЕРНЫЕ РАСХОДЫ ====
    usa_delivery = 600
    sea_shipping = 1500
    broker = 500

    # Примерная растаможка (упрощённая логика)
    customs = price * 0.15

    total_usd = price + usa_delivery + sea_shipping + broker + customs
    total_kzt = total_usd * USD_TO_KZT

    await message.answer(
        f"📊 Предварительный расчёт:\n\n"
        f"💰 Цена авто: ${price:,.0f}\n"
        f"🚚 Доставка по США: ${usa_delivery}\n"
        f"🚢 Доставка морем: ${sea_shipping}\n"
        f"🧾 Растаможка (примерно): ${customs:,.0f}\n"
        f"🤝 Услуги: ${broker}\n\n"
        f"✅ ИТОГО: ${total_usd:,.0f}\n"
        f"🇰🇿 В тенге: {total_kzt:,.0f} ₸"
    )

    await state.clear()

# ====== ЗАПУСК БОТА ======
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
