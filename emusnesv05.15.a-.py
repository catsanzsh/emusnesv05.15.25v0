import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from PIL import Image, ImageTk, ImageDraw
import ctypes
import time

# Enhanced Custom SNES Core with interactive vibes
class CustomSNESCore:
    def __init__(self):
        self.frame_width = 256
        self.frame_height = 224
        self.player_x = 128  # Starting position of our vibe box
        self.player_y = 112
        self.player_speed = 2
        self.last_update = time.time()

    def load_game(self, rom_path):
        pass  # No ROM loading in fallback mode

    def run(self):
        # Update every ~16ms (60 FPS vibes)
        current_time = time.time()
        if current_time - self.last_update > 0.016:
            self.last_update = current_time
            # Movement happens via set_input_state

    def get_video_frame(self):
        # Draw a dynamic frame with a controllable box
        img = Image.new('RGB', (self.frame_width, self.frame_height), 'black')
        draw = ImageDraw.Draw(img)
        draw.rectangle([self.player_x, self.player_y, self.player_x + 20, self.player_y + 20], fill='blue')
        draw.text((10, 10), "Custom Core Active - VIBE MODE", fill='white')
        draw.text((10, 30), "Arrow keys to move the box!", fill='white')
        return img.tobytes()

    def reset(self):
        self.player_x = 128
        self.player_y = 112

    def set_input_state(self, button, state):
        # Move the box based on arrow key input
        if button == 12 and state:  # Up
            self.player_y -= self.player_speed
        elif button == 13 and state:  # Down
            self.player_y += self.player_speed
        elif button == 14 and state:  # Left
            self.player_x -= self.player_speed
        elif button == 15 and state:  # Right
            self.player_x += self.player_speed
        # Keep the box in bounds
        self.player_x = max(0, min(self.player_x, self.frame_width - 20))
        self.player_y = max(0, min(self.player_y, self.frame_height - 20))

# Libretro Core (still a placeholder)
class Core:
    def __init__(self, path):
        try:
            self.lib = ctypes.CDLL(path)
            self.frame_width, self.frame_height = 256, 224
        except OSError as e:
            raise Exception(f"Failed to load core: {e}")
    
    def load_game(self, rom_path):
        pass
    
    def run(self):
        pass
    
    def get_video_frame(self):
        return b'\x00' * (self.frame_width * self.frame_height * 3)
    
    def reset(self):
        pass
    
    def set_input_state(self, button, state):
        pass

class SNESEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("EMUSNESV0.1 - VIBE EDITION")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.bg_color = "#343434"
        self.text_color = "#FFFFFF"
        self.button_color = "#565656"
        self.accent_color = "#6D2D92"
        self.root.configure(bg=self.bg_color)
        
        self.current_rom = None
        self.is_running = False
        self.core = None
        self.core_path = None
        self.core_type = None
        
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        self.root.bind("<space>", self.toggle_emulation)
        self.root.bind("r", self.reset_emulation)
        self.root.bind("<KeyPress>", self.handle_input)
        self.root.bind("<KeyRelease>", self.handle_input)

        self.core_path = self.find_core_path()

    def find_core_path(self):
        core_file = "snes9x_libretro.dll"
        search_paths = [
            r"C:\RetroArch-Win64\cores",  # Winget default installation path
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "cores"),
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "RetroArch", "cores"),
            os.path.join(os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming")), "RetroArch", "cores"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "RetroArch", "cores"),
        ]
        path_env = os.environ.get("PATH", "").split(os.pathsep)
        search_paths.extend(path_env)
        
        for path in search_paths:
            try:
                core_path = os.path.join(path, core_file)
                if os.path.exists(core_path):
                    return core_path
            except (OSError, TypeError):
                continue
        
        return None  # Core not found, handle in start_emulation

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM...", command=self.open_rom)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg=self.bg_color, width=600, height=340)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_frame.pack_propagate(False)
        
        self.rom_label = tk.Label(self.main_frame, text="No ROM loaded", fg=self.text_color, 
                                 bg=self.bg_color, font=("Arial", 10, "bold"))
        self.rom_label.pack(side=tk.TOP, pady=(0, 10))
        
        self.canvas = tk.Canvas(self.main_frame, bg="black", width=512, height=240)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_message("EMUSNESV0.1 - VIBE EDITION\nSelect File > Open ROM to start")
        
        self.controls_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        tk.Button(self.controls_frame, text="Start", bg=self.button_color, fg=self.text_color, 
                  command=self.start_emulation).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Pause", bg=self.button_color, fg=self.text_color, 
                  command=self.pause_emulation).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Reset", bg=self.button_color, fg=self.text_color, 
                  command=self.reset_emulation).pack(side=tk.LEFT, padx=5)

    def create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=self.accent_color, height=20)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_bar, text="Ready", bg=self.accent_color, 
                                    fg=self.text_color, anchor=tk.W, padx=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def draw_message(self, text):
        self.canvas.delete("all")
        lines = text.split('\n')
        y = 100
        for i, line in enumerate(lines):
            self.canvas.create_text(256, y + i * 30, text=line, fill="white", font=("Arial", 12))

    def open_rom(self):
        filetypes = [("SNES ROM files", "*.sfc *.smc"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select SNES ROM", filetypes=filetypes)
        if filename and os.path.isfile(filename) and filename.lower().endswith(('.sfc', '.smc')):
            self.current_rom = filename
            rom_name = os.path.basename(filename)
            self.rom_label.config(text=f"ROM: {rom_name}")
            self.status_label.config(text=f"Loaded: {rom_name}")
            self.is_running = False
            self.core = None
            self.reset_emulation()
        else:
            messagebox.showerror("Invalid File", "Please select a valid .sfc or .smc file.")

    def start_emulation(self):
        if not self.current_rom:
            messagebox.showinfo("No ROM", "Load a ROM first!")
            return
        
        if self.core_path is None:
            messagebox.showwarning("404 No Libretro", 
                "snes9x_libretro.dll not found. Using VIBE MODE custom core.\n\n"
                "For full SNES action, install RetroArch via Winget and ensure the core is in C:\\RetroArch-Win64\\cores.")
            self.core = CustomSNESCore()
            self.core_type = "Custom Core"
        else:
            try:
                self.core = Core(self.core_path)
                self.core_type = "Libretro Core"
            except Exception as e:
                messagebox.showwarning("Core Load Failed", 
                    f"Failed to load core: {e}. Switching to VIBE MODE custom core!")
                self.core = CustomSNESCore()
                self.core_type = "Custom Core"
        
        self.core.load_game(self.current_rom)
        self.is_running = True
        self.status_label.config(text=f"Running: {os.path.basename(self.current_rom)} ({self.core_type})")
        self.emulation_loop()

    def emulation_loop(self):
        if not self.is_running or not self.core:
            return
        self.core.run()
        frame_data = self.core.get_video_frame()
        if frame_data:
            img = Image.frombytes("RGB", (self.core.frame_width, self.frame_height), frame_data)
            img = img.resize((512, 240), Image.NEAREST)
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(256, 120, image=self.photo)
        self.root.after(16, self.emulation_loop)

    def pause_emulation(self):
        if self.is_running:
            self.is_running = False
            self.status_label.config(text=f"Paused: {os.path.basename(self.current_rom)} ({self.core_type})")

    def reset_emulation(self, event=None):
        self.is_running = False
        if self.core:
            self.core.reset()
        self.canvas.delete("all")
        if self.current_rom:
            rom_name = os.path.basename(self.current_rom)
            self.draw_message(f"ROM loaded: {rom_name}\nPress Start to vibe")
            self.status_label.config(text=f"Reset: {rom_name}" + 
                                   (f" ({self.core_type})" if self.core_type else ""))
        else:
            self.draw_message("EMUSNESV0.1 - VIBE EDITION\nSelect File > Open ROM to start")
            self.status_label.config(text="Ready")

    def toggle_emulation(self, event):
        if self.is_running:
            self.pause_emulation()
        else:
            self.start_emulation()

    def handle_input(self, event):
        if not self.is_running or not self.core:
            return
        key_map = {
            "Up": 12, "Down": 13, "Left": 14, "Right": 15,  # For custom core movement
            "z": 0, "x": 1, "Return": 8  # For Libretro core (A, B, Start)
        }
        if event.keysym in key_map:
            button = key_map[event.keysym]
            state = 1 if event.type == tk.EventType.KeyPress else 0
            self.core.set_input_state(button, state)

if __name__ == "__main__":
    root = tk.Tk()
    app = SNESEmulator(root)
    root.mainloop()
