import aiohttp
from fake_useragent import UserAgent

BASE_URL = "https://www.copart.com/public/lots/search"

ua = UserAgent()

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://www.copart.com",
    "referer": "https://www.copart.com/",
}


async def search_copart(brand: str, model: str, min_price: int, max_price: int):
    headers = HEADERS.copy()
    headers["user-agent"] = ua.random

    payload = {
        "filter": {
            "make": [brand.upper()],
            "model": [model.upper()],
            "saleStatus": ["onSale"],
            "vehicleTypeCode": ["VEHICLE"],
            "buyNowAmount": {
                "from": min_price,
                "to": max_price
            }
        },
        "sort": [{"field": "auctionDate", "direction": "asc"}],
        "page": 0,
        "size": 10
    }

    cars = []

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(BASE_URL, json=payload) as resp:
            try:
                data = await resp.json(content_type=None)
            except Exception:
                print("Copart returned invalid JSON")
                return []
            if "application/json" not in resp.headers.get("Content-Type", ""):
                print("Copart blocked request (HTML returned)")
                return []

            if not isinstance(data, dict):
                print("Copart response is not a dict")
                return []

            results = data.get("data", {}).get("results", [])

            if not isinstance(results, list):
                print("Copart results is not a list")
                return []

            for lot in results:
                if not isinstance(lot, dict):
                    continue

                year = lot.get("year")
                make = lot.get("make")
                model_name = lot.get("model")

                if not year or not make or not model_name:
                    continue

                price = lot.get("buyNowAmount") or lot.get("currentBid") or 0
                lot_id = lot.get("lotNumberStr")
                image = lot.get("imageThumbnailUrl")

                if not lot_id:
                    continue

                cars.append({
                    "title": f"{year} {make} {model_name}",
                    "price": float(price) if price else 0,
                    "lot_id": lot_id,
                    "image": image,
                    "url": f"https://www.copart.com/lot/{lot_id}"
                })

    return cars
