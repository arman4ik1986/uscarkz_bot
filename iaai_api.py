import aiohttp
from fake_useragent import UserAgent

ua = UserAgent()

BASE_URL = "https://www.iaai.com/Search/GetSearchResults"


async def search_iaai(brand: str, model: str, min_price: int, max_price: int):
    headers = {
        "User-Agent": ua.random,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.iaai.com/",
        "Origin": "https://www.iaai.com",
        "Content-Type": "application/json;charset=UTF-8"
    }

    payload = {
        "SearchKeyword": f"{brand} {model}",
        "PageNumber": 1,
        "PageSize": 10,
    }

    cars = []

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(BASE_URL, json=payload) as resp:

            # Если сайт отдал HTML вместо JSON — просто выходим
            if "application/json" not in resp.headers.get("Content-Type", ""):
                print("IAAI blocked request (HTML returned)")
                return []

            try:
                data = await resp.json()
            except Exception:
                print("IAAI invalid JSON")
                return []

            results = data.get("SearchResults", [])
            if not isinstance(results, list):
                return []

            for item in results:
                if not isinstance(item, dict):
                    continue

                year = item.get("Year")
                make = item.get("Make")
                model_name = item.get("Model")

                price = item.get("BuyNowPrice") or item.get("CurrentBid") or 0
                lot_id = item.get("StockNumber")

                if not lot_id:
                    continue

                cars.append({
                    "title": f"{year} {make} {model_name}",
                    "price": float(price) if price else 0,
                    "lot_id": lot_id,
                    "image": item.get("ImageUrl"),
                    "url": f"https://www.iaai.com/VehicleDetail/{lot_id}"
                })

    return cars
