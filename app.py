import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
import cv2
from ultralytics import YOLO
from pathlib import Path
import threading
import time
import random
import platform


# PATH CONFIG
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best.pt"

# Load YOLO model
model = YOLO(str(MODEL_PATH))

# Unified stop flag for all feeds
stop_all = False
animation_running = False


# CLASS LIST (5 CLASSES)
CLASS_NAMES = ["Grenade", "Knife", "Missile", "Pistol", "Rifle"]


# MATRIX HACKER THEME COLORS
BG = "#020b02"
SIDEBAR_BG = "#020f06"
PANEL_BG = "#031a09"
BTN_BG = "#052b11"
BTN_HOVER = "#0a3d1a"
TEXT = "#00ff41"
MUTED = "#00aa55"
ACCENT = "#00ff41"
ACCENT_SOFT = "#004d1f"

# Global UI refs
panel = None
status_label = None
detail_label = None
log_text = None
loader_canvas = None
log_images = []  # Prevent garbage-collection

angle = 0


# SOUND (Beep)
def play_beep():
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1200, 120)  # (frequency, duration)
        else:
            root.bell()
    except:
        try:
            root.bell()
        except:
            pass



#  SYSTEM LOG TEXT
def log(msg: str):
    if log_text is None:
        return
    log_text.config(state="normal")
    prefix = random.choice(["[MATRIX]", "[CORE]", "[NODE-01]", "[SYS]", "[SCAN]"])
    log_text.insert("end", f"{prefix} {msg}\n")
    log_text.see("end")
    log_text.config(state="disabled")



#  SCI-FI THUMBNAIL EFFECT
def add_thumbnail_to_log(pil_img: Image.Image, label: str):
    try:
        # Resize to thumbnail
        thumb = pil_img.copy()
        thumb.thumbnail((150, 100))

        # Apply slight green tint
        enhancer = ImageEnhance.Color(thumb)
        thumb = enhancer.enhance(1.5)

        # Add neon border
        border = 4
        neon_img = Image.new("RGB", (thumb.width + border*2, thumb.height + border*2), (0, 40, 0))
        neon_img.paste(thumb, (border, border))

        # Add scanlines
        px = neon_img.load()
        for y in range(0, neon_img.height, 3):
            for x in range(neon_img.width):
                r, g, b = px[x, y]
                px[x, y] = (r//3, g//3, b//3)

        # Convert final sci-fi frame to Tk object
        imgtk = ImageTk.PhotoImage(neon_img)
        log_images.append(imgtk)

        log_text.config(state="normal")
        log_text.image_create("end", image=imgtk)
        log_text.insert("end", f"  {label}\n\n")
        log_text.see("end")
        log_text.config(state="disabled")

    except Exception as e:
        log(f"ERROR sci-fi thumbnail -> {e}")



# LOADER ANIMATION
def start_loader():
    global animation_running, loader_canvas
    if animation_running:
        return

    animation_running = True

    loader_canvas = tk.Canvas(panel, width=200, height=200, bg=PANEL_BG, highlightthickness=0)
    loader_canvas.place(relx=0.5, rely=0.5, anchor="center")
    animate_loader()


def stop_loader():
    global animation_running, loader_canvas
    animation_running = False
    if loader_canvas:
        loader_canvas.destroy()
        loader_canvas = None


def animate_loader():
    global angle, animation_running

    if not animation_running or loader_canvas is None:
        return

    loader_canvas.delete("all")

    cx, cy = 100, 100
    r1, r2 = 60, 40

    # Outer ring
    loader_canvas.create_oval(cx-r1, cy-r1, cx+r1, cy+r1, outline=ACCENT, width=3)

    # Arc
    loader_canvas.create_arc(cx-r1, cy-r1, cx+r1, cy+r1,
                             start=angle, extent=110,
                             style="arc", outline=ACCENT, width=5)

    # Inner circle
    loader_canvas.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, outline=MUTED, width=2)

    loader_canvas.create_text(cx, cy+50, text="SCANNING...", fill=ACCENT,
                              font=("Consolas", 10, "bold"))

    angle = (angle + 12) % 360
    loader_canvas.after(40, animate_loader)



# BUTTON HOVER
def on_enter(event):
    event.widget["background"] = BTN_HOVER


def on_leave(event):
    event.widget["background"] = BTN_BG



# SHOW IMAGE (MAIN DISPLAY)
def show_image(path: Path):
    try:
        img = Image.open(path).resize((800, 500))
        img_tk = ImageTk.PhotoImage(img)
        panel.config(image=img_tk)
        panel.image = img_tk
    except Exception as e:
        log(f"ERROR showing image -> {e}")



# IMAGE DETECTION
def detect_image():

    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Images", "*.jpg *.jpeg *.png")]
    )
    if not file_path:
        return

    log(f"Image selected: {file_path}")

    status_label.config(text="STATUS: IMAGE SCAN ACTIVE")
    detail_label.config(text="DETAIL: Running model...")
    start_loader()
    root.update_idletasks()

    try:
        results = model.predict(file_path, save=True)

        r = results[0]
        saved_dir = Path(r.save_dir)
        stem = Path(file_path).stem

        # Find YOLO output image
        candidates = list(saved_dir.glob(f"{stem}.*"))
        output = candidates[0] if candidates else sorted(saved_dir.glob("*"))[-1]

        # Show full image
        show_image(output)

        detected_class = None
        conf_val = 0

        for box in r.boxes:
            cls = int(box.cls[0])
            conf_val = float(box.conf[0]) * 100
            detected_class = CLASS_NAMES[cls]

        if detected_class:
            status_label.config(text=f"STATUS: {detected_class} DETECTED")
            detail_label.config(text=f"CONFIDENCE: {conf_val:.2f}%")
            log(f"Detected: {detected_class} ({conf_val:.2f}%)")

            pil_img = Image.open(output).convert("RGB")
            timestamp = time.strftime("%H:%M:%S")
            add_thumbnail_to_log(pil_img, f"{timestamp} — {detected_class}")

            play_beep()

        else:
            status_label.config(text="STATUS: NO DETECTION")
            detail_label.config(text="DETAIL: No weapon found.")
            log("No weapon detected.")

    except Exception as e:
        log(f"ERROR: {e}")

    finally:
        stop_loader()



# VIDEO DETECTION (threaded)
def detect_video():
    """
    Called from main thread (UI). It asks for file and then spawns
    a background thread to process the video so UI doesn't freeze.
    """
    file_path = filedialog.askopenfilename(
        title="Select Video",
        filetypes=[("Videos", "*.mp4 *.avi *.mkv *.mov")]
    )
    if not file_path:
        return

    # start thread to process the video
    t = threading.Thread(target=process_video, args=(file_path,))
    t.daemon = True
    t.start()


