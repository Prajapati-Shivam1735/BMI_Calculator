import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from statistics import mean

# ---------------- Database Connection ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="bmi_user",
        password="server",
        database="bmi_calc"
    )

# ---------------- BMI Logic ----------------
def calculate_bmi(weight, height, unit_system):
    """Calculate BMI in metric or imperial units."""
    return (weight / height ** 2) if unit_system == "Metric" else (weight / height ** 2) * 703

def classify_bmi(bmi):
    """Classify BMI category."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obesity"

def save_bmi(username, weight, height, bmi, category, unit_system):
    """Save BMI record to database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bmi_records (username, weight, height, bmi, category, unit_system, date)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (username, weight, height, bmi, category, unit_system, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()

def fetch_user_history(username):
    """Fetch BMI records for a user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT date,bmi,category FROM bmi_records WHERE username=%s ORDER BY date ASC", (username,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fetch_average_bmi():
    """Fetch average BMI per day."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DATE(date), AVG(bmi)
        FROM bmi_records
        GROUP BY DATE(date)
        ORDER BY DATE(date)
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ---------------- GUI Setup ----------------
root = tb.Window(themename="cyborg")
root.title("BMI Dashboard")
root.geometry("950x550")

# Sidebar
sidebar = ttk.Frame(root, bootstyle=SECONDARY)
sidebar.pack(side=LEFT, fill=Y)

menu_label = ttk.Label(sidebar, text=" BMI Dashboard", bootstyle=INVERSE, font=("Segoe UI", 14, "bold"))
menu_label.pack(pady=20)

current_theme = "cyborg"
def toggle_theme():
    global current_theme
    new_theme = "flatly" if current_theme == "cyborg" else "cyborg"
    root.style.theme_use(new_theme)
    current_theme = new_theme

def highlight_button(active_btn):
    for btn in sidebar.winfo_children():
        if isinstance(btn, ttk.Button):
            btn.configure(bootstyle=SECONDARY)
    active_btn.configure(bootstyle=INFO)

# Main content frame
main_frame = ttk.Frame(root, padding=30)
main_frame.pack(fill=BOTH, expand=True)

# ---------------- Views ----------------
def clear_main_frame():
    """Remove all widgets from the main frame."""
    for widget in main_frame.winfo_children():
        widget.destroy()

def show_home():
    highlight_button(home_btn)
    clear_main_frame()

    title_label = ttk.Label(main_frame, text="BMI Calculator", font=("Segoe UI", 20, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=E, pady=5)
    username_entry = ttk.Entry(main_frame, width=25)
    username_entry.grid(row=1, column=1, pady=5)

    ttk.Label(main_frame, text="Weight:").grid(row=2, column=0, sticky=E, pady=5)
    weight_entry = ttk.Entry(main_frame, width=25)
    weight_entry.grid(row=2, column=1, pady=5)

    ttk.Label(main_frame, text="Height:").grid(row=3, column=0, sticky=E, pady=5)
    height_entry = ttk.Entry(main_frame, width=25)
    height_entry.grid(row=3, column=1, pady=5)

    # Unit system
    unit_var = tk.StringVar(value="Metric")
    unit_frame = ttk.Frame(main_frame)
    unit_frame.grid(row=4, column=0, columnspan=2, pady=10)
    ttk.Radiobutton(unit_frame, text="Metric (kg/m)", variable=unit_var, value="Metric").pack(side=LEFT, padx=10)
    ttk.Radiobutton(unit_frame, text="Imperial (lbs/in)", variable=unit_var, value="Imperial").pack(side=LEFT, padx=10)

    result_label = ttk.Label(main_frame, text="", font=("Segoe UI", 14, "bold"))
    result_label.grid(row=5, column=0, columnspan=2, pady=15)

    def on_calculate():
        username = username_entry.get().strip()
        unit_system = unit_var.get()
        try:
            weight = float(weight_entry.get())
            height = float(height_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter numbers.")
            return
        if not username:
            messagebox.showerror("Error", "Enter a username.")
            return
        bmi = calculate_bmi(weight, height, unit_system)
        category = classify_bmi(bmi)
        result_label.config(text=f"{bmi:.2f} ({category})")
        save_bmi(username, weight, height, bmi, category, unit_system)
        messagebox.showinfo("Saved", f"BMI saved for {username}.")

    ttk.Button(main_frame, text="Calculate BMI", bootstyle=SUCCESS, width=20, command=on_calculate).grid(row=6, column=0, columnspan=2, pady=10)
    ttk.Button(main_frame, text="View History", bootstyle=INFO, width=20, command=lambda: show_history(username_entry.get().strip())).grid(row=7, column=0, columnspan=2, pady=5)

def show_history(username):
    highlight_button(history_btn)
    clear_main_frame()

    title = ttk.Label(main_frame, text="📜 BMI History", font=("Segoe UI", 18, "bold"))
    title.pack(pady=10)

    if not username:
        ttk.Label(main_frame, text="Enter a username on Home to view history.", font=("Segoe UI", 12)).pack(pady=20)
        return

    records = fetch_user_history(username)
    if not records:
        ttk.Label(main_frame, text=f"No records found for '{username}'.", font=("Segoe UI", 12)).pack(pady=20)
        return

    # ===== Summary Card =====
    total_records = len(records)
    avg_bmi = mean([r[1] for r in records])
    last_cat = records[-1][2]

    summary = ttk.LabelFrame(main_frame, text="Summary", bootstyle=INFO)
    summary.pack(fill=X, padx=10, pady=10)

    ttk.Label(summary, text=f"Total Records: {total_records}", font=("Segoe UI", 11)).pack(side=LEFT, padx=15, pady=5)
    ttk.Label(summary, text=f"Average BMI: {avg_bmi:.2f}", font=("Segoe UI", 11)).pack(side=LEFT, padx=15, pady=5)
    ttk.Label(summary, text=f"Last Category: {last_cat}", font=("Segoe UI", 11)).pack(side=LEFT, padx=15, pady=5)

    # ===== Table =====
    columns = ("Date", "BMI", "Category")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
    for c in columns:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=200)
    for d, b, cat in records:
        tree.insert("", "end", values=(d.strftime("%Y-%m-%d %H:%M"), f"{b:.2f}", cat))
    tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

    ttk.Button(main_frame, text="📊 Show Trend", bootstyle=INFO,
               command=lambda: plot_trend(username, records)).pack(pady=10)

def plot_trend(username, records):
    user_dates = [r[0] for r in records]
    user_bmis = [r[1] for r in records]
    avg_records = fetch_average_bmi()
    avg_dates = [r[0] for r in avg_records]
    avg_bmis = [r[1] for r in avg_records]

    plt.figure(figsize=(8, 4))
    plt.plot(user_dates, user_bmis, marker="o", label=f"{username}'s BMI")
    if avg_records:
        plt.plot(avg_dates, avg_bmis, linestyle="--", label="Average BMI", color="orange")
    plt.title(f"BMI Trend for {username}")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()

# ---------------- Sidebar Buttons ----------------
home_btn = ttk.Button(sidebar, text="🏠 Home", width=25, command=show_home)
home_btn.pack(pady=10, padx=10)

history_btn = ttk.Button(sidebar, text="📜 History", width=25, command=lambda: show_history(""))
history_btn.pack(pady=10, padx=10)

settings_btn = ttk.Button(sidebar, text="⚙️ Settings", width=25, command=lambda: messagebox.showinfo("Settings", "Feature coming soon!"))
settings_btn.pack(pady=10, padx=10)

theme_btn = ttk.Button(sidebar, text="🌗 Toggle Light/Dark", width=25, command=lambda:[highlight_button(theme_btn), toggle_theme()])
theme_btn.pack(pady=10, padx=10)

exit_btn = ttk.Button(sidebar, text="❌ Exit", width=25, command=root.quit)
exit_btn.pack(pady=10, padx=10)

# Start on home view
show_home()

root.mainloop()
