import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import re
import plant_backend

class PlantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌿 Plant Tracker")
        self.geometry("800x600")
        self.configure(bg="#90bd9c")

        # Load plants
        self.plants = plant_backend.load_plants()

        # ─── Configure Main Window Responsiveness ─────────────────────────────
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # ─── Navigation Menu (Top Row) ────────────────────────────────────────
        menu = ttk.Frame(self)
        menu.grid(row=0, column=0, sticky="ew", pady=5, padx=10)
        # Remove column weight distribution so they don’t spread evenly
        menu.columnconfigure(0, weight=1)

        # Keep the buttons packed to the left
        ttk.Button(menu, text="Manage Plants", command=lambda: self.show_frame("AddPlantPage")).pack(side="left", padx=5)
        ttk.Button(menu, text="Water Plant", command=lambda: self.show_frame("WaterPlantPage")).pack(side="left", padx=5)
        ttk.Button(menu, text="View All Plants", command=lambda: self.show_frame("ShowPlantsPage")).pack(side="left", padx=5)

        # Exit button stays pinned to the right for balance
        ttk.Button(menu, text="Exit", command=self.quit).pack(side="right", padx=5)

        # ─── Container for Pages ───────────────────────────────────────────────
        container = ttk.Frame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}
        for F in (AddPlantPage, ShowPlantsPage, WaterPlantPage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("AddPlantPage")

    def show_frame(self, page_name):
        """Switch between pages"""
        frame = self.frames[page_name]
        if page_name == "ShowPlantsPage":
            frame.refresh_plants()
        elif page_name == "WaterPlantPage":
            frame.refresh_dropdown()
        frame.tkraise()

# ─── Add Plant Page ─────────────────────────────────────────────────────────────
class AddPlantPage(ttk.Frame):
    VALID_LIGHT_INTENSITY = ["Low", "Low-Medium", "Medium", "Medium-High", "High"]
    VALID_LIGHT_TYPE = ["Direct", "Indirect"]

    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="🌱 Manage Plants", font=("Helvetica", 20, "bold")).grid(row=0, column=0, pady=10)

        # Add Plant Card
        add_card = ttk.LabelFrame(self, text="Add a Plant", padding=15)
        add_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        add_card.columnconfigure(1, weight=1)

        self.entries = {}
        fields = [
            ("Common Name *", "common_name"),
            ("Scientific Name", "scientific_name"),
            ("Date Acquired (YYYY-MM-DD)", "date_acquired"),
            ("Humidity (0–1)", "min_humidity")
        ]

        for i, (label, key) in enumerate(fields):
            ttk.Label(add_card, text=label).grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(add_card)
            entry.grid(row=i, column=1, sticky="ew", pady=3)
            self.entries[key] = entry

        ttk.Label(add_card, text="Light Intensity").grid(row=4, column=0, sticky="w", pady=3)
        self.entries["light_intensity"] = ttk.Combobox(add_card, values=self.VALID_LIGHT_INTENSITY, state="readonly")
        self.entries["light_intensity"].grid(row=4, column=1, sticky="ew", pady=3)

        ttk.Label(add_card, text="Light Type").grid(row=5, column=0, sticky="w", pady=3)
        self.entries["light_type"] = ttk.Combobox(add_card, values=self.VALID_LIGHT_TYPE, state="readonly")
        self.entries["light_type"].grid(row=5, column=1, sticky="ew", pady=3)

        ttk.Button(add_card, text="Add Plant", command=self.add_plant).grid(row=6, column=0, columnspan=2, pady=(10, 0))

        # Remove Plant Card
        remove_card = ttk.LabelFrame(self, text="Remove a Plant", padding=15)
        remove_card.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        remove_card.columnconfigure(1, weight=1)

        ttk.Label(remove_card, text="Common Name:").grid(row=0, column=0, sticky="w", pady=3)
        self.remove_entry = ttk.Entry(remove_card)
        self.remove_entry.grid(row=0, column=1, sticky="ew", pady=3)
        ttk.Button(remove_card, text="Remove Plant", command=self.remove_plant).grid(row=0, column=2, padx=(5,0))

    def add_plant(self):
        # identical logic as your version
        plant_data = {key: entry.get().strip() for key, entry in self.entries.items()}
        if not plant_data["common_name"]:
            messagebox.showerror("Error", "Common name is required.")
            return
        date_str = plant_data["date_acquired"]
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Date must be YYYY-MM-DD.")
                return
        else:
            plant_data["date_acquired"] = None

        if plant_data["min_humidity"]:
            try:
                val = float(plant_data["min_humidity"])
                if not (0 <= val <= 1): raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Humidity must be between 0 and 1.")
                return
            plant_data["min_humidity"] = val
        else:
            plant_data["min_humidity"] = None

        try:
            self.controller.plants = plant_backend.add_plant_gui(self.controller.plants, plant_data)
            plant_backend.save_plants(self.controller.plants)
            messagebox.showinfo("Success", f"{plant_data['common_name'].upper()} added!")
            for e in self.entries.values(): e.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def remove_plant(self):
        name = self.remove_entry.get().strip().upper()
        if not name:
            messagebox.showerror("Error", "Enter a plant name.")
            return
        if name not in self.controller.plants:
            messagebox.showerror("Error", f"{name} not found.")
            return
        if messagebox.askyesno("Confirm", f"Remove {name}?"):
            self.controller.plants.pop(name)
            plant_backend.save_plants(self.controller.plants)
            self.remove_entry.delete(0, tk.END)
            messagebox.showinfo("Removed", f"{name} removed!")

