import requests

CBU_JSON_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"

def get_cbu_rates():
    r = requests.get(CBU_JSON_URL, timeout=10)
    r.raise_for_status()
    data = r.json()

    out = {}
    for item in data:
        code = item.get("Ccy")
        rate = item.get("Rate")
        date = item.get("Date")
        if code in ("USD", "EUR"):
            out[code] = {"rate": float(rate), "date": date}
    return out
