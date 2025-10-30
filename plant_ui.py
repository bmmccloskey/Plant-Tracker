import tkinter as tk
from tkinter import ttk, messagebox
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
        ttk.Button(menu, text="Add Plant", command=lambda: self.show_frame("AddPlantPage")).pack(side="left", padx=5)
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
        super().__init__(parent, padding=10)
        self.controller = controller
        self.pack_propagate(False)

        ttk.Label(self, text="🌱 Add A Plant", font=("Helvetica", 18, "bold")).pack(pady=10)

        # Main form container
        form = ttk.Frame(self)
        form.pack(pady=10, fill="both", expand=True)

        self.entries = {}

        # Common Name
        ttk.Label(form, text="Common name (required):").grid(row=0, column=0, sticky="w", pady=3)
        self.entries["common_name"] = ttk.Entry(form, width=40)
        self.entries["common_name"].grid(row=0, column=1, sticky="ew", pady=3)

        # Scientific Name
        ttk.Label(form, text="Scientific name:").grid(row=1, column=0, sticky="w", pady=3)
        self.entries["scientific_name"] = ttk.Entry(form, width=40)
        self.entries["scientific_name"].grid(row=1, column=1, sticky="ew", pady=3)

        # Date Acquired
        ttk.Label(form, text="Date acquired (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=3)
        self.entries["date_acquired"] = ttk.Entry(form, width=40)
        self.entries["date_acquired"].grid(row=2, column=1, sticky="ew", pady=3)

        # Light Intensity (optional)
        ttk.Label(form, text="Light intensity:").grid(row=4, column=0, sticky="w", pady=3)
        self.entries["light_intensity"] = ttk.Combobox(form, values=self.VALID_LIGHT_INTENSITY, state="readonly", width=37)
        self.entries["light_intensity"].grid(row=4, column=1, sticky="ew", pady=3)

        # Light Type (optional)
        ttk.Label(form, text="Light type:").grid(row=5, column=0, sticky="w", pady=3)
        self.entries["light_type"] = ttk.Combobox(form, values=self.VALID_LIGHT_TYPE, state="readonly", width=37)
        self.entries["light_type"].grid(row=5, column=1, sticky="ew", pady=3)

        # Humidity (optional)
        ttk.Label(form, text="Humidity (0–1):").grid(row=3, column=0, sticky="w", pady=3)
        self.entries["min_humidity"] = ttk.Entry(form, width=40)
        self.entries["min_humidity"].grid(row=3, column=1, sticky="ew", pady=3)

        # Centered "Add Plant" button
        button_frame = ttk.Frame(form)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(15, 0))
        ttk.Button(button_frame, text="Add Plant", command=self.add_plant).pack(anchor="center")

        # Allow proportional resizing
        form.columnconfigure(1, weight=1)

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

class WaterPlantPage(ttk.Frame):
    """Page to water plants and automatically show average watering info."""
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        ttk.Label(self, text="🌱 Water A Plant", font=("Helvetica", 18, "bold")).pack(pady=10)

        # Dropdown for selecting a plant
        self.dropdown = ttk.Combobox(self, state="readonly", width=40)
        self.dropdown.pack(pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.update_average_display)

        # Button to water plant
        ttk.Button(
            self,
            text="💧 Click here to water the selected plant!",
            command=self.water_selected
        ).pack(pady=5)

        # Label for showing average interval
        self.avg_label = ttk.Label(self, text="", font=("Helvetica", 14, "bold"))
        self.avg_label.pack(pady=20)

    def refresh_dropdown(self):
        """Refresh dropdown and average label."""
        self.controller.plants = plant_backend.load_plants()
        plant_names = sorted(self.controller.plants.keys())
        self.dropdown["values"] = plant_names

        if plant_names:
            self.dropdown.current(0)
            self.update_average_display()  # show average right away
        else:
            self.avg_label.config(text="No plants available.")

    def update_average_display(self, event=None):
        """Automatically update average watering info for selected plant."""
        plant_name = self.dropdown.get()
        if not plant_name:
            self.avg_label.config(text="")
            return

        try:
            avg_str = plant_backend.show_average_watering_gui(self.controller.plants, plant_name)
            self.avg_label.config(text=avg_str)
        except ValueError:
            self.avg_label.config(text="No watering data available for this plant yet.")

    def water_selected(self):
        """Water the selected plant and refresh average info."""
        plant_name = self.dropdown.get()
        if not plant_name:
            messagebox.showerror("Error", "Please select a plant to water.")
            return

        try:
            self.controller.plants = plant_backend.water_plant_gui(self.controller.plants, plant_name)
            messagebox.showinfo("Success", f"{plant_name} watered today!")
            self.update_average_display()  # update interval display immediately
        except ValueError as e:
            messagebox.showerror("Error", str(e))

class ShowPlantsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        ttk.Label(self, text="🌱 All Plants", font=("Helvetica", 18, "bold")).pack(pady=10)

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
        self.controller.plants = plant_backend.load_plants()
        all_plants_str = plant_backend.show_all_plants_gui(self.controller.plants)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, all_plants_str)

if __name__ == "__main__":
    app = PlantApp()
    app.mainloop()
