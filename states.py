from aiogram.fsm.state import StatesGroup, State


class SearchCar(StatesGroup):
    brand = State()
    model = State()
    year = State()
    engine = State()
    min_price = State()
    max_price = State()
