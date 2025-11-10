import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import re
import plant_backend  # your backend

class PlantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌿 Plant Tracker")
        self.geometry("700x500")
        self.configure(bg="#90bd9c")

        # Load plants from JSON
        self.plants = plant_backend.load_plants()

        # Navigation buttons
        menu = ttk.Frame(self)
        menu.pack(side="top", fill="x", pady=5)
        ttk.Button(menu, text="Manage Plants", command=lambda: self.show_frame("AddPlantPage")).pack(side="left", padx=5)
        ttk.Button(menu, text="Water Plant", command=lambda: self.show_frame("WaterPlantPage")).pack(side="left", padx=5)
        ttk.Button(menu, text="View All Plants", command=lambda: self.show_frame("ShowPlantsPage")).pack(side="left", padx=5)
       
        ttk.Button(menu, text="Exit", command=self.quit).pack(side="right", padx=5)

        # Container for pages
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        
         # Make window resize dynamically
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.grid_propagate(False)

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

class AddPlantPage(ttk.Frame):
    VALID_LIGHT_INTENSITY = ["Low", "Low-Medium", "Medium", "Medium-High", "High"]
    VALID_LIGHT_TYPE = ["Direct", "Indirect"]

    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.pack_propagate(False)

        ttk.Label(self, text="🌱 Manage Plants", font=("Helvetica", 20, "bold")).pack(pady=10)

        # --- Add Plant Section ---
        add_card = ttk.LabelFrame(self, text="Add a Plant", padding=15)
        add_card.pack(fill="x", padx=10, pady=(0, 15))

        self.entries = {}

        # Common Name
        ttk.Label(add_card, text="Common Name *").grid(row=0, column=0, sticky="w", pady=3)
        self.entries["common_name"] = ttk.Entry(add_card, width=40)
        self.entries["common_name"].grid(row=0, column=1, sticky="ew", pady=3)

        # Scientific Name
        ttk.Label(add_card, text="Scientific Name").grid(row=1, column=0, sticky="w", pady=3)
        self.entries["scientific_name"] = ttk.Entry(add_card, width=40)
        self.entries["scientific_name"].grid(row=1, column=1, sticky="ew", pady=3)

        # Date Acquired
        ttk.Label(add_card, text="Date Acquired (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=3)
        self.entries["date_acquired"] = ttk.Entry(add_card, width=40)
        self.entries["date_acquired"].grid(row=2, column=1, sticky="ew", pady=3)

        # Humidity
        ttk.Label(add_card, text="Humidity (0–1)").grid(row=3, column=0, sticky="w", pady=3)
        self.entries["min_humidity"] = ttk.Entry(add_card, width=40)
        self.entries["min_humidity"].grid(row=3, column=1, sticky="ew", pady=3)

        # Light Preferences (aligned)
        ttk.Label(add_card, text="Light Intensity").grid(row=4, column=0, sticky="w", pady=3)
        self.entries["light_intensity"] = ttk.Combobox(add_card, values=self.VALID_LIGHT_INTENSITY, state="readonly", width=37)
        self.entries["light_intensity"].grid(row=4, column=1, sticky="ew", pady=3)

        ttk.Label(add_card, text="Light Type").grid(row=5, column=0, sticky="w", pady=3)
        self.entries["light_type"] = ttk.Combobox(add_card, values=self.VALID_LIGHT_TYPE, state="readonly", width=37)
        self.entries["light_type"].grid(row=5, column=1, sticky="ew", pady=3)

        # Add Plant Button
        ttk.Button(add_card, text="Add Plant", command=self.add_plant).grid(row=6, column=0, columnspan=2, pady=(10,0))

        add_card.columnconfigure(1, weight=1)

        # --- Remove Plant Section ---
        remove_card = ttk.LabelFrame(self, text="Remove a Plant", padding=15)
        remove_card.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(remove_card, text="Common Name:").grid(row=0, column=0, sticky="w", pady=3)
        self.remove_entry = ttk.Entry(remove_card, width=40)
        self.remove_entry.grid(row=0, column=1, sticky="ew", padx=(0,5), pady=3)

        ttk.Button(remove_card, text="Remove Plant", command=self.remove_plant).grid(row=0, column=2, padx=(5,0))
        remove_card.columnconfigure(1, weight=1)

    def add_plant(self):
        plant_data = {key: entry.get().strip() for key, entry in self.entries.items()}

        # Validate Common Name
        if not plant_data["common_name"]:
            messagebox.showerror("Error", "Common name is required.")
            return

        # Light intensity and type are optional — if blank, set to None
        if plant_data["light_intensity"] not in self.VALID_LIGHT_INTENSITY:
            plant_data["light_intensity"] = None
        if plant_data["light_type"] not in self.VALID_LIGHT_TYPE:
            plant_data["light_type"] = None

        # Humidity is optional
        if plant_data["min_humidity"]:
            try:
                plant_data["min_humidity"] = float(plant_data["min_humidity"])
                if not (0 <= plant_data["min_humidity"] <= 1):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Humidity must be a number between 0 and 1.")
                return
        else:
            plant_data["min_humidity"] = None

        # Add plant using backend
        try:
            self.controller.plants = plant_backend.add_plant_gui(self.controller.plants, plant_data)
            messagebox.showinfo("Success", f"{plant_data['common_name']} added successfully!")
            for entry in self.entries.values():
                entry.delete(0, tk.END)  # clear fields
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def remove_plant(self):
        common_name = self.remove_entry.get().strip().upper()
        if not common_name:
            messagebox.showerror("Error", "Please enter the common name of the plant to remove.")
            return
        if common_name not in self.controller.plants:
            messagebox.showerror("Error", f"{common_name} not found.")
            return

        confirm = messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove {common_name}?")
        if confirm:
            self.controller.plants.pop(common_name)
            plant_backend.save_plants(self.controller.plants)
            self.remove_entry.delete(0, tk.END)
            messagebox.showinfo("Removed", f"{common_name} removed successfully!")

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
                self.next_water_label.config(text="🟢 Next Watering: —")
        else:
            self.next_water_label.config(text="🟢 Next Watering: —")

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
            values=["Common name", "Minimum humidity", "Light intensity", "Date acquired", "Last watered"],
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

        # Map user-friendly labels to backend keys
        sort_key_map = {
            "Common name": "common_name",
            "Minimum humidity": "min_humidity",
            "Light intensity": "light_intensity",
            "Date acquired": "date_acquired",
            "Last watered": "last_watered"
        }

        key = sort_key_map.get(sort_choice, "common_name")
        sorted_list = plant_backend.sort_plants_gui(self.controller.plants, sort_by=key, reverse=reverse)

        if not sorted_list:
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, "No plants found.")
            return

        # Display sorted results
        self.text_box.delete("1.0", tk.END)
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