class WaterPlantPage(ttk.Frame):
    """Dashboard-style page to water plants with separate cards for controls and info."""
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller

        # ── Page Header ─────────────────────────────
        ttk.Label(
            self,
            text="🌱 Water A Plant",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(10, 15))

        # ── Plant Selection Card ─────────────────────
        label = ttk.Label(self, text="🌿 Plant Selection", font=("Helvetica", 16, "bold"))
        control_card = ttk.LabelFrame(self, labelwidget=label, padding=15)
        control_card.pack(fill="x", padx=10, pady=(0, 15))

        ttk.Label(
            control_card,
            text="Choose a plant:",
            font=("Helvetica", 14, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(5,10))

        self.dropdown = ttk.Combobox(control_card, state="readonly", width=30)
        self.dropdown.grid(row=0, column=1, padx=(0,10))
        self.dropdown.bind("<<ComboboxSelected>>", self.update_display_info)

        ttk.Button(
            control_card,
            text="Water!",
            command=self.water_selected
        ).grid(row=0, column=2)
        control_card.columnconfigure(1, weight=1)

        # ── Watering Info Card ──────────────────────
        label_info = ttk.Label(self, text="🌿 Watering Information", font=("Helvetica", 16, "bold"))
        info_card = ttk.LabelFrame(self, labelwidget=label_info, padding=15)
        info_card.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.last_watered_label = ttk.Label(info_card, text="🗓️ Last Watered: —", font=("Helvetica", 14))
        self.last_watered_label.pack(anchor="w", pady=5)

        self.avg_label = ttk.Label(info_card, text="📊 Average Interval: —", font=("Helvetica", 14))
        self.avg_label.pack(anchor="w", pady=5)

        self.next_water_label = ttk.Label(info_card, text="🌞 Next Watering: —", font=("Helvetica", 14))
        self.next_water_label.pack(anchor="w", pady=5)

    def refresh_dropdown(self):
        """Reload plant names into dropdown and update info."""
        self.controller.plants = plant_backend.load_plants()
        plant_names = sorted(self.controller.plants.keys())
        self.dropdown["values"] = plant_names

        if plant_names:
            self.dropdown.current(0)
            self.update_display_info()
        else:
            self.last_watered_label.config(text="🗓️ Last Watered: —")
            self.avg_label.config(text="📊 Average Interval: —")
            self.next_water_label.config(text="🌞 Next Watering: —")

    def update_display_info(self, event=None):
        """Update watering info for the selected plant."""
        plant_name = self.dropdown.get().strip().upper()  # normalize to match backend
        if not plant_name:
            self.last_watered_label.config(text="🗓️ Last Watered: —")
            self.avg_label.config(text="📊 Average Interval: —")
            self.next_water_label.config(text="🌞 Next Watering: —")
            return

        plants = self.controller.plants
        info = plants.get(plant_name, {})

        # Last Watered
        last_watered = info.get("last_watered") or "No record"
        self.last_watered_label.config(text=f"🗓️ Last Watered: {last_watered}")

        # Average Interval
        avg_days = None
        try:
            avg_str = plant_backend.show_average_watering_gui(plants, plant_name)
            match = re.search(r"(\d+(\.\d+)?)", avg_str)  # extract number
            if match:
                avg_days = float(match.group(1))
            self.avg_label.config(text=f"📊 {avg_str.split(': ', 1)[-1]}")
        except ValueError:
            self.avg_label.config(text="📊 Not enough watering data yet.")

        # Next Watering
        if last_watered != "No record" and avg_days is not None:
            try:
                last_date = datetime.strptime(last_watered, "%Y-%m-%d")
                next_date = last_date + timedelta(days=round(avg_days))
                formatted = next_date.strftime("%Y-%m-%d")

                if next_date <= datetime.now():
                    self.next_water_label.config(
                        text=f"🔴 Next Watering: {formatted}"
                    )
                else:
                    self.next_water_label.config(text=f"🟢 Next Watering: {formatted}")
            except Exception:
                self.next_water_label.config(text="⚪ Next Watering: —")
        else:
            self.next_water_label.config(text=" Next Watering: —")

    def water_selected(self):
        """Water the selected plant and refresh info."""
        plant_name = self.dropdown.get()
        if not plant_name:
            messagebox.showerror("Error", "Please select a plant to water.")
            return

        try:
            self.controller.plants = plant_backend.water_plant_gui(self.controller.plants, plant_name)
            messagebox.showinfo("Success", f"{plant_name} watered today!")
            self.update_display_info()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

class ShowPlantsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        ttk.Label(self, text="🌱 All Plants", font=("Helvetica", 18, "bold")).pack(pady=10)

        # --- Sorting Controls ---
        sort_frame = ttk.Frame(self)
        sort_frame.pack(pady=5)

        ttk.Label(sort_frame, text="Sort by:").pack(side="left", padx=5)
        self.sort_option = ttk.Combobox(
            sort_frame,
            values=["Common name", "Minimum humidity", "Light intensity", "Date acquired", "Last watered", "Needs watering"],
            state="readonly",
            width=20
        )
        self.sort_option.current(0)
        self.sort_option.pack(side="left", padx=5)

        ttk.Label(sort_frame, text="Order:").pack(side="left", padx=5)
        self.sort_order = ttk.Combobox(
            sort_frame,
            values=["Ascending", "Descending"],
            state="readonly",
            width=12
        )
        self.sort_order.current(0)
        self.sort_order.pack(side="left", padx=5)

        ttk.Button(sort_frame, text="Apply Sort", command=self.sort_and_display).pack(side="left", padx=10)

        # --- Text Display ---
        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self.text_box = tk.Text(
            text_frame,
            wrap="word",
            font=("Courier", 14),
            yscrollcommand=scrollbar.set
        )
        self.text_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text_box.yview)

        ttk.Button(self, text="Refresh List", command=self.refresh_plants).pack(pady=5)

    def refresh_plants(self):
        """Reload and display all plants (alphabetically by default)."""
        self.controller.plants = plant_backend.load_plants()
        all_plants_str = plant_backend.show_all_plants_gui(self.controller.plants)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, all_plants_str)

    def sort_and_display(self):
        """Sort and display plants based on selected criteria."""
        sort_choice = self.sort_option.get()
        order_choice = self.sort_order.get()
        reverse = (order_choice == "Descending")

        sort_key_map = {
            "Common name": "common_name",
            "Minimum humidity": "min_humidity",
            "Light intensity": "light_intensity",
            "Date acquired": "date_acquired",
            "Last watered": "last_watered",
            "Needs watering": "needs_watering"
        }

        key = sort_key_map.get(sort_choice, "common_name")
        sorted_list = plant_backend.sort_plants_gui(self.controller.plants, sort_by=key, reverse=reverse)

        # --- Filter overdue plants if "Needs watering" is selected ---
        if key == "needs_watering":
            today = datetime.now()
            filtered_list = []
            for name, info in sorted_list:
                last = info.get("last_watered")
                history = info.get("watering_history", [])
                if last and len(history) >= 2:
                    dates = [datetime.strptime(d, "%Y-%m-%d") for d in history]
                    diffs = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
                    avg = sum(diffs) / len(diffs)
                    next_date = datetime.strptime(last, "%Y-%m-%d") + timedelta(days=avg)
                    if next_date <= today:
                        filtered_list.append((name, info))
            sorted_list = filtered_list
        # -------------------------------------------------------------

        self.text_box.delete(1.0, tk.END)
        if not sorted_list:
            self.text_box.insert(tk.END, "No plants found for this filter.\n")
            return

        for name, info in sorted_list:
            self.text_box.insert(
                tk.END,
                f"🍃 {name} ({info['scientific_name']})\n"
                f"   Date acquired: {info['date_acquired']}\n"
                f"   Last watered: {info['last_watered']}\n"
                f"   Light intensity: {info['light_intensity']}\n"
                f"   Light type: {info['light_type']}\n"
                f"   Minimum humidity: {info['min_humidity']}\n"
                f"   Notes: {info['notes']}\n\n"
            )

if __name__ == "__main__":
    app = PlantApp()
    app.mainloop()
