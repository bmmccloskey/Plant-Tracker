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

def add_plant(plants):
    # Common name is required
    common_name = input("Common name (required): ").strip().upper()
    if not common_name:
        print("Common name cannot be empty.\n")
        return
    
    if common_name in plants:
        print(f"{common_name} already exists!\n")
        return

    # Optional fields
    scientific_name = input("Scientific name (optional): ").strip() or None
    date_acquired = input("Date acquired (YYYY-MM-DD, optional): ").strip() or None

    # Light intensity
    while True:
        light_intensity = input(f"Light intensity: {', '.join(VALID_LIGHT_INTENSITY)} (optional): ").strip().title()
        if light_intensity == "":
            light_intensity = None
            break
        elif light_intensity in VALID_LIGHT_INTENSITY:
            break
        else:
            print("Invalid option. Try again.")

    # Light type3
    while True:
        light_type = input(f"Light type: {', '.join(VALID_LIGHT_TYPE)} (optional): ").strip().title()
        if light_type == "":
            light_type = None
            break
        elif light_type in VALID_LIGHT_TYPE:
            break
        else:
            print("Invalid option. Try again.")

    # Minimum humidity
    while True:
        min_humidity_input = input("Minimum humidity (0-1, optional): ").strip()
        if min_humidity_input == "":
            min_humidity = None
            break
        try:
            min_humidity = float(min_humidity_input)
            if 0 <= min_humidity <= 1:
                break
            else:
                print("Enter a number between 0 and 1.")
        except ValueError:
            print("Enter a valid number.")

    notes = input("Notes (optional): ").strip() or None

    # Create the plant entry
    plants[common_name] = {
        "scientific_name": scientific_name,
        "date_acquired": date_acquired,
        "last_watered": None,
        "watering_history": [],
        "light_intensity": light_intensity,
        "light_type": light_type,
        "min_humidity": min_humidity,
        "notes": notes
    }

    # Make sure plants in dictionary are sorted alphabetically by common name
    plants = dict(sorted(plants.items(), key=lambda p: p[0].lower()))

    save_plants(plants)
    print(f"{common_name} added!\n")

def water_plant(plants):
    common_name = input("Which plant did you water? ").strip().upper()
    if common_name not in plants:
        print("Plant not found.")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    plants[common_name]["last_watered"] = today
    plants[common_name]["watering_history"].append(today)
    
    save_plants(plants)
    print(f"{common_name} watered today.\n")

def show_average_watering(plants):
    if not plants:
        print("No plants added yet.\n")
        return

    common_name = input("Enter the plant's common name: ").strip().upper()
    
    if common_name not in plants:
        print("Plant not found.\n")
        return

    history = plants[common_name]["watering_history"]

    if len(history) < 2:
        print(f"{common_name}: Not enough watering data to calculate average.\n")
        return

    # Convert string dates to datetime objects
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in history]

    # Calculate differences between consecutive dates
    differences = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]

    # Calculate average
    average_days = sum(differences) / len(differences)

    # (1f formats to 1 decimal place)
    print(f"{common_name}: Average days between watering = {average_days:.1f}\n")

def show_all_plants(plants):
    if not plants:
        print("No plants added yet.\n")
        return

    for name, info in plants.items():
        print(f"\n🍃 {name} ({info['scientific_name']})")
        print(f"   Date acquired: {info['date_acquired']}")
        print(f"   Last watered: {info['last_watered']}")
        print(f"   Light intensity: {info['light_intensity']}")
        print(f"   Light type: {info['light_type']}")
        print(f"   Minimum humidity: {info['min_humidity']}")
        print(f"   Notes: {info['notes']}")
    print()

def show_plant(plants):
    if not plants:
        print("No plants added yet.\n")
        return

    common_name = input("Enter the plant's common name: ").strip().upper()
    if common_name not in plants:
        print("Plant not found.\n")
        return

    info = plants[common_name]
    print(f"\n🍃 {common_name} ({info['scientific_name']})")
    print(f"   Date acquired: {info['date_acquired']}")
    print(f"   Last watered: {info['last_watered']}")
    print(f"   Light intensity: {info['light_intensity']}")
    print(f"   Light type: {info['light_type']}")
    print(f"   Minimum humidity: {info['min_humidity']}")
    print(f"   Notes: {info['notes']}\n")

