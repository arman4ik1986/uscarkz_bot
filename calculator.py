import pandas as pd
from datetime import datetime

USD_TO_KZT = 507

customs_df = pd.read_excel("istochnik_informacii_po_ts_01.01.2026_rus.xlsx")

# ===== ОЧИСТКА ДАННЫХ =====
customs_df["Engine"] = (
    customs_df["Engine"]
    .astype(str)
    .str.replace(" ", "")
    .str.replace(",", "")
)

customs_df["Engine"] = pd.to_numeric(customs_df["Engine"], errors="coerce")
customs_df["Year"] = pd.to_numeric(customs_df["Year"], errors="coerce")
customs_df["customs_value_usd"] = pd.to_numeric(customs_df["customs_value_usd"], errors="coerce")

customs_df = customs_df.dropna(subset=["Engine", "Year", "customs_value_usd"])

def get_customs_value(engine_cc, year):
    """
    Получаем таможенную стоимость из таблицы.
    Если точного года нет — уменьшаем на 15% за каждый год.
    """

    # Ищем строки с ближайшим объёмом двигателя
    df_engine = customs_df.iloc[(customs_df["Engine"] - engine_cc).abs().argsort()[:5]]

    # Ищем точное совпадение по году
    exact_year = df_engine[df_engine["Year"] == year]

    if not exact_year.empty:
        return float(exact_year.iloc[0]["customs_value_usd"])

    # Если года нет — берём ближайший год из таблицы
    closest_row = df_engine.iloc[(df_engine["Year"] - year).abs().argsort()[:1]].iloc[0]
    base_value = float(closest_row["customs_value_usd"])
    base_year = int(closest_row["Year"])

    year_diff = year - base_year

    # Если авто старше, уменьшаем на 15% за каждый год
    if year_diff < 0:
        depreciated = base_value * (0.85 ** abs(year_diff))
    else:
        depreciated = base_value  # если авто новее, не увеличиваем

    return depreciated


def calculate_total(
    auction_price_usd,
    engine_cc,
    year,
    miles_from_savannah,
    car_type  # sedan / crossover / suv / pickup
):
    current_year = datetime.now().year
    age = current_year - year

    # ===== Таможенная стоимость =====
    customs_value = get_customs_value(engine_cc, year)

    # ===== Доставка по США =====
    usa_delivery = miles_from_savannah * 1.2

    # ===== Морская доставка =====
    if car_type == "sedan":
        sea_shipping = 1300
    elif car_type == "crossover":
        sea_shipping = 1600
    else:  # suv / pickup
        sea_shipping = 1800

    georgia_delivery = 2000

    # ===== Акциз =====
    excise = 0
    if engine_cc > 3000:
        excise = (engine_cc - 3000) * 0.5  # можно заменить на точную ставку

    # ===== НДС 16% =====
    vat_base = customs_value + usa_delivery + sea_shipping + georgia_delivery + excise
    vat = vat_base * 0.16

    # ===== Утильсбор (тенге) =====
    if engine_cc <= 1000:
        recycling_kzt = 324_375
    elif engine_cc <= 2000:
        recycling_kzt = 756_875
    elif engine_cc <= 3000:
        recycling_kzt = 1_081_250
    else:
        recycling_kzt = 2_486_875

    # ===== Первичная регистрация =====
    if age <= 2:
        registration_kzt = 1_081.25
    elif age <= 3:
        registration_kzt = 216_250
    else:
        registration_kzt = 2_162_500

    # ===== Прочие расходы =====
    services_kzt = 370_000
    epts_kzt = 100_000

    # ===== Итог в долларах =====
    total_usd = (
        auction_price_usd +
        customs_value +
        usa_delivery +
        sea_shipping +
        georgia_delivery +
        excise +
        vat
    )

    # Добавляем тенговые платежи, переведённые в доллары
    total_usd += (recycling_kzt + registration_kzt + services_kzt + epts_kzt) / USD_TO_KZT

    return round(total_usd, 2)

# ===== БРЕНДЫ И МОДЕЛИ ИЗ EXCEL =====

def get_all_brands():
    if "Марка" not in customs_df.columns:
        raise ValueError("В Excel нет колонки 'Марка'")
    return sorted(customs_df["Марка"].dropna().astype(str).unique())


def get_models_by_brand(brand):
    if "Модель" not in customs_df.columns:
        raise ValueError("В Excel нет колонки 'Модель'")
    df = customs_df[customs_df["Марка"].astype(str) == str(brand)]
    return sorted(df["Модель"].dropna().astype(str).unique())