def process_video(file_path: str):
    global stop_all
    stop_all = False

    log(f"Video selected: {file_path}")
    status_label.config(text="STATUS: VIDEO SCAN ACTIVE")
    detail_label.config(text="DETAIL: Processing video frames...")

    start_loader()
    root.update_idletasks()
    time.sleep(0.5)
    stop_loader()

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        status_label.config(text="STATUS: ERROR")
        detail_label.config(text="DETAIL: Cannot open video file.")
        log("ERROR: Cannot open video file.")
        return

    log("Video detection started.")

    try:
        while not stop_all:
            ret, frame = cap.read()
            if not ret:
                break

            # Run YOLO on the frame
            try:
                result = model(frame)[0]
            except Exception as e:
                log(f"Model inference error: {e}")
                break

            plotted = result.plot()
            rgb = cv2.cvtColor(plotted, cv2.COLOR_BGR2RGB)

            # Convert to PIL -> ImageTk
            img = Image.fromarray(rgb).resize((800, 500))
            imgtk = ImageTk.PhotoImage(img)

            # Update panel (must be done from main thread but config is thread-safe enough here;
            # if you see issues, use root.after to schedule GUI updates)
            panel.config(image=imgtk)
            panel.image = imgtk

            # If detection present
            if len(result.boxes) > 0:
                try:
                    cls = int(result.boxes[0].cls[0])
                    conf = float(result.boxes[0].conf[0]) * 100
                    det_name = CLASS_NAMES[cls]
                except Exception:
                    det_name = "Unknown"
                    conf = 0.0

                status_label.config(text=f"STATUS: {det_name} DETECTED")
                detail_label.config(text=f"CONFIDENCE: {conf:.2f}%")
                log(f"Video detected: {det_name} ({conf:.2f}%)")

                # Add thumbnail to log
                pil_frame = Image.fromarray(rgb)
                timestamp = time.strftime("%H:%M:%S")
                add_thumbnail_to_log(pil_frame, f"{timestamp} — {det_name}")

                play_beep()
            else:
                status_label.config(text="STATUS: VIDEO SCAN ACTIVE")
                detail_label.config(text="DETAIL: Scanning frames...")

            # Allow UI events to process
            root.update_idletasks()
            time.sleep(0.01)

        # Feed ended or stopped
        if stop_all:
            status_label.config(text="STATUS: VIDEO STOPPED")
            detail_label.config(text="DETAIL: Feed stopped by user.")
            log("Video stopped by user.")
        else:
            status_label.config(text="STATUS: VIDEO COMPLETED")
            detail_label.config(text="DETAIL: All frames processed.")
            log("Video processing finished.")

    except Exception as e:
        log(f"ERROR video detection -> {e}")

    finally:
        cap.release()



# WEBCAM DETECTION (already threaded by start_webcam)
def run_webcam():

    global stop_all
    stop_all = False

    log("Starting webcam...")
    status_label.config(text="STATUS: LIVE MATRIX FEED")
    detail_label.config(text="DETAIL: Camera connected.")

    start_loader()
    time.sleep(0.5)
    stop_loader()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log("ERROR: Webcam not found.")
        status_label.config(text="STATUS: ERROR")
        detail_label.config(text="DETAIL: Webcam not found.")
        return

    log("Webcam Online.")

    try:
        while not stop_all:
            ret, frame = cap.read()
            if not ret:
                break

            try:
                result = model(frame)[0]
            except Exception as e:
                log(f"Model inference error (webcam): {e}")
                break

            plotted = result.plot()
            rgb = cv2.cvtColor(plotted, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(rgb).resize((800, 500))
            imgtk = ImageTk.PhotoImage(img)
            panel.config(image=imgtk)
            panel.image = imgtk

            if len(result.boxes) > 0:
                try:
                    cls = int(result.boxes[0].cls[0])
                    conf = float(result.boxes[0].conf[0]) * 100
                    current_class = CLASS_NAMES[cls]
                except Exception:
                    current_class = "Unknown"
                    conf = 0.0

                status_label.config(text=f"STATUS: {current_class} DETECTED")
                detail_label.config(text=f"CONFIDENCE: {conf:.2f}%")
                log(f"Webcam detected: {current_class} ({conf:.2f}%)")

                pil_frame = Image.fromarray(rgb)
                timestamp = time.strftime("%H:%M:%S")
                add_thumbnail_to_log(pil_frame, f"{timestamp} — {current_class}")

                play_beep()
            else:
                status_label.config(text="STATUS: LIVE MATRIX FEED")
                detail_label.config(text="DETAIL: Scanning...")

            root.update_idletasks()
            time.sleep(0.01)

    finally:
        cap.release()
        status_label.config(text="STATUS: FEED TERMINATED")
        detail_label.config(text="DETAIL: Connection closed.")
        log("Webcam stopped.")


def start_webcam():
    t = threading.Thread(target=run_webcam)
    t.daemon = True
    t.start()



# STOP ALL FEEDS (single button)
def stop_all_func():
    global stop_all
    stop_all = True
    log("STOP command received: Stopping all feeds.")


# UI BUILDING
root = tk.Tk()
root.title("MATRIX // WEAPON-DETECTION NODE // YOLOv8")
root.state("zoomed")
root.configure(bg=BG)

# --- Header ---
header = tk.Frame(root, bg=BG)
header.pack(fill="x", pady=10, padx=15)

tk.Label(header, text="MATRIX WEAPON DETECTION CONSOLE",
         fg=ACCENT, bg=BG, font=("Consolas", 20, "bold")).pack(side="left")

tk.Label(header, text="ENGINE: YOLOv8   NODE: ACTIVE",
         fg=MUTED, bg=BG, font=("Consolas", 10)).pack(side="left", padx=20)

# Sci-fi line
tk.Frame(root, bg=ACCENT, height=2).pack(fill="x", padx=15, pady=10)

# --- Main Layout ---
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=15, pady=10)

