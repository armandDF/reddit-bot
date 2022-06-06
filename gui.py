import tkinter as tk

import threading
import random
import time

from main import *

""" === Start Functions === """


def main_loop(**kwargs):
    """
    Posts a message, then waits with the given wait times
    Outputs the time it waits, and the different actions
    """
    # - Get the parameters - #
    is_oc, is_spoiler, is_nsfw, is_flair = [
        kwargs[key] for key in ("is_oc", "is_spoiler", "is_nsfw", "is_flair")]
    is_proxy = kwargs["is_proxy"]
    wait_min, wait_max, timeout = [kwargs[key]
                                   for key in ("wait_min", "wait_max", "timeout")]
    time_restart = kwargs["time_restart"]
    file_path = kwargs["file_path"]
    is_headless = kwargs["is_headless"]

    last_sub_reddit = ''
    sub_reddits = get_subreddits()
    while start_btn["text"] == "Stop":
        while True:
            try:
                # - Open browser and login - #
                driver = start_driver(proxy=is_proxy, headless=is_headless)
                driver = login(driver)
                break
            except Exception as e:
                output_box.insert(
                    tk.END, f"[{time.strftime('%D %H:%M:%S')}] Error logging in : {e}")

        # quits and relogs after time_restart seconds
        start_time = time.time()
        while time.time() - start_time < time_restart:
            if start_btn["text"] != "Stop":
                break
            # - Post message - #
            date = time.strftime("%D %H:%M:%S")
            output_box.insert(
                tk.END, f"[{date}] Posting a new message...")
            # - Getting a random subreddit different than the last one - #
            if last_sub_reddit and len(sub_reddits) > 1:
                sub_reddits.remove(last_sub_reddit)
                sub_reddit = random.choice(sub_reddits)
                sub_reddits.append(last_sub_reddit)
            else:
                sub_reddit = random.choice(sub_reddits)
            last_sub_reddit = sub_reddit

            try:
                is_successful = post_msg_comment(driver, sub_reddit, file_path, timeout=timeout, is_oc=is_oc,
                                                 is_spoiler=is_spoiler, is_nsfw=is_nsfw, is_flair=is_flair)
            except Exception as e:
                date = time.strftime("%D %H:%M:%S")
                output_box.insert(tk.END, f"[{date}] Error: {e}")
                break

            if not is_successful:
                output_box.insert(
                    tk.END, f"[{date}] Failed to post a message, restarting...")
                break

            # - Wait - #
            wait_time = random.randint(wait_min, wait_max)
            date = time.strftime("%D %H:%M:%S")
            output_box.insert(
                tk.END, f"[{date}] Waiting {int(wait_time)} seconds")

            # - Sleep but check if bot is stopped - #
            for sec_i in range(wait_time):
                if start_btn["text"] != "Stop" or (time.time() - start_time > time_restart):
                    break
                time.sleep(1)
            if (time.time() - start_time > time_restart):
                break
            time.sleep(random.random())

        if start_btn["text"] == "Stop":
            date = time.strftime("%D %H:%M:%S")
            output_box.insert(
                tk.END, f"[{date}] Restarting browser...")
        driver.quit()


def start():
    """
    Retrieves all parameters from the window, and switch the btn text
    """
    if start_btn["text"] == "Start":
        is_oc, is_spoiler, is_nsfw, is_flair = [
            var.get() for var in post_variables]
        is_proxy = proxy_var.get()
        wait_min, wait_max, timeout = [entry.get() for entry in entries]
        time_restart = restart_entry.get()
        file_path = file_entry.get()
        is_headless = headless_var.get()

        try:
            wait_min, wait_max, timeout = map(
                int, [wait_min, wait_max, timeout])
        except ValueError:
            output_box.insert(tk.END, "Invalid time values")
            return
        try:
            time_restart = int(time_restart)
        except ValueError:
            output_box.insert(tk.END, "Invalid time restart value")
            return
        if wait_min > wait_max:
            output_box.insert(tk.END, "Wait min must be less than wait max")
            return

        # - Start the main loop - #
        kwargs = {"is_oc": is_oc, "is_spoiler": is_spoiler, "is_nsfw": is_nsfw, "is_flair": is_flair, "is_proxy": is_proxy,
                  "wait_min": wait_min, "wait_max": wait_max, "timeout": timeout, "time_restart": time_restart,
                  "file_path": file_path, "is_headless": is_headless}
        thread = threading.Thread(target=main_loop, kwargs=kwargs)
        thread.start()
        output_box.insert(
            tk.END, f"[{time.strftime('%D %H:%M:%S')}] Starting the bot...")
        start_btn["text"] = "Stop"
    else:
        output_box.insert(
            tk.END, f"[{time.strftime('%D %H:%M:%S')}] Stopping the bot...")
        start_btn["text"] = "Stopping..."
        start_btn["state"] = "disabled"

        win.after(1000, reset)  # wait for bot to finish


