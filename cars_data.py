import pandas as pd

cars_df = pd.read_excel("istochnik_informacii_po_ts_01.01.2026_rus.xlsx")

# Приводим к строкам и чистим
cars_df["Марка"] = cars_df["Марка"].astype(str).str.strip()
cars_df["Модель"] = cars_df["Модель"].astype(str).str.strip()
cars_df["Тип ТС"] = cars_df["Тип ТС"].astype(str).str.strip()

def get_brands(body_type: str):
    brands = (
        cars_df[cars_df["Тип ТС"].str.lower() == body_type.lower()]["Марка"]
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(brands)


def get_models(body_type: str, brand: str):
    models = (
        cars_df[
            (cars_df["Тип ТС"].str.lower() == body_type.lower()) &
            (cars_df["Марка"].str.lower() == brand.lower())
        ]["Модель"]
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(models)
