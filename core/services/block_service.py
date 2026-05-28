import datetime
from config.settings import BLOCK_CATEGORIES


def get_all_block_domains(blocklist: list[str], categories: list[str]) -> list[str]:
    domains = set(blocklist)
    for cat in categories:
        cat_data = BLOCK_CATEGORIES.get(cat, {})
        for d in cat_data.get("domains", []):
            domains.add(d)
    return sorted(domains)


def is_blocked(url: str, blocklist: list[str], categories: list[str]) -> tuple[bool, str]:
    all_domains = get_all_block_domains(blocklist, categories)
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname or ""
        hostname = hostname.replace("www.", "")
        for domain in all_domains:
            if hostname == domain or hostname.endswith("." + domain):
                cat = _find_category(domain, categories)
                return True, cat
    except Exception:
        pass
    return False, ""


def _find_category(domain: str, active_categories: list[str]) -> str:
    for cat in active_categories:
        cat_data = BLOCK_CATEGORIES.get(cat, {})
        if domain in cat_data.get("domains", []):
            return cat
    return "custom"


def get_category_label(category: str) -> str:
    cat_data = BLOCK_CATEGORIES.get(category)
    return cat_data["label"] if cat_data else category


def is_schedule_active(schedule_enabled: bool, start_time: str, end_time: str,
                       active_days: str) -> bool:
    """Check if blocking schedule is currently active."""
    if not schedule_enabled:
        return False

    now = datetime.datetime.now()

    day_map = {"0": 6, "1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5}
    current_weekday = now.weekday()  # 0=Monday

    scheduled_days = [d.strip() for d in active_days.split(",") if d.strip()]
    scheduled_weekdays = [day_map.get(d, -1) for d in scheduled_days]

    if current_weekday not in scheduled_weekdays:
        return False

    try:
        start_h, start_m = map(int, start_time.split(":"))
        end_h, end_m = map(int, end_time.split(":"))
    except (ValueError, AttributeError):
        return False

    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m
    current_minutes = now.hour * 60 + now.minute

    if start_minutes <= end_minutes:
        return start_minutes <= current_minutes <= end_minutes
    else:
        # Overnight schedule (e.g., 22:00-06:00)
        return current_minutes >= start_minutes or current_minutes <= end_minutes
