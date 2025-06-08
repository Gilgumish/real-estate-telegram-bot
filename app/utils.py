import re
from app.data import ads


def parse_price(price_str: str) -> int:
    return int(re.sub(r"[^\d]", "", price_str))


def parse_budget_range(budget_str: str) -> tuple:
    if "до" in budget_str:
        max_val = int(re.sub(r"[^\d]", "", budget_str))
        return (0, max_val)
    elif "понад" in budget_str:
        min_val = int(re.sub(r"[^\d]", "", budget_str))
        return (min_val + 1, float("inf"))
    else:
        # формат: "15 000–20 000 грн"
        numbers = list(map(int, re.findall(r"\d+", budget_str)))
        if len(numbers) == 2:
            return (numbers[0], numbers[1])
    return (0, float("inf"))  # fallback


def filter_ads(user_filters: dict) -> list:
    result = []

    for ad in ads:
        # фільтр по типу послуги
        if user_filters.get("service") and ad.get("type") != user_filters["service"]:
            continue

        # фільтр по кімнатах
        if user_filters.get("rooms") and ad["rooms"] not in user_filters["rooms"]:
            continue

        # фільтр по районах
        if user_filters.get("districts"):
            selected = [d.lower() for d in user_filters["districts"]]
            if ad["district"].lower() not in selected:
                continue

        # фільтр по бюджету
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
                continue

        result.append(ad)

    return result