# Sidebar
sidebar = tk.Frame(main, bg=SIDEBAR_BG, width=330)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(sidebar, text="> CONTROL PANEL", fg=ACCENT,
         bg=SIDEBAR_BG, font=("Consolas", 14, "bold")).pack(anchor="w", padx=20, pady=15)

btn_box = tk.Frame(sidebar, bg=SIDEBAR_BG)
btn_box.pack(fill="x", padx=20, pady=10)


def make_btn(name, cmd):
    b = tk.Button(btn_box, text=name, command=cmd,
                  fg=TEXT, bg=BTN_BG, bd=0, relief="flat",
                  font=("Consolas", 11), pady=7)
    b.pack(fill="x", pady=6)
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    return b


make_btn("▣ IMAGE SCAN", detect_image)
make_btn("▣ VIDEO SCAN", detect_video)
make_btn("▣ LIVE WEBCAM", start_webcam)
make_btn("✘ STOP ALL FEEDS", stop_all_func)

# --- System Log ---
tk.Label(sidebar, text="\n> SYSTEM LOG", fg=ACCENT,
         bg=SIDEBAR_BG, font=("Consolas", 12, "bold")).pack(anchor="w", padx=20)

log_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
log_frame.pack(fill="both", expand=True, padx=15, pady=10)

log_text = tk.Text(log_frame, bg="#000000", fg=ACCENT,
                   font=("Consolas", 9), relief="flat", wrap="word")
log_text.pack(fill="both", expand=True)
log_text.config(state="disabled")

log("BOOT: MATRIX Online.")
log("YOLOv8 Node Initialized.")
log("Awaiting Commands...")

# --- Preview Panel ---
content = tk.Frame(main, bg=BG)
content.pack(side="left", fill="both", expand=True)

preview_outer = tk.Frame(content, bg=ACCENT_SOFT)
preview_outer.pack(pady=10)

preview_inner = tk.Frame(preview_outer, bg=PANEL_BG)
preview_inner.pack(padx=3, pady=3)

panel = tk.Label(preview_inner, bg=PANEL_BG, width=800, height=500)
panel.pack()

# --- Status Bar ---
status_frame = tk.Frame(content, bg=BG)
status_frame.pack(fill="x")

status_label = tk.Label(status_frame, text="STATUS: IDLE",
                        fg=ACCENT, bg=BG, font=("Consolas", 12, "bold"))
status_label.pack(fill="x")

detail_label = tk.Label(status_frame, text="DETAIL: Waiting for command...",
                        fg=MUTED, bg=BG, font=("Consolas", 9))
detail_label.pack(fill="x")

# --- Umar Credit INSIDE Status Bar ---
credit_label = tk.Label(status_frame,
                        text="Made with ❤️by Umar Team",
                        fg=ACCENT,
                        bg=BG,
                        font=("Consolas", 10, "bold"))
credit_label.pack(fill="x", pady=3)

root.mainloop()
