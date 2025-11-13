import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt

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
    """Fetch BMI records for a specific user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, date, bmi, category FROM bmi_records WHERE username=%s ORDER BY date ASC", (username,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fetch_all_history():
    """Fetch all BMI records for all users."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, date, bmi, category FROM bmi_records ORDER BY username ASC, date ASC")
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
    # Adjust label color
    menu_label.configure(foreground="black" if new_theme == "cyborg" else "#0d6efd")

def highlight_button(active_btn):
    for btn in sidebar.winfo_children():
        if isinstance(btn, ttk.Button):
            btn.configure(bootstyle=SECONDARY)
    active_btn.configure(bootstyle=INFO)

# Main frame
main_frame = ttk.Frame(root, padding=30)
main_frame.pack(fill=BOTH, expand=True)

# ---------------- Delete Logic ----------------
def delete_selected_record(tree, username):
    """Delete selected BMI record for logged user."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a record to delete.")
        return

    record = tree.item(selected[0])["values"]
    if not record:
        return
    record_id = record[0]

    confirm = messagebox.askyesno("Confirm Delete", "Delete this record?")
    if not confirm:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM bmi_records WHERE id=%s AND username=%s", (record_id, username))
    conn.commit()
    cur.close()
    conn.close()

    messagebox.showinfo("Deleted", "Record deleted successfully.")
    show_history(username)

def delete_all_records(username):
    """Delete all BMI records for a user (confirmation required)."""
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ALL records for '{username}'?")
    if not confirm:
        return

    confirm_window = tb.Toplevel(root)
    confirm_window.title("Confirm Username")
    confirm_window.geometry("330x180")
    confirm_window.resizable(False, False)
    confirm_window.grab_set()

    bg_color = "#121212" if current_theme == "cyborg" else "white"
    fg_color = "white" if current_theme == "cyborg" else "black"
    confirm_window.configure(bg=bg_color)

    ttk.Label(confirm_window, text=f"Type '{username}' to confirm:",
              font=("Segoe UI", 11, "bold"), background=bg_color, foreground=fg_color).pack(pady=10)
    entry = ttk.Entry(confirm_window, width=25)
    entry.pack(pady=5)

    def confirm_delete_action():
        if entry.get().strip() == username:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM bmi_records WHERE username=%s", (username,))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Deleted", f"All records for {username} deleted.")
            confirm_window.destroy()
            show_history(username)
        else:
            messagebox.showerror("Mismatch", "Username does not match. Deletion cancelled.")
            confirm_window.destroy()

    btn_frame = ttk.Frame(confirm_window)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Confirm Delete", bootstyle=DANGER, command=confirm_delete_action).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame, text="Cancel", bootstyle=SECONDARY, command=confirm_window.destroy).pack(side=LEFT, padx=5)

# ---------------- Views ----------------
def clear_main_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

def show_home():
    highlight_button(home_btn)
    clear_main_frame()

    ttk.Label(main_frame, text="BMI Calculator", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 20))

    ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=E, pady=5)
    username_entry = ttk.Entry(main_frame, width=25)
    username_entry.grid(row=1, column=1, pady=5, sticky=W)

    ttk.Label(main_frame, text="Weight:").grid(row=2, column=0, sticky=E, pady=5)
    weight_entry = ttk.Entry(main_frame, width=25)
    weight_entry.grid(row=2, column=1, pady=5, sticky=W)

    ttk.Label(main_frame, text="Height:").grid(row=3, column=0, sticky=E, pady=5)
    height_entry = ttk.Entry(main_frame, width=25)
    height_entry.grid(row=3, column=1, pady=5, sticky=W)

    unit_var = tk.StringVar(value="Metric")
    unit_frame = ttk.Frame(main_frame)
    unit_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=W)
    ttk.Radiobutton(unit_frame, text="Metric (kg/m)", variable=unit_var, value="Metric").pack(side=LEFT, padx=10)
    ttk.Radiobutton(unit_frame, text="Imperial (lbs/in)", variable=unit_var, value="Imperial").pack(side=LEFT, padx=10)

    result_label = ttk.Label(main_frame, text="", font=("Segoe UI", 14, "bold"))
    result_label.grid(row=5, column=0, columnspan=2, pady=15, sticky=W)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=2, rowspan=6, padx=40, sticky="n")

    def on_calculate():
        username = username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Enter a username.")
            return
        try:
            weight = float(weight_entry.get())
            height = float(height_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")
            return
        unit_system = unit_var.get()
        bmi = calculate_bmi(weight, height, unit_system)
        category = classify_bmi(bmi)
        result_label.config(text=f"{bmi:.2f} ({category})")
        save_bmi(username, weight, height, bmi, category, unit_system)
        messagebox.showinfo("Saved", f"BMI saved for {username}.")

    ttk.Button(button_frame, text=" Calculate BMI", bootstyle=SUCCESS, width=20, command=on_calculate).pack(pady=10)
    ttk.Button(button_frame, text=" View History", bootstyle=INFO, width=20,
               command=lambda: show_history(username_entry.get().strip())).pack(pady=10)

def show_history(username):
    highlight_button(history_btn)
    clear_main_frame()

    ttk.Label(main_frame, text=" BMI History", font=("Segoe UI", 18, "bold")).pack(pady=10)

    # All users view
    if not username:
        records = fetch_all_history()
        if not records:
            ttk.Label(main_frame, text="No records found.", font=("Segoe UI", 12)).pack(pady=20)
            return
        columns = ("Username", "Date", "BMI", "Category")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=12)
        for c in columns:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=200)
        current_user = None
        for user, d, b, cat in records:
            if user != current_user:
                tree.insert("", "end", values=(f"--- {user} ---", "", "", ""))
                current_user = user
            tree.insert("", "end", values=(user, d.strftime("%Y-%m-%d %H:%M"), f"{b:.2f}", cat))
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        return

    # Personal user history
    records = fetch_user_history(username)
    if not records:
        ttk.Label(main_frame, text=f"No records found for '{username}'.", font=("Segoe UI", 12)).pack(pady=20)
        return

    columns = ("ID", "Date", "BMI", "Category")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
    for c in columns:
        tree.heading(c, text=c)
        width = 80 if c == "ID" else 200
        tree.column(c, anchor="center", width=width)
    for rec in records:
        tree.insert("", "end", values=(rec[0], rec[1].strftime("%Y-%m-%d %H:%M"), f"{rec[2]:.2f}", rec[3]))
    tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text=" Show Trend", bootstyle=INFO,
               command=lambda: plot_trend(username, records)).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame, text=" Delete Selected", bootstyle=WARNING,
               command=lambda: delete_selected_record(tree, username)).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame, text=" Delete All", bootstyle=DANGER,
               command=lambda: delete_all_records(username)).pack(side=LEFT, padx=5)

def plot_trend(username, records):
    user_dates = [r[1] for r in records]
    user_bmis = [r[2] for r in records]
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
home_btn = ttk.Button(sidebar, text="Home", width=25, command=show_home)
home_btn.pack(pady=10, padx=10)

history_btn = ttk.Button(sidebar, text=" History", width=25, command=lambda: show_history(""))
history_btn.pack(pady=10, padx=10)

settings_btn = ttk.Button(sidebar, text=" Settings", width=25,
                           command=lambda: messagebox.showinfo("Settings", "Feature coming soon!"))
settings_btn.pack(pady=10, padx=10)

theme_btn = ttk.Button(sidebar, text=" Toggle Light/Dark", width=25,
                        command=lambda: [highlight_button(theme_btn), toggle_theme()])
theme_btn.pack(pady=10, padx=10)

exit_btn = ttk.Button(sidebar, text=" Exit", width=25, command=root.quit)
exit_btn.pack(pady=10, padx=10)

# Start on home
show_home()
root.mainloop()