def sort_plants(plants):
    if not plants:
        print("No plants to sort.\n")
        return

    print("\nSort plants by:")
    print("1. Minimum humidity")
    print("2. Light intensity")
    print("3. Date acquired")
    print("4. Last watered")
    print("5. Cancel")
    print()

    choice = input("Choose an option: ").strip()

    # Define sorting key and default direction
    if choice == "1":
        key_func = lambda p: p[1]["min_humidity"] or 0
        sort_type = "Minimum humidity"
    elif choice == "2":
        order = ["Low", "Low-Medium", "Medium", "Medium-High", "High"]
        key_func = lambda p: order.index(p[1]["light_intensity"]) if p[1]["light_intensity"] in order else -1
        sort_type = "Light intensity"
    elif choice == "3":
        key_func = lambda p: datetime.strptime(p[1]["date_acquired"], "%Y-%m-%d")
        sort_type = "Date acquired"
    elif choice == "4":
        key_func = lambda p: datetime.strptime(p[1]["last_watered"], "%Y-%m-%d")
        sort_type = "Last watered"
    else:
        print("Sorting canceled.\n")
        return

    # Let user choose sort direction
    order_choice = input("Sort ascending (A) or descending (D)? [A/D]: ").strip().upper()
    reverse = order_choice == "D"

    # Ask if user wants to limit results
    limit_input = input("\nEnter the number of plants to display (or press Enter to show all): ").strip()
    limit = int(limit_input) if limit_input.isdigit() else None

    sorted_list = sorted(plants.items(), key=key_func, reverse=reverse)

    if limit is not None:
        sorted_list = sorted_list[:limit]

    print(f"\n🌿 Plants sorted by {sort_type} ({'descending' if reverse else 'ascending'}):")
    for name, info in sorted_list:
        print(f"- {name} (Humidity: {info['min_humidity']}, Light: {info['light_intensity']}, "
              f"Acquired: {info['date_acquired']}, Last watered: {info['last_watered']})")
    print()

def delete_plant(plants):
    if not plants:
        print("No plants to delete.\n")
        return

    common_name = input("Enter the plant's common name to delete: ").strip().upper()
    if common_name in plants:
        confirm = input(f"Are you sure you want to delete {common_name}? (Y/N): ").strip().upper()
        if confirm == "Y":
            del plants[common_name]
            save_plants(plants)
            print(f"{common_name} has been deleted.\n")
        else:
            print("Deletion canceled.\n")
    else:
        print("Plant not found.\n")

def clean_list(plants):
    if not plants:
        print("No plants to delete.\n")
        return

    confirm = input("Are you sure you want to delete ALL plants? (Y/N): ").strip().upper()
    if confirm == "Y":
        plants.clear()
        save_plants(plants)
        print("All plants have been deleted.\n")
    else:
        print("Deletion canceled.\n")

def help_menu(plants):
    print("----------------------------")
    print("| 🌱 Plant Tracker Menu 🌱 |")
    print("----------------------------")
    print("1. Add a new plant -> add")
    print("2. Show a plant -> show plant")
    print("3. Show ALL plants -> show all")
    print("4. Water a plant -> water")
    print("5. Show plant watering schedule -> show waterings")
    print("6. Sort plants -> sort")
    print("7. Remove a plant -> remove")
    print("8. Reset plant tracker -> reset")
    print("9. Exit program -> exit")
    print("10. Show help menu -> help")


def main():
    plants = load_plants()  # Load existing plants from JSON
    print("-------------------------------------")
    print("| 🌱 Welcome to Plant Tracker!!! 🌱 |")
    print("-------------------------------------")

    while True:

        choice = input("\nChoose an option: ").strip().upper()
        print()

        if choice == "1" or choice == "ADD":
            add_plant(plants)
        elif choice == "2" or choice == "SHOW PLANT":
            show_plant(plants)
        elif choice == "3" or choice == "SHOW ALL":
            show_all_plants(plants)
        elif choice == "4" or choice == "WATER":
            water_plant(plants)
        elif choice == "5" or choice == "SHOW WATERINGS":
            show_average_watering(plants)
        elif choice == "6" or choice == "SORT":
            sort_plants(plants)
        elif choice == "7" or choice == "REMOVE":
            delete_plant(plants)
        elif choice == "8" or choice == "RESET":
            clean_list(plants)
        elif choice == "9" or choice == "EXIT" or choice == "DONE":
            print("Thanks and goodbye!!! 🌻")
            break
        elif choice == "10" or choice == "HELP":
            help_menu(plants)
        else:
            print("Invalid choice, please try again.\n")

if __name__ == "__main__":
    main()