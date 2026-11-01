# Random Password Generator
import secrets
import string
import tkinter as tk
import pyperclip

AMBIGUOUS = "0O1lI"


def build_pools(upper, lower, digits, symbols, no_ambiguous):
    pools = []
    if upper:
        pools.append(string.ascii_uppercase)
    if lower:
        pools.append(string.ascii_lowercase)
    if digits:
        pools.append(string.digits)
    if symbols:
        pools.append(string.punctuation)
    if no_ambiguous:
        pools = ["".join(c for c in p if c not in AMBIGUOUS) for p in pools]
    return pools


def generate_password(length, pools):
    password = [secrets.choice(pool) for pool in pools]
    all_chars = "".join(pools)
    while len(password) < length:
        password.append(secrets.choice(all_chars))
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def check_strength(password):
    score = 0
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    return "Strong"

history = []
COLORS = {"Weak": "#ff6b6b", "Medium": "#ffd166", "Strong": "#4ecdc4"}


def on_generate():
    pools = build_pools(upper_var.get(), lower_var.get(), digit_var.get(),
                        symbol_var.get(), ambig_var.get())
    if len(pools) < 2:
        message.config(text="Select at least 2 character types", fg="#ff6b6b")
        return
    pw = generate_password(length_var.get(), pools)
    password_var.set(pw)
    pyperclip.copy(pw)
    strength = check_strength(pw)
    strength_label.config(text="Strength: " + strength, fg=COLORS[strength])
    message.config(text="Copied to clipboard", fg="#4ecdc4")
    history.insert(0, pw)
    del history[5:]
    history_box.delete(0, tk.END)
    for item in history:
        history_box.insert(tk.END, item)


def on_copy():
    if password_var.get():
        pyperclip.copy(password_var.get())
        message.config(text="Copied to clipboard", fg="#4ecdc4")


root = tk.Tk()
root.title("Password Generator")
root.resizable(False, False)
root.configure(bg="#1e1b2e")

length_var = tk.IntVar(value=12)
upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
digit_var = tk.BooleanVar(value=True)
symbol_var = tk.BooleanVar(value=True)
ambig_var = tk.BooleanVar(value=False)
password_var = tk.StringVar()

tk.Label(root, text="Password Generator", font=("Segoe UI", 20, "bold"),
         bg="#1e1b2e", fg="#c9b6ff").pack(pady=15)

tk.Entry(root, textvariable=password_var, font=("Consolas", 16),
         justify="center", state="readonly", width=24).pack(pady=5)

strength_label = tk.Label(root, text="Strength: -", font=("Segoe UI", 12),
                          bg="#1e1b2e", fg="white")
strength_label.pack(pady=5)

tk.Label(root, text="Length", bg="#1e1b2e", fg="white").pack()
tk.Scale(root, from_=8, to=32, orient="horizontal", variable=length_var,
         length=280, bg="#1e1b2e", fg="white", highlightthickness=0).pack()

for text, var in [("Uppercase letters", upper_var), ("Lowercase letters", lower_var),
                  ("Numbers", digit_var), ("Symbols", symbol_var),
                  ("Exclude confusing characters (0 O 1 l I)", ambig_var)]:
    tk.Checkbutton(root, text=text, variable=var, bg="#1e1b2e", fg="white",
                   selectcolor="#3b3556", activebackground="#1e1b2e",
                   activeforeground="white").pack(anchor="w", padx=60)

tk.Button(root, text="Generate", command=on_generate, bg="#7c5cff", fg="white",
          font=("Segoe UI", 12, "bold"), width=14).pack(pady=10)
tk.Button(root, text="Copy", command=on_copy, bg="#4ecdc4",
          font=("Segoe UI", 11), width=14).pack()

message = tk.Label(root, text="", bg="#1e1b2e", fg="white")
message.pack(pady=5)

tk.Label(root, text="Last 5 passwords", bg="#1e1b2e", fg="#c9b6ff").pack()
history_box = tk.Listbox(root, height=5, width=32, font=("Consolas", 11))
history_box.pack(pady=5)

root.mainloop()
