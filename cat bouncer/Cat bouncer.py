import os
import random
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk  # 🔹 added

# === CONFIG ===
CAT_FOLDER = r"C:\Users\S0156051\OneDrive - St Joseph's College, Gregory Terrace\cat picturs"
FPS_MS = 16
SCALE_FACTOR = 0.5  # 🔹 custom scaling (0.5 = half, 1.0 = original, 2.0 = double)

def pick_speed():
    speed = random.randint(3, 7)
    return speed if random.random() < 0.5 else -speed

# === BOUNCING CAT ===
class BounceCat:
    def __init__(self, root, img_path):
        self.root = root
        self.img_path = img_path

        # 🔹 Load image and apply custom scaling
        pil_img = Image.open(img_path)
        if SCALE_FACTOR != 1.0:
            new_w = int(pil_img.width * SCALE_FACTOR)
            new_h = int(pil_img.height * SCALE_FACTOR)
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(pil_img)
        self.w, self.h = self.tk_img.width(), self.tk_img.height()

        # Create Toplevel window
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.label = tk.Label(self.win, image=self.tk_img, bg="black")
        self.label.pack()

        self.win.update_idletasks()
        self.screen_w = self.win.winfo_screenwidth()
        self.screen_h = self.win.winfo_screenheight()

        self.x = random.randint(0, max(0, self.screen_w - self.w))
        self.y = random.randint(0, max(0, self.screen_h - self.h))
        self.vx = pick_speed()
        self.vy = pick_speed()

        self.win.geometry(f"{self.w}x{self.h}+{self.x}+{self.y}")
        self._alive = True
        self._tick()

    def _tick(self):
        if not self._alive:
            return
        self.x += self.vx
        self.y += self.vy

        if self.x <= 0 or self.x + self.w >= self.screen_w:
            self.vx *= -1
        if self.y <= 0 or self.y + self.h >= self.screen_h:
            self.vy *= -1

        self.win.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.win.after(FPS_MS, self._tick)

    def destroy(self):
        self._alive = False
        try:
            self.win.destroy()
        except Exception:
            pass

# === MAIN APP ===
class CatApp:
    def __init__(self, root, max_cats):
        self.root = root
        self.cats = []
        self.spawned_count = 0
        self.max_cats = max_cats

        # Control window
        self.ctrl = tk.Toplevel(root)
        self.ctrl.title("Bouncing Cats — E=spawn Q=clear Esc=quit")
        self.ctrl.geometry("420x150+50+50")
        self.ctrl.configure(bg="#111")

        self.label_info = tk.Label(
            self.ctrl,
            text="🐈 Bouncing Cats\nE → spawn cat   |   Q → clear cats   |   Esc → quit",
            fg="white",
            bg="#111",
            justify="left"
        )
        self.label_info.pack(padx=10, pady=5, anchor="w")

        self.counter_label = tk.Label(
            self.ctrl,
            text="Cats spawned: 0",
            fg="cyan",
            bg="#111",
            font=("Consolas", 12, "bold")
        )
        self.counter_label.pack(pady=5, anchor="w")

        # Load images (PNG + GIF only)
        self.img_files = [os.path.join(CAT_FOLDER, f) for f in os.listdir(CAT_FOLDER)
                          if f.lower().endswith((".png", ".gif"))]
        if not self.img_files:
            messagebox.showwarning("No images", f"No PNG or GIF images found in:\n{CAT_FOLDER}")

        root.bind_all("<KeyPress>", self._on_key)
        self.spawn_cat()

    def _on_key(self, event):
        key = (event.keysym or "").lower()
        if key == "e":
            self.spawn_cat()
        elif key == "q":
            self.clear_cats()
        elif key == "escape":
            self.quit_app()

    def spawn_cat(self):
        if not self.img_files:
            return

        if self.spawned_count >= self.max_cats:
            self.trigger_bluescreen()
            return

        path = random.choice(self.img_files)
        try:
            cat = BounceCat(self.root, path)
        except Exception:
            return  # skip broken image

        self.cats.append(cat)
        self.spawned_count += 1
        self.counter_label.config(
            text=f"Cats spawned: {self.spawned_count} / {self.max_cats}"
        )

        if self.spawned_count >= self.max_cats:
            self.trigger_bluescreen()

    def clear_cats(self):
        for c in self.cats:
            c.destroy()
        self.cats.clear()

    def quit_app(self):
        self.clear_cats()
        self.root.quit()

    def trigger_bluescreen(self):
        self.clear_cats()
        bsod = tk.Toplevel(self.root)
        bsod.attributes("-fullscreen", True)
        bsod.configure(bg="#0000AA")

        tk.Label(bsod, text=":(", fg="white", bg="#0000AA",
                 font=("Segoe UI", 120, "bold")).pack(pady=20, padx=50, anchor="w")

        msg = ("Your PC ran into a problem and needs to restart.\n"
               "We're just collecting some error info, and then we'll restart for you.")
        tk.Label(bsod, text=msg, fg="white", bg="#0000AA",
                 font=("Segoe UI", 22), justify="left").pack(pady=20, padx=50, anchor="w")

        progress = tk.Label(bsod, text="0% complete",
                            fg="white", bg="#0000AA", font=("Segoe UI", 20))
        progress.pack(pady=10, padx=50, anchor="w")

        def fake_progress(i=0):
            if i <= 100:
                progress.config(text=f"{i}% complete")
                bsod.after(50, fake_progress, i + 1)

        fake_progress()

        try:
            qr_img = tk.PhotoImage(file="rickroll_qr.png")
            qr_label = tk.Label(bsod, image=qr_img, bg="#0000AA")
            qr_label.image = qr_img
            qr_label.pack(pady=20, side="right", anchor="e")
        except Exception:
            pass

        tk.Label(bsod, text="Stop Code: TOO_MANY_CATS",
                 fg="white", bg="#0000AA", font=("Segoe UI", 18, "bold"),
                 justify="left").pack(pady=10, padx=50, anchor="w")

        bsod.bind("<Escape>", lambda e: self.quit_app())

# === MAIN ===
def main():
    root = tk.Tk()
    root.withdraw()

    max_cats = simpledialog.askinteger(
        "Cat Limit",
        "Enter max number of cats before BSOD:",
        minvalue=10,
        maxvalue=100000,
        initialvalue=1000
    )
    if not max_cats:
        max_cats = 1000

    CatApp(root, max_cats)
    root.mainloop()

if __name__ == "__main__":
    main()
