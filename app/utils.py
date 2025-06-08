import re
from app.data import ads

EN_TO_UK_DISTRICTS = {
    "center": "Центр",
    "lukyanivka": "Лук’янівка",
    "pozniaky": "Позняки",
    "obolon": "Оболонь",
    "troieshchyna": "Троєщина",
    "darnytsia": "Дарниця",
    "holosiiv": "Голосієво",
    "shuliavka": "Шулявка",
}

def normalize_district(name: str) -> str:
    key = name.lower()
    return EN_TO_UK_DISTRICTS.get(key, name)

def parse_price(price_str: str) -> int:
    return int(re.sub(r"[^\d]", "", price_str))

def parse_budget_range(budget_str: str) -> tuple:
    text = budget_str.lower()
    numbers = list(map(int, re.findall(r"\d+", budget_str)))
    multiplier = 1000 if "тис" in text or "k" in text else 1

    if "до" in text or "up to" in text:
        max_val = numbers[0] * multiplier
        return (0, max_val)
    elif "понад" in text or "+" in text:
        min_val = numbers[0] * multiplier
        return (min_val + 1, float("inf"))
    elif len(numbers) == 2:
        return (numbers[0] * multiplier, numbers[1] * multiplier)

    return (0, float("inf"))

def filter_ads(user_filters: dict) -> list:
    result = []

    print("🔍 Вхідні фільтри:", user_filters)
    for ad in ads:
        print("➡️ Перевірка оголошення:", ad)

        if user_filters.get("service") and ad.get("type") != user_filters["service"]:
            print("✖️ Пропущено через 'service'")
            continue

        if user_filters.get("rooms") and str(ad["rooms"]) not in user_filters["rooms"]:
            print("✖️ Пропущено через 'rooms'")
            continue

        if user_filters.get("districts"):
            selected = [normalize_district(d) for d in user_filters["districts"]]
            if ad["district"] not in selected:
                print("✖️ Пропущено через 'district'")
                continue

        price = parse_price(ad["price"])
        budget_filters = user_filters.get("budget", [])

        if budget_filters:
            matched = False
            for b in budget_filters:
                min_b, max_b = parse_budget_range(b)
                if min_b <= price <= max_b:
                    matched = True
                    break
            if not matched:
                print("✖️ Пропущено через 'budget'")
                continue

        print("✅ Додано до результатів")
        result.append(ad)

    print("🎯 Знайдено:", len(result))
    return result

