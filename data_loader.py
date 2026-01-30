import pandas as pd

# Загружаем таблицу ТС
customs_df = pd.read_excel("istochnik_informacii_po_ts_01.01.2026_rus.xlsx")

# Приводим названия колонок к удобному виду (если в файле по-русски)
customs_df.columns = [c.strip() for c in customs_df.columns]

# Ожидаемые колонки (проверь названия в Excel!):
# "Марка", "Модель", "Engine", "Price"

def get_all_brands():
    return sorted(customs_df["Марка"].dropna().unique())

def get_models_by_brand(brand):
    df = customs_df[customs_df["Марка"] == brand]
    return sorted(df["Модель"].dropna().unique())