def reset():
    """
    Resets to default start button
    """
    if threading.active_count() > 1:
        return win.after(1000, reset)
    start_btn["text"] = "Start"
    start_btn["state"] = "normal"


""" === Window Setup === """
win = tk.Tk()
win.title("Reddit Bot")
win.geometry("860x500")
win.resizable(False, False)
win.iconbitmap("./reddit.ico")

# --- Canvas --- #
canv = tk.Canvas(win, width=860, height=600)
canv.place(x=0, y=0)
canv.create_rectangle(10, 10, 450, 100)
canv.create_rectangle(10, 120, 450, 200)
canv.create_rectangle(10, 210, 450, 340)
canv.create_rectangle(10, 350, 450, 490)

# --- Time Settings --- #
time_infos = [(15, 15, "Random Wait Min", 60),
              (150, 15, "Random Wait Max", 300),
              (290, 15, "Action timeout", 10),
              ]
time_labels = []
entries = []
for x, y, text, amount in time_infos:
    label = tk.Label(win, text=text)
    label.place(x=x, y=y)
    time_labels.append(label)

    entry = tk.Entry(win, width=12)
    entry.insert(0, amount)
    entry.place(x=x+10, y=y+30)
    entries.append(entry)

# --- Post options --- #
post_infos = [(15, 125, "Post OC"),
              (100, 125, "Post Spoiler"),
              (200, 125, "Post NSFW"),
              (300, 125, "Post Flair"),
              ]
post_labels = []
post_checkbox = []
post_variables = [tk.IntVar() for i in range(len(post_infos))]
i = 0
for x, y, text in post_infos:
    label = tk.Label(win, text=text)
    label.place(x=x, y=y)
    post_labels.append(label)

    check_btn = tk.Checkbutton(win, variable=post_variables[i])
    check_btn.place(x=x+25, y=y+30)
    post_checkbox.append(check_btn)
    i += 1

# --- Proxies / Driver restart / File / Headless --- #

proxy_var = tk.IntVar()
proxy_label = tk.Label(win, text="Proxy :")
proxy_label.place(x=15, y=225)
proxy_checkbox = tk.Checkbutton(win, variable=proxy_var)
proxy_checkbox.place(x=70, y=225)

restart_label = tk.Label(win, text="Time before restart :")
restart_label.place(x=100, y=225)
restart_entry = tk.Entry(win, width=14)
restart_entry.insert(0, "900")
restart_entry.place(x=290, y=225)

file_label = tk.Label(win, text="Image/Video file (leave blank for none) :")
file_label.place(x=15, y=260)
file_entry = tk.Entry(win, width=14)
file_entry.place(x=290, y=260)

headless_var = tk.IntVar()
headless_label = tk.Label(win, text="Headless :")
headless_label.place(x=15, y=300)
headless_checkbox = tk.Checkbutton(win, variable=headless_var)
headless_checkbox.place(x=100, y=300)

# --- Used Files --- #
files_info = [(15, 355, "Login file :                ./settings/login.txt"),
              (15, 355, "Message titles file :       ./settings/post_titles.txt"),
              (15, 355, "Subreddits file :           ./settings/subreddits.txt"),
              (15, 355, "Static content :              ./settings/static_content.txt"),
              (15, 355, "Proxies file :              ./settings/proxies.txt")
              ]

info_labels = []
for i, file_info in enumerate(files_info):
    x, y, text = file_info
    label = tk.Label(win, text=text, anchor="w")
    label.place(x=x, y=y+i*25)
    info_labels.append(label)

# --- Start/Stop Button --- #
start_btn = tk.Button(win, text="Start", command=start)
start_btn.place(x=480, y=15)

# --- Output --- #
output_box = tk.Listbox(win, width=40, height=15)
output_box.place(x=480, y=120)

win.mainloop()
