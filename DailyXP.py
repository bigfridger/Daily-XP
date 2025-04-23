import tkinter as tk
from tkinter import ttk
import json
import os
import math
import random
import sys

# Get directory where this script is located (handles .exe too)
base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
save_file = os.path.join(base_dir, "xp_data.json")



# XP Scaling System
def xp_needed(level):
    if level < 10:
        return 8
    elif level < 20:
        return 15
    elif level < 30:
        return 25
    elif level < 40:
        return 40
    elif level < 50:
        return 60
    elif level < 60:
        return 80
    elif level < 70:
        return 100
    elif level < 80:
        return 120
    elif level < 90:
        return 150
    else:
        return 200

xp_data = {
    "STR": {"xp": 0, "level": 1, "gold_stars": 0},
    "INT": {"xp": 0, "level": 1, "gold_stars": 0},
    "DIS": {"xp": 0, "level": 1, "gold_stars": 0},
    "CRE": {"xp": 0, "level": 1, "gold_stars": 0}
}

def load_random_quote():
    try:
        with open(os.path.join(base_dir, "quotes.txt"), "r", encoding="utf-8") as file:
            quotes = file.readlines()
        return random.choice(quotes).strip()
    except FileNotFoundError:
        return "No quote found. Make sure quotes.txt is in the same folder!"

def glow_label(label, color, duration=600, steps=10):
    original_color = label.cget("fg")
    def blend(c1, c2, t):
        return '#' + ''.join([
            format(int(int(c1[i:i+2], 16) * (1 - t) + int(c2[i:i+2], 16) * t), '02x')
            for i in (1, 3, 5)
        ])
    def animate(step=0):
        if step <= steps:
            t = step / steps
            label.config(fg=blend("#ffffff", color, t))
            label.after(duration // (2 * steps), animate, step + 1)
        elif step <= 2 * steps:
            t = (step - steps) / steps
            label.config(fg=blend(color, "#ffffff", t))
            label.after(duration // (2 * steps), animate, step + 1)
    animate()

def add_xp(attribute, amount):
    data = xp_data[attribute]
    old_level = data["level"]
    data["xp"] += amount
    while data["xp"] >= xp_needed(data["level"]):
        data["xp"] -= xp_needed(data["level"])
        data["level"] += 1
    if data["level"] > old_level:
        glow_label(ui_elements[attribute]["label"], "#00FF00")
    update_ui()

def subtract_xp(attribute, amount):
    data = xp_data[attribute]
    old_level = data["level"]
    data["xp"] -= amount
    while data["xp"] < 0 and data["level"] > 1:
        data["level"] -= 1
        data["xp"] += xp_needed(data["level"])
    data["xp"] = max(0, data["xp"])
    glow_label(ui_elements[attribute]["label"], "#FF0000")
    update_ui()

def ascend():
    for attr, data in xp_data.items():
        initial_level = data["level"]
        new_level = max(1, initial_level - 100)
        data["level"] = new_level
        if initial_level >= 100 and data["gold_stars"] < 10:
            data["gold_stars"] += 1
    update_ui()

def save_data():
    with open(save_file, 'w') as file:
        json.dump(xp_data, file, indent=4)
    print("Data saved!")

def load_data():
    if not os.path.exists(save_file):
        save_data()
    with open(save_file, 'r') as file:
        loaded_data = json.load(file)
        for attr in xp_data:
            xp_data[attr] = loaded_data.get(attr, xp_data[attr])
    update_ui()
    print("Data loaded!")

def animate_progress(progressbar, from_value, to_value, steps=40, delay=10):
    def ease_in_out(t):
        return 0.5 * (1 - math.cos(math.pi * t))
    def step(i=0):
        t = i / steps
        eased = ease_in_out(t)
        new_value = from_value + (to_value - from_value) * eased
        progressbar['value'] = new_value
        if i < steps:
            progressbar.after(delay, step, i + 1)
        else:
            progressbar['value'] = to_value
    step()

def update_ui():
    for attr, widgets in ui_elements.items():
        level = xp_data[attr]["level"]
        xp = xp_data[attr]["xp"]
        needed = xp_needed(level)
        animate_progress(widgets["progress"], widgets.get("current_value", 0), (xp / needed) * 100)
        widgets["current_value"] = (xp / needed) * 100
        widgets["label"].config(text=f"{attr} - Level {level}: {xp}/{needed} XP")
        gold_stars = xp_data[attr]["gold_stars"]
        for i in range(10):
            if i < gold_stars:
                widgets["star_gold"][i].place(x=10 + i * 40, y=25)
                widgets["star_gray"][i].place_forget()
            else:
                widgets["star_gray"][i].place(x=10 + i * 40, y=25)
                widgets["star_gold"][i].place_forget()

# GUI Setup
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.iconbitmap(os.path.join(base_dir, "app.ico"))
root.title("XP Tracker")
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.state('zoomed')
root.configure(bg='#3C2F2F')

label_font = ("Arial", 14, "bold")
button_font = ("Arial", 12)

ui_elements = {}

# Main content frame for XP UI
main_frame = tk.Frame(root, bg='#3C2F2F')
main_frame.pack(pady=10, fill='both', expand=True)

# Create XP UI
for i, attr in enumerate(xp_data.keys()):
    frame = tk.Frame(main_frame, bg='#3C2F2F', padx=20, pady=10)
    frame.pack(pady=10, fill='x')

    label = tk.Label(frame, text=f"{attr} - Level 1: 0/{xp_needed(1)} XP", font=label_font, fg="white", bg='#3C2F2F')
    label.pack()

    progress = ttk.Progressbar(frame, length=350, mode='determinate', style='custom.Horizontal.TProgressbar')
    progress.pack(pady=5)

    star_gray = [tk.Label(frame, text="★", font=("Arial", 18, "bold"), fg="gray", bg='#3C2F2F') for _ in range(10)]
    star_gold = [tk.Label(frame, text="★", font=("Arial", 18, "bold"), fg="gold", bg='#3C2F2F') for _ in range(10)]

    for i in range(10):
        star_gray[i].place(x=10 + i * 40, y=25)
        star_gold[i].place_forget()

    button_frame = tk.Frame(frame, bg='#3C2F2F')
    button_frame.pack(pady=5)

    for xp_amount in [1, 2, 5]:
        button = tk.Button(button_frame, text=f"-{xp_amount} XP", font=("Courier"),
                           command=lambda a=attr, amt=xp_amount: subtract_xp(a, amt),
                           bg='#854442', fg="white", relief="flat", padx=5, pady=5, width=8)
        button.pack(side='left', padx=5)

    for xp_amount in [1, 2, 5, 10, 20]:
        button = tk.Button(button_frame, text=f"+{xp_amount} XP", font=("Courier"),
                           command=lambda a=attr, amt=xp_amount: add_xp(a, amt),
                           bg='#DFCCAF', fg="brown", relief="flat", padx=5, pady=5, width=8)
        button.pack(side='left', padx=5)

    ui_elements[attr] = {"label": label, "progress": progress, "star_gray": star_gray, "star_gold": star_gold}

# Quote Label (centered near bottom)
# Quote Frame pinned to bottom
# Quote Frame pinned to bottom with enough height
quote_frame = tk.Frame(root, bg='#3C2F2F', height=100)
quote_frame.pack(side='bottom', fill='x')

quote_label = tk.Label(
    quote_frame,
    text=load_random_quote(),
    font=("Courier", 14),
    fg="white",
    bg='#3C2F2F',
    wraplength=1000,
    justify='center',
    anchor='center'
)
quote_label.pack(side='left', fill='both', expand=True, pady=10)

# Progressbar Style
style = ttk.Style()
style.theme_use('default')
style.configure("custom.Horizontal.TProgressbar",
                thickness=20,
                troughcolor="#a9a9a9",
                background="#0f2848")

def open_guide():
    guide_window = tk.Toplevel(root)
    guide_window.title("Tutorial")
    guide_window.geometry("950x700")
    guide_window.configure(bg='#f7e5c3')

    guide_text = (
        "Hi there! This app is made for people like you, who strive for the best and nothing else.\n" \
        "You are not here by accident, there is purpose for you, your goals are important.\n\n" \
        "This app works by tracking different types of XP to turn your life into a game, pretty cool right?\n"
        "There are 4 main different types of XP, STR (Strength), INT (Intelligence), DIS (Discipline), and CRE (Creativity) \n"
        "Each of these types are relevant to their own activities, for example, excercise will gain you strength XP\n\n" \
        "Each red button on the left will subtract the amount of XP it says, while the cream buttons on the right will add the amount of XP it says.\n\n" \
        "You can ascend at any time by using the ascend button to subtract 100 levels from every XP type, but if you ascend and any XP type is over 100 total levels, \n" \
        "a gold star will be earned while 100 is subtracted. There is a maximum of 10 gold stars for each XP type. For any XP over 100 levels, it will be acredited to the next ascension.\n\n" \
        "You can save and load your data at any time by using the respective buttons. Note that before you add any XP, you need to load any previous XP, so new XP will be added on top of previous XP. \n" \
        "This is to see the total amount. When you click save, the program will save the current amount of XP. When you load it, it loads that amount, the app is designed for you to load and then edit \n" \
        "the specific data. All data is stored locally and privately, and can be deleted at any time. \n\n"
        "After you earn 10 gold stars in each XP type, the levels will begin to increase without a cap since there is no need for ascension. See how far you can go! \n" \
        "(if you follow the intended system it should last you a very long time :) )\n\n" \
        "You can revist this screen at any time by pressing the 'Tutorial' button.\n"
        "You can see the intended system by clicking 'Guide' which is just under load"
    )

    label = tk.Label(guide_window, text=guide_text, font=("Courier", 12), fg="brown",
                     bg="#f7e5c3", wraplength=800, justify="left")
    label.pack(padx=20, pady=20)

def show_tutorial():
    tutorial_win = tk.Toplevel(root)
    tutorial_win.title("XP Guide")
    tutorial_win.configure(bg="#f7e5c3")
    tutorial_win.geometry("800x600")
    

    placeholder_label = tk.Label(
        tutorial_win,
        
        text=
        "STR (Strength): \n"
        "   Workout = +5 XP per 30 minutes \n"
        "   Sports = +10 XP per point scored \n"
        "   Exhaustion = +10 XP per full exhaustion (need water/rest) \n\n" 
        
        "INT (Intelligence): \n"
        "   Study = +5 XP per focused session \n"
        "   Reading = +1 XP per 3 pages \n"
        "   Learn new skill = +20 XP per every new skill learnt thoroughly\n\n"
        ""
        "DIS (Discipline): \n"
        "   7am wake up = +5 XP, 6am wake up = +10 XP\n"
        "   Ignoring distractions = +15 XP\n"
        "   Ignoring unhealthy things = +15 XP \n"
        "   Working to improve your life = +20 XP per hour \n\n"
        ""
        "CRE (Creativity)\n"
        "   Art, Music or Writing = +50 XP per finished piece, \n" 
        "       or +5 XP per hour spent on a expressive form \n"
        "   Practicing an instrument = 1 XP per 10 minutes \n"
        "\n"
        "\n"
        "Remember that these are just a guide! \n"
        "I intentionally didn't include punishing minus XP into this system,\n " \
        "I think thats for you to decide.\n" \
        "You can write down your own system somewhere to add XP as you see fit\n",
        font=("Arial", 12),
        fg="brown",
        bg="#f7e5c3",
        wraplength=800,
        justify="left"
    )
    placeholder_label.pack(padx=20, pady=20)

# Side Buttons
right_frame = tk.Frame(root, bg='#3C2F2F')
right_frame.place(relx=0.985, rely=0.5, anchor="e")

ascend_button = tk.Button(right_frame, text="Ascend", font=("Courier"), bg='#be9b7b', fg="black",
                          relief="flat", padx=20, pady=10, command=ascend)
ascend_button.pack(pady=10)

save_button = tk.Button(right_frame, text="Save", font=("Courier"), bg='#DFCCAF', fg="brown",
                        relief="flat", padx=20, pady=10, command=save_data)
save_button.pack(pady=10)

load_button = tk.Button(right_frame, text="Load", font=("Courier"), bg='#6F4436', fg="white",
                        relief="flat", padx=20, pady=10, command=load_data)
load_button.pack(pady=10)

tutorial_button = tk.Button(right_frame, text="Guide", font=("Courier"), bg='#be9b7b', fg="white",
relief="flat", padx=20, pady=10, command=show_tutorial)
tutorial_button.pack(pady=10)


def flash_tutorial_text():
    original_color = guide_button.cget("fg")
    steps = 10
    duration = 1000

    def blend(c1, c2, t):
        return '#' + ''.join([
            format(int(int(c1[i:i+2], 16) * (1 - t) + int(c2[i:i+2], 16) * t), '02x')
            for i in (1, 3, 5)
        ])

    def animate(step=0):
        if step <= steps:
            t = step / steps
            guide_button.config(fg=blend("#ffffff", "#00FF00", t))
            guide_button.after(duration // (2 * steps), animate, step + 1)
        elif step <= 2 * steps:
            t = (step - steps) / steps
            guide_button.config(fg=blend("#00FF00", "#ffffff", t))
            guide_button.after(duration // (2 * steps), animate, step + 1)
        else:
            guide_button.config(fg="#ffffff")

    animate()

# Add this function after your update_ui() function
def check_for_flash():
    if all(data["level"] == 1 and data["xp"] == 0 for data in xp_data.values()):
        flash_tutorial_text()
    root.after(1000, check_for_flash)


def flash_quote():
    current_color = quote_label.cget("fg")
    next_color = "white" if current_color == "#FFDD57" else "#FFDD57"  # light yellowish flash
    quote_label.config(fg=next_color)
    quote_label.after(500, flash_quote)  # every 500ms

flash_quote()

# ... [your existing root = tk.Tk() and GUI setup code]

# After creating the guide_button at the end:
guide_button = tk.Button(right_frame, text="Tutorial", font=("Courier"), bg='#3C2F2F', fg="white", relief="flat", padx=20, pady=10, command=open_guide)
guide_button.pack(pady=10)

exit_button = tk.Button(right_frame, text="Exit", font=("Courier"), bg='red', fg="white", relief="flat", command=root.destroy)
exit_button.pack(pady=10)

check_for_flash()

root.mainloop()

