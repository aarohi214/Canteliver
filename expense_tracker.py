import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv

# -------------------- DATABASE --------------------
def init_db():
    conn = sqlite3.connect("expenses_v2.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            category TEXT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_expense(category, amount, date):
    conn = sqlite3.connect("expenses_v2.db")
    c = conn.cursor()
    c.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
              (category, amount, date))
    conn.commit()
    conn.close()

def get_expenses(month_filter=None):
    conn = sqlite3.connect("expenses_v2.db")
    c = conn.cursor()
    if month_filter:
        c.execute("SELECT * FROM expenses WHERE strftime('%Y-%m', date)=? ORDER BY date DESC", (month_filter,))
    else:
        c.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# -------------------- FUNCTIONS --------------------
def add_expense():
    category = category_var.get()
    amount = amount_entry.get()
    date = date_entry.get()

    if not amount:
        messagebox.showwarning("Input Error", "Amount is required.")
        return

    try:
        amount = float(amount)
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Format Error", "Amount must be a number.\nDate format: YYYY-MM-DD.")
        return

    insert_expense(category, amount, date)
    amount_entry.delete(0, tk.END)
    refresh_table()

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    month = month_filter_entry.get().strip()
    rows = get_expenses(month if month else None)
    
    total = 0
    for row in rows:
        tree.insert("", tk.END, values=row[1:])
        total += row[2]
    
    total_label.config(text=f"Total: ₹{total:.2f}")

def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Delete", "Select a record to delete.")
        return
    item = tree.item(selected[0])
    category, amount, date = item['values']
    
    conn = sqlite3.connect("expenses_v2.db")
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE category=? AND amount=? AND date=? LIMIT 1",
              (category, amount, date))
    conn.commit()
    conn.close()
    refresh_table()

def export_to_csv():
    rows = get_expenses(month_filter_entry.get().strip() or None)
    if not rows:
        messagebox.showinfo("Export", "No expenses to export.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Amount", "Date"])
        for row in rows:
            writer.writerow(row[1:])
    
    messagebox.showinfo("Export", f"Expenses exported to {file_path}")

def show_summary():
    conn = sqlite3.connect("expenses_v2.db")
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = c.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("Summary", "No data to show.")
        return

    summary = "\n".join([f"{cat}: ₹{amt:.2f}" for cat, amt in data])
    messagebox.showinfo("Category Summary", summary)

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    bg = "#2e2e2e" if dark_mode else "SystemButtonFace"
    fg = "white" if dark_mode else "black"

    root.configure(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.configure(bg=bg, fg=fg)
        except:
            pass

# -------------------- GUI SETUP --------------------
init_db()
root = tk.Tk()
root.title("Enhanced Expense Tracker")
root.geometry("650x600")
root.resizable(False, False)
dark_mode = False

# ----- Input Frame -----
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Category").grid(row=0, column=0, padx=5, pady=5)
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(input_frame, textvariable=category_var, values=[
    "Food", "Travel", "Utilities", "Shopping", "Rent", "Other"], state="readonly")
category_dropdown.grid(row=0, column=1, padx=5)
category_dropdown.set("Food")

tk.Label(input_frame, text="Amount (₹)").grid(row=1, column=0, padx=5)
amount_entry = tk.Entry(input_frame)
amount_entry.grid(row=1, column=1, padx=5)

tk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(row=2, column=0, padx=5)
date_entry = tk.Entry(input_frame)
date_entry.grid(row=2, column=1, padx=5)
date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

tk.Button(input_frame, text="Add Expense", command=add_expense).grid(row=3, column=0, columnspan=2, pady=10)

# ----- Filter -----
filter_frame = tk.Frame(root)
filter_frame.pack(pady=5)

tk.Label(filter_frame, text="Filter (YYYY-MM):").pack(side=tk.LEFT, padx=5)
month_filter_entry = tk.Entry(filter_frame, width=10)
month_filter_entry.pack(side=tk.LEFT)
tk.Button(filter_frame, text="Apply Filter", command=refresh_table).pack(side=tk.LEFT, padx=5)

# ----- Table (Treeview) -----
columns = ("Category", "Amount", "Date")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")
tree.pack(pady=10)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.place(x=615, y=235, height=300)

# ----- Total Label -----
total_label = tk.Label(root, text="Total: ₹0.00", font=("Arial", 12, "bold"))
total_label.pack()

# ----- Buttons -----
tk.Button(root, text="Delete Selected", command=delete_selected).pack(pady=2)
tk.Button(root, text="Export to CSV", command=export_to_csv).pack(pady=2)
tk.Button(root, text="Category Summary", command=show_summary).pack(pady=2)
tk.Button(root, text="Toggle Dark Mode", command=toggle_theme).pack(pady=2)

refresh_table()
root.mainloop()
# Close the database connection when the application exits

