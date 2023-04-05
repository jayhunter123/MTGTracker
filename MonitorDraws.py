import os
import time
import re
import tkinter as tk
from tkinter import ttk
import threading
import psutil

root = tk.Tk()

def read_land_cards_from_file(filename="land_cards.txt"):
    with open(filename, "r") as file:
        land_cards = [line.strip() for line in file.readlines()]
    return land_cards

# List of basic land card names (You can update this list as needed)
land_cards = read_land_cards_from_file()

# MTG Arena log file location
log_file_path = os.path.expanduser("E:\MTGA\MTGA_Data\Logs\Logs")

# Card draw and game start regex patterns
card_draw_pattern = re.compile(r"<== PlayerInventory\.UpdateCardInventory\(\d+\) (.+?)\n")
game_start_pattern = re.compile(r"(Event_Start|Event_Join)")

def is_mtga_running():
    for process in psutil.process_iter(["name"]):
        if process.info["name"] == "MTGA.exe":
            return True
    return False

def update_ui():
    land_draws_label.config(text=f"Land Draws: {land_draws}")
    nonland_draws_label.config(text=f"Non-land Draws: {nonland_draws}")
    ratio = land_draws / (land_draws + nonland_draws) if land_draws + nonland_draws > 0 else 0
    ratio_label.config(text=f"Land to Non-land Ratio: {ratio:.2f}")
    games_played_label.config(text=f"Games Played: {games_played}")
    root.update()

def save_log():
    ratio = land_draws / (land_draws + nonland_draws) if land_draws + nonland_draws > 0 else 0
    with open("draws_log.txt", "a") as file:
        file.write(f"{land_draws},{nonland_draws},{ratio:.2f},{games_played}\n")

def is_land(card_name):
    return card_name in land_cards

status_label = ttk.Label(root, text="MTG Arena Status: Not Running")
status_label.pack()

def update_status(root, running, reading):
    if running:
        status_label.config(text="MTG Arena Status: Running")
        if reading:
            status_label.config(foreground="green")
        else:
            status_label.config(foreground="orange")
    else:
        status_label.config(text="MTG Arena Status: Not Running")
        status_label.config(foreground="red")
    root.update()

def monitor_log_file(file_path):
    global land_draws, nonland_draws, games_played
    land_draws, nonland_draws, games_played = 0, 0, 0

    if not os.path.exists(file_path):
        print(f"Log file not found: {file_path}")
        return

    previous_size = os.path.getsize(file_path)

    reading = False

    while True:
        current_size = os.path.getsize(file_path)
        mtga_running = is_mtga_running()
        update_status(root, mtga_running, reading)

        if current_size != previous_size:
            with open(file_path, "r", encoding="utf-8") as f:
                f.seek(previous_size)
                lines = f.readlines()
                previous_size = current_size

            reading = True

            for line in lines:
                if game_start_pattern.search(line):
                    games_played += 1
                    land_draws, nonland_draws = 0, 0
                    print(f"New game started. Total games played: {games_played}")

                card_draw_match = card_draw_pattern.search(line)
                if card_draw_match:
                    card_name = card_draw_match.group(1)
                    if is_land(card_name):
                        land_draws += 1
                    else:
                        nonland_draws += 1

                    print(f"Land Draws: {land_draws}")
                    print(f"Non-land Draws: {nonland_draws}")
                    print("-------------------------------")

                update_ui()

        time.sleep(1)  # Sleep for a short period before checking for new lines

if __name__ == "__main__":
    land_draws, nonland_draws, games_played = 0, 0, 0
    root = tk.Tk()
    root.title("MTG Arena Land/Non-land Draws")

    land_draws_label = ttk.Label(root, text=f"Land Draws: {land_draws}")
    land_draws_label.pack()
    nonland_draws_label = ttk.Label(root, text=f"Non-land Draws: {nonland_draws}")
    nonland_draws_label.pack()
    ratio_label = ttk.Label(root, text="Land to Non-land Ratio: 0.00")
    ratio_label.pack()
    games_played_label = ttk.Label(root, text=f"Games Played: {games_played}")
    games_played_label.pack()

    save_button = ttk.Button(root, text="Save Log", command=save_log)
    save_button.pack()

    monitor_thread = threading.Thread(target=monitor_log_file, args=(log_file_path,), daemon=True)
    monitor_thread.start()

    root.mainloop()

