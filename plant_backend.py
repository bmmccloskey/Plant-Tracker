import json
from datetime import datetime

DATA_FILE = "plants.json"

def load_plants():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # no file yet, return empty dict

def save_plants(plants):
    with open(DATA_FILE, "w") as f:
        json.dump(plants, f, indent=4)

# Fixed Options
VALID_LIGHT_INTENSITY = ["Low", "Low-Medium", "Medium", "Medium-High", "High"]
VALID_LIGHT_TYPE = ["Direct", "Indirect"]

def add_plant_gui(plants, plant_data):
    """
    Add a plant from a dictionary (used by GUI).
    `plant_data` should include keys:
        common_name, scientific_name, date_acquired,
        light_intensity, light_type, min_humidity, notes
    """
    common_name = plant_data.get("common_name", "").strip().upper()
    if not common_name:
        raise ValueError("Common name is required")

    if common_name in plants:
        raise ValueError(f"{common_name} already exists!")

    plants[common_name] = {
        "scientific_name": plant_data.get("scientific_name"),
        "date_acquired": plant_data.get("date_acquired"),
        "last_watered": None,
        "watering_history": [],
        "light_intensity": plant_data.get("light_intensity"),
        "light_type": plant_data.get("light_type"),
        "min_humidity": plant_data.get("min_humidity"),
        "notes": plant_data.get("notes")
    }

    # Keep dictionary sorted alphabetically
    plants = dict(sorted(plants.items(), key=lambda p: p[0].lower()))
    save_plants(plants)
    return plants

def water_plant_gui(plants, common_name):
    """
    Mark a plant as watered (for GUI use).
    Updates the 'last_watered' field and appends to watering history.
    Returns updated plants dictionary.
    """
    common_name = common_name.strip().upper()
    if common_name not in plants:
        raise ValueError(f"{common_name} not found.")

    today = datetime.now().strftime("%Y-%m-%d")
    plants[common_name]["last_watered"] = today
    plants[common_name]["watering_history"].append(today)

    save_plants(plants)
    return plants

def show_average_watering_gui(plants, common_name):
    """
    Return the average days between waterings as a string (for GUI display).
    """
    common_name = common_name.strip().upper()
    if common_name not in plants:
        raise ValueError(f"{common_name} not found.")

    history = plants[common_name]["watering_history"]

    if len(history) < 2:
        return f"🔴 {common_name}: Not enough watering data to calculate an average yet. 🔴"

    # Convert to datetime objects
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in history]
    differences = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    average_days = sum(differences) / len(differences)
    return f"📊 {common_name}: Average days between watering = {average_days:.1f} 📊"

def show_all_plants_gui(plants):
    """Return a formatted string of all plants"""
    if not plants:
        return "No plants added yet.\n"

    result = ""
    for name, info in plants.items():
        result += f"🍃 {name} ({info['scientific_name']})\n"
        result += f"   Date acquired: {info['date_acquired']}\n"
        result += f"   Last watered: {info['last_watered']}\n"
        result += f"   Light intensity: {info['light_intensity']}\n"
        result += f"   Light type: {info['light_type']}\n"
        result += f"   Minimum humidity: {info['min_humidity']}\n"
        result += f"   Notes: {info['notes']}\n\n"
    return result