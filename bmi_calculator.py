import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# =========== Database Connection ===========
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="bmi_user",
        password="server",
        database="bmi_calc"
    )

# =========== BMI Calculation ===========
def calculate_bmi(weight, height, unit_system):
    """Calculate BMI in metric (kg/m) or imperial (lbs/in)."""
    if unit_system == "Metric":
        return weight / (height ** 2)
    else:  # Imperial
        return (weight / (height ** 2)) * 703.0  # lbs/inches²

def classify_bmi(bmi):
    """Return BMI category."""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25.0:
        return "Normal weight"
    elif 25.0 <= bmi < 30.0:
        return "Overweight"
    else:
        return "Obesity"

# ============ Database Functions ============
def save_bmi(username, weight, height, bmi, category, unit_system):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bmi_records (username, weight, height, bmi, category, unit_system, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, weight, height, bmi, category, unit_system, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving BMI record: {err}")

def fetch_user_history(username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT date, bmi, category FROM bmi_records WHERE username=%s ORDER BY date ASC", (username,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching history: {err}")
        return []

def fetch_average_bmi():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT DATE(date) as day, AVG(bmi) as avg_bmi
            FROM bmi_records
            GROUP BY DATE(date)
            ORDER BY DATE(date)
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching averages: {err}")
        return []

# ============ GUI Functions ============
def on_calculate():
    username = username_entry.get().strip()
    unit_system = unit_var.get()

    # parse numeric entries
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Weight and height must be numeric.")
        return

    if not username:
        messagebox.showerror("Missing Info", "Please enter a username.")
        return

    # validation: use AND so both conditions must be true to pass
    if unit_system == "Metric":
        if not (0 < weight < 500 and 0 < height < 3):
            messagebox.showerror("Invalid Range", "Please enter realistic metric values (kg, meters).")
            return
    else:  # Imperial
        if not (0 < weight < 1100 and 0 < height < 120):
            messagebox.showerror("Invalid Range", "Please enter realistic imperial values (lbs, inches).")
            return

    bmi = calculate_bmi(weight, height, unit_system)
    category = classify_bmi(bmi)
    result_label.config(text=f"BMI: {bmi:.2f} ({category})")

    save_bmi(username, weight, height, bmi, category, unit_system)
    messagebox.showinfo("Saved", f"Record saved for {username}")

def on_view_history():
    username = username_entry.get().strip()
    if not username:
        messagebox.showerror("Missing Info", "Enter a username to view history.")
        return

    records = fetch_user_history(username)
    if not records:
        messagebox.showinfo("No Data", f"No records found for {username}.")
        return

    hist_win = tk.Toplevel(root)
    hist_win.title(f"{username}'s BMI History")
    hist_win.geometry("500x350")

    tree = ttk.Treeview(hist_win, columns=("Date", "BMI", "Category"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("BMI", text="BMI")
    tree.heading("Category", text="Category")
    tree.column("Date", width=180)
    tree.column("BMI", width=80, anchor="center")
    tree.column("Category", width=120, anchor="center")

    for row in records:
        # row[0] is a datetime or string; format nicely
        if isinstance(row[0], datetime):
            date_str = row[0].strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_str = str(row[0])
        tree.insert("", "end", values=(date_str, f"{row[1]:.2f}", row[2]))

    tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    ttk.Button(hist_win, text="Show BMI Trend", command=lambda: plot_trend(username, records)).pack(pady=6)

def plot_trend(username, records):
    # convert user records to date/datetime and floats
    user_dates = []
    user_bmis = []
    for r in records:
        d = r[0]
        if isinstance(d, datetime):
            dt = d
        else:
            # MySQL connector typically returns datetime objects, but guard here
            try:
                dt = datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S")
            except Exception:
                # fallback try date-only format
                try:
                    dt = datetime.strptime(str(d), "%Y-%m-%d")
                except Exception:
                    continue
        user_dates.append(dt)
        user_bmis.append(float(r[1]))

    avg_records = fetch_average_bmi()
    avg_dates = []
    avg_bmis = []
    for r in avg_records:
        # r[0] is DATE (YYYY-MM-DD), r[1] is avg_bmi
        try:
            dt = datetime.strptime(str(r[0]), "%Y-%m-%d")
            avg_dates.append(dt)
            avg_bmis.append(float(r[1]))
        except Exception:
            continue

    if not user_dates:
        messagebox.showinfo("No Data", "No plottable user data.")
        return

    plt.figure(figsize=(9, 5))
    plt.plot(user_dates, user_bmis, marker='o', label=f"{username}'s BMI")
    if avg_dates and avg_bmis:
        plt.plot(avg_dates, avg_bmis, linestyle='--', marker='s', label='Daily Average BMI')

    plt.title(f"BMI Trend for {username}")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ============ Main GUI Setup ============
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("420x520")
root.resizable(False, False)

title_label = tk.Label(root, text="BMI Calculator", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# username
tk.Label(root, text="Username:").pack()
username_entry = tk.Entry(root, width=30)
username_entry.pack(pady=5)

# weight & height
tk.Label(root, text="Weight:").pack()
weight_entry = tk.Entry(root, width=30)
weight_entry.pack(pady=5)

tk.Label(root, text="Height:").pack()
height_entry = tk.Entry(root, width=30)
height_entry.pack(pady=5)

# unit system
unit_var = tk.StringVar(value="Metric")
unit_frame = tk.Frame(root)
unit_frame.pack(pady=5)
tk.Label(unit_frame, text="Unit System:").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(unit_frame, text="Metric (kg / m)", variable=unit_var, value="Metric").pack(side=tk.LEFT, padx=6)
tk.Radiobutton(unit_frame, text="Imperial (lbs / in)", variable=unit_var, value="Imperial").pack(side=tk.LEFT, padx=6)

# buttons
ttk.Button(root, text="Calculate BMI", command=on_calculate).pack(pady=12)
result_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="blue")
result_label.pack(pady=6)

ttk.Button(root, text="View History", command=on_view_history).pack(pady=6)
ttk.Button(root, text="Exit", command=root.quit).pack(pady=6)

root.mainloop()
