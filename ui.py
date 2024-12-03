import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data_handler import DataHandler
import csv


class WorkoutTrackerUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Workout Tracker")
        self.window.geometry("1200x800")

        # Modern Styling
        self.apply_modern_theme()

        # Data handler
        self.data_handler = DataHandler()
        self.workout_data = []  # Stores workout plan data

        # Default calculation method
        self.calculation_method = tk.StringVar(value="Total Method")

        # Setup UI
        self.setup_ui()

    def apply_modern_theme(self):
        style = ttk.Style()
        style.theme_use("clam")  # Modern theme
        style.configure("TLabel", font=("Arial", 12), padding=5)
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("TCombobox", font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
        style.map("Treeview", background=[("selected", "#a6c0ff")])

        self.window.configure(bg="#f0f0f0")  # Light grey background

    def setup_ui(self):
        sidebar = ttk.Frame(self.window, width=200)
        sidebar.pack(side="left", fill="y")

        main_content = ttk.Frame(self.window)
        main_content.pack(side="right", fill="both", expand=True)

        # Sidebar Buttons
        ttk.Button(sidebar, text="Workout Plan", command=self.show_workout_plan).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Weekly Summary", command=self.show_summary).pack(fill="x", pady=5)

        # Workout Plan
        self.workout_plan_frame = ttk.Frame(main_content)
        self.workout_tree = ttk.Treeview(self.workout_plan_frame,
                                         columns=('Routine', 'Exercise', 'Sets', 'Reps', 'RIR', 'Weight', 'Main', 'Secondary'),
                                         show='headings')
        for col in self.workout_tree['columns']:
            self.workout_tree.heading(col, text=col)
            self.workout_tree.column(col, width=100)
        self.workout_tree.pack(fill="both", expand=True)

        # Buttons for Workout Plan
        workout_buttons_frame = ttk.Frame(self.workout_plan_frame)
        workout_buttons_frame.pack(fill="x", pady=10)
        ttk.Button(workout_buttons_frame, text="Remove Selected", command=self.remove_selected_exercise).pack(side="left", padx=5)
        ttk.Button(workout_buttons_frame, text="Export to CSV", command=self.export_to_csv).pack(side="left", padx=5)

        # Weekly Summary
        self.summary_frame = ttk.Frame(main_content)

        # Calculation Method Dropdown
        ttk.Label(self.summary_frame, text="Calculation Method:").pack(side="top", pady=5)
        method_dropdown = ttk.Combobox(self.summary_frame, textvariable=self.calculation_method,
                                       values=["Total Method", "Fractional Method", "Direct Method"], state="readonly")
        method_dropdown.pack(side="top", pady=5)
        method_dropdown.bind("<<ComboboxSelected>>", lambda _: self.update_summary())

        # Summary Treeview
        self.summary_tree = ttk.Treeview(self.summary_frame,
                                         columns=('Muscle', 'Weekly Sets'),
                                         show='headings')
        for col in self.summary_tree['columns']:
            self.summary_tree.heading(col, text=col)
            self.summary_tree.column(col, width=150)
        self.summary_tree.pack(fill="both", expand=True)

        # Buttons and Inputs
        input_frame = ttk.Frame(main_content)
        input_frame.pack(fill="x", pady=10)
        self.create_input_fields(input_frame)

        self.show_workout_plan()

    def create_input_fields(self, frame):
        # Routine Dropdown
        ttk.Label(frame, text="Routine:").grid(row=0, column=0, padx=5, pady=5)
        self.routine_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.routine_var, values=["A1", "B1", "A2", "B2"]).grid(row=0, column=1, padx=5, pady=5)

        # Exercise Dropdown
        ttk.Label(frame, text="Exercise:").grid(row=0, column=2, padx=5, pady=5)
        self.exercise_var = tk.StringVar()
        self.exercise_combobox = ttk.Combobox(frame, textvariable=self.exercise_var, width=30)
        self.exercise_combobox['values'] = self.data_handler.get_exercise_names()
        self.exercise_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.exercise_combobox.bind("<<ComboboxSelected>>", self.update_muscle_groups)

        # Sets
        ttk.Label(frame, text="Sets:").grid(row=1, column=0, padx=5, pady=5)
        self.sets_var = tk.IntVar()
        ttk.Entry(frame, textvariable=self.sets_var).grid(row=1, column=1, padx=5, pady=5)

        # Rep Range
        ttk.Label(frame, text="Rep Range:").grid(row=1, column=2, padx=5, pady=5)
        self.rep_range_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.rep_range_var).grid(row=1, column=3, padx=5, pady=5)

        # RIR
        ttk.Label(frame, text="RIR:").grid(row=2, column=0, padx=5, pady=5)
        self.rir_var = tk.IntVar()
        ttk.Entry(frame, textvariable=self.rir_var).grid(row=2, column=1, padx=5, pady=5)

        # Weight
        ttk.Label(frame, text="Weight (KG):").grid(row=2, column=2, padx=5, pady=5)
        self.weight_var = tk.DoubleVar()
        ttk.Entry(frame, textvariable=self.weight_var).grid(row=2, column=3, padx=5, pady=5)

        # Add Exercise Button
        ttk.Button(frame, text="Add Exercise", command=self.add_exercise).grid(row=3, column=0, columnspan=4, pady=10)

    def update_muscle_groups(self, event=None):
        exercise = self.exercise_var.get()
        if exercise:
            main, secondary = self.data_handler.get_muscle_groups(exercise)
            self.main_muscle = main
            self.secondary_muscle = secondary

    def show_workout_plan(self):
        self.clear_frames()
        self.workout_plan_frame.pack(fill="both", expand=True)

    def show_summary(self):
        self.clear_frames()
        self.summary_frame.pack(fill="both", expand=True)
        self.update_summary()

    def clear_frames(self):
        self.workout_plan_frame.pack_forget()
        self.summary_frame.pack_forget()

    def add_exercise(self):
        if not self.exercise_var.get() or not self.sets_var.get() or not self.rep_range_var.get() or not self.weight_var.get():
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        entry = {
            "routine": self.routine_var.get(),
            "exercise": self.exercise_var.get(),
            "sets": self.sets_var.get(),
            "reps": self.rep_range_var.get(),
            "rir": self.rir_var.get(),
            "weight": self.weight_var.get(),
            "main_muscle": self.main_muscle,
            "secondary_muscle": self.secondary_muscle
        }
        self.workout_data.append(entry)
        self.update_workout_plan()

    def update_workout_plan(self):
        for item in self.workout_tree.get_children():
            self.workout_tree.delete(item)
        for entry in self.workout_data:
            self.workout_tree.insert('', 'end', values=tuple(entry.values()))

    def update_summary(self):
        # Clear the current summary
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)

        # Calculate total sets per muscle group
        muscle_summary = {}
        for entry in self.workout_data:
            main = entry['main_muscle']
            secondary = entry['secondary_muscle']
            sets = entry['sets']

            if main:
                if self.calculation_method.get() == "Total Method":
                    muscle_summary[main] = muscle_summary.get(main, 0) + sets
                    if secondary and secondary != "None":
                        muscle_summary[secondary] = muscle_summary.get(secondary, 0) + sets
                elif self.calculation_method.get() == "Fractional Method":
                    muscle_summary[main] = muscle_summary.get(main, 0) + sets
                    if secondary and secondary != "None":
                        muscle_summary[secondary] = muscle_summary.get(secondary, 0) + sets * 0.5
                elif self.calculation_method.get() == "Direct Method":
                    muscle_summary[main] = muscle_summary.get(main, 0) + sets

        # Update the summary treeview
        for muscle, sets in muscle_summary.items():
            self.summary_tree.insert('', 'end', values=(muscle, round(sets, 2)))

    def remove_selected_exercise(self):
        selected_item = self.workout_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an exercise to remove!")
            return
        for item in selected_item:
            index = self.workout_tree.index(item)
            self.workout_tree.delete(item)
            del self.workout_data[index]

    def export_to_csv(self):
        if not self.workout_data:
            messagebox.showwarning("Warning", "No data to export!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Routine", "Exercise", "Sets", "Reps", "RIR", "Weight", "Main Muscle", "Secondary Muscle"])
                for entry in self.workout_data:
                    writer.writerow(entry.values())
            messagebox.showinfo("Success", "Workout plan exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def run(self):
        self.window.mainloop()
