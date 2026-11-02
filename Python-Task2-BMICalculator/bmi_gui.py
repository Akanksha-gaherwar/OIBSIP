# BMI Calculator (Advanced) - tkinter, SQLite, matplotlib
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

DB_FILE = "bmi_records.db"
BG = "#eef3fb"
CARD = "#ffffff"
DARK = "#1f2a44"
COLORS = {"Underweight": "#74c0fc", "Normal": "#69db7c",
          "Overweight": "#ffd43b", "Obese": "#ff8787"}
SEGMENTS = [(10, 18.5, "Underweight"), (18.5, 25, "Normal"),
            (25, 30, "Overweight"), (30, 40, "Obese")]


def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    return "Obese"


def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY "
                     "AUTOINCREMENT, name TEXT, weight REAL, height REAL, "
                     "bmi REAL, category TEXT, date TEXT)")
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


def save_record(name, weight, height, bmi, category):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO records (name, weight, height, bmi, category, date) "
                     "VALUES (?, ?, ?, ?, ?, ?)",
                     (name, weight, height, bmi, category,
                      datetime.now().strftime("%d-%m-%Y %H:%M")))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


def load_records(name):
    try:
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute("SELECT date, bmi, category FROM records "
                            "WHERE name = ? ORDER BY id", (name,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error:
        return []


def load_names():
    try:
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute("SELECT DISTINCT name FROM records").fetchall()
        conn.close()
        return [r[0] for r in rows]
    except sqlite3.Error:
        return []


def set_status(text, ok=True):
    status.config(text=text, fg="#2b8a3e" if ok else "#e03131")


def draw_scale(bmi=None):
    scale.delete("all")
    def x(v):
        return 10 + (v - 10) / 30 * 620
    for start, end, cat in SEGMENTS:
        scale.create_rectangle(x(start), 22, x(end), 40, fill=COLORS[cat], outline="")
    for value in (18.5, 25, 30):
        scale.create_text(x(value), 52, text=str(value), font=("Segoe UI", 9),
                          fill=DARK)
    if bmi is not None:
        mx = x(min(max(bmi, 10), 40))
        scale.create_polygon(mx - 7, 6, mx + 7, 6, mx, 21, fill=DARK)


def refresh_table():
    for row in table.get_children():
        table.delete(row)
    for date, bmi, cat in load_records(user_var.get().strip())[-6:][::-1]:
        table.insert("", tk.END, values=(date, format(bmi, ".2f"), cat))


def refresh_names():
    user_box["values"] = load_names()


def on_calculate():
    name = user_var.get().strip()
    if name == "":
        set_status("Enter or choose a name", False)
        return
    try:
        weight = float(weight_var.get())
        height = float(height_var.get())
    except ValueError:
        set_status("Weight and height must be numbers", False)
        return
    if not (20 <= weight <= 300) or not (0.5 <= height <= 2.5):
        set_status("Use weight 20-300 kg and height 0.5-2.5 m", False)
        return
    bmi = weight / (height ** 2)
    category = get_category(bmi)
    card.config(bg=COLORS[category])
    title_label.config(bg=COLORS[category])
    bmi_label.config(text=format(bmi, ".2f"), bg=COLORS[category])
    cat_label.config(text=category, bg=COLORS[category])
    draw_scale(bmi)
    if save_record(name, weight, height, bmi, category):
        set_status("Record saved for " + name)
    else:
        set_status("Could not save the record", False)
    refresh_names()
    refresh_table()


def on_graph():
    name = user_var.get().strip()
    rows = load_records(name)
    if len(rows) < 2:
        messagebox.showinfo("BMI trend", "Calculate at least 2 times for this name.")
        return
    values = [r[1] for r in rows]
    plt.figure("BMI trend - " + name)
    plt.axhspan(18.5, 24.9, color="#69db7c", alpha=0.25, label="Normal range")
    plt.plot(range(1, len(values) + 1), values, marker="o", color="#1f2a44")
    plt.xlabel("Entry number")
    plt.ylabel("BMI")
    plt.title("BMI trend for " + name)
    plt.legend()
    plt.show()


root = tk.Tk()
root.title("BMI Calculator")
root.state("zoomed")
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=34, font=("Segoe UI", 13))
style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

user_var = tk.StringVar()
weight_var = tk.StringVar()
height_var = tk.StringVar()

tk.Label(root, text="BMI Tracker", font=("Segoe UI", 34, "bold"),
         bg=BG, fg=DARK).pack(pady=(14, 2))
tk.Label(root, text="Calculate, save and track your BMI over time",
         bg=BG, fg="#5c6b8a").pack()

body = tk.Frame(root, bg=BG)
body.pack(pady=20, padx=80, fill="both", expand=True)

left = tk.Frame(body, bg=CARD, padx=30, pady=26)
left.pack(side="left", fill="y")
right = tk.Frame(body, bg=BG)
right.pack(side="left", padx=(30, 0), fill="both", expand=True)

tk.Label(left, text="Name", bg=CARD, fg=DARK).pack(anchor="w")
user_box = ttk.Combobox(left, textvariable=user_var, width=28, values=load_names())
user_box.pack(pady=(2, 10))
user_box.bind("<<ComboboxSelected>>", lambda e: refresh_table())

tk.Label(left, text="Weight (kg)", bg=CARD, fg=DARK).pack(anchor="w")
tk.Entry(left, textvariable=weight_var, width=30, font=("Segoe UI", 13)).pack(pady=(2, 10))
tk.Label(left, text="Height (m)", bg=CARD, fg=DARK).pack(anchor="w")
tk.Entry(left, textvariable=height_var, width=30, font=("Segoe UI", 13)).pack(pady=(2, 14))

tk.Button(left, text="Calculate", command=on_calculate, bg="#228be6", fg="white",
          font=("Segoe UI", 11, "bold"), width=22).pack(pady=3)
tk.Button(left, text="Show trend graph", command=on_graph, bg="#e9ecef",
          font=("Segoe UI", 10), width=22).pack(pady=3)
status = tk.Label(left, text="", bg=CARD, wraplength=210)
status.pack(pady=(8, 0))

card = tk.Frame(right, bg="#dee2e6", padx=20, pady=26)
card.pack(fill="x")
title_label = tk.Label(card, text="Your BMI", bg="#dee2e6", fg=DARK)
title_label.pack()
bmi_label = tk.Label(card, text="--", font=("Segoe UI", 64, "bold"),
                     bg="#dee2e6", fg=DARK)
bmi_label.pack()
cat_label = tk.Label(card, text="Enter your details", font=("Segoe UI", 22),
                     bg="#dee2e6", fg=DARK)
cat_label.pack()

scale = tk.Canvas(right, width=640, height=70, bg=BG, highlightthickness=0)
scale.pack(pady=8)
draw_scale()

table = ttk.Treeview(right, columns=("date", "bmi", "category"), show="headings",
                     height=8)
for col, text, width in [("date", "Date", 230), ("bmi", "BMI", 110),
                         ("category", "Category", 190)]:
    table.heading(col, text=text)
    table.column(col, width=width, anchor="center")
table.pack(fill="x")

if not init_db():
    set_status("Database error", False)

root.mainloop()