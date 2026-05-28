from config.settings import PLANT_TYPES
from core.repositories.session_repo import plant_seed, water_plant, get_plants, get_garden_stats


def get_random_position() -> tuple[float, float]:
    import random
    return random.uniform(0.05, 0.9), random.uniform(0.05, 0.85)


def create_new_plant(plant_type: str = "tree", name: str | None = None) -> str:
    pt = PLANT_TYPES.get(plant_type)
    if not pt:
        plant_type = "tree"
        pt = PLANT_TYPES["tree"]

    xp_needed = pt["xp_per_stage"][0]
    x, y = get_random_position()
    return plant_seed(plant_type, xp_needed, x, y, name)


def water_on_session(session_minutes: int, plant_type: str | None = None) -> dict:
    """Called after a completed session. Distributes XP to plants."""
    xp_per_session = session_minutes * 2
    plants = get_plants()

    if not plants:
        return {"plants_watered": 0, "plants_leveled": 0, "total_xp": xp_per_session}

    active = [p for p in plants if p["stage"] < 4]
    if not active:
        return {"plants_watered": 0, "plants_leveled": 0, "total_xp": 0}

    if plant_type:
        active = [p for p in active if p["plant_type"] == plant_type]

    xp_each = max(1, xp_per_session // len(active))
    watered = 0
    leveled = 0

    for plant in active:
        result = water_plant(plant["id"], xp_each)
        if result:
            watered += 1
            if result.get("leveled_up"):
                leveled += 1

    return {"plants_watered": watered, "plants_leveled": leveled, "total_xp": xp_per_session}


def get_garden_status() -> dict:
    plants = get_plants()
    stats = get_garden_stats()

    plant_data = []
    for p in plants:
        pt = PLANT_TYPES.get(p["plant_type"], PLANT_TYPES["tree"])
        stage_icon = pt["stages"][min(p["stage"], 4)]
        plant_data.append({
            "id": p["id"],
            "type": p["plant_type"],
            "name": p["name"] or "Tanaman",
            "stage": p["stage"],
            "xp": p["xp"],
            "xp_required": p["xp_required"],
            "icon": stage_icon,
            "plant_type_name": pt["name"],
            "position_x": p["position_x"],
            "position_y": p["position_y"],
            "planted_date": p["planted_date"],
        })

    return {"plants": plant_data, "total": stats["total_plants"], "full_grown": stats["full_grown"]}
