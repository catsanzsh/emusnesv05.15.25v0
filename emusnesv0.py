import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess

class SNESEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("EMUSNESV0.1")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.bg_color = "#343434"
        self.accent_color = "#6D2D92"
        self.text_color = "#FFFFFF"
        self.button_color = "#565656"
        
        self.root.configure(bg=self.bg_color)
        
        self.current_rom = None
        self.is_running = False
        self.emulator_path = None
        self.emulator_process = None
        
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.root.bind("<space>", self.toggle_emulation)
        self.root.bind("r", self.reset_emulation)
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM...", command=self.open_rom)
        file_menu.add_command(label="Recent ROMs", command=self.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        emulation_menu = tk.Menu(menubar, tearoff=0)
        emulation_menu.add_command(label="Start", command=self.start_emulation)
        emulation_menu.add_command(label="Pause", command=self.not_implemented)
        emulation_menu.add_command(label="Reset", command=self.reset_emulation)
        menubar.add_cascade(label="Emulation", menu=emulation_menu)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Set Emulator Path...", command=self.set_emulator_path)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_main_frame(self):
        """Create the main display frame"""
        self.main_frame = tk.Frame(self.root, bg=self.bg_color, width=600, height=340)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_frame.pack_propagate(False)
        
        self.rom_info_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.rom_info_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.rom_label = tk.Label(self.rom_info_frame, text="No ROM loaded", fg=self.text_color, bg=self.bg_color, font=("Arial", 10, "bold"))
        self.rom_label.pack(side=tk.LEFT)
        
        self.display_frame = tk.Frame(self.main_frame, bg="black", width=512, height=240)
        self.display_frame.pack(fill=tk.BOTH, expand=True)
        self.display_frame.pack_propagate(False)
        
        self.canvas = tk.Canvas(self.display_frame, bg="black", width=512, height=240)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_message("EMUSNESV0.1\nSelect File > Open ROM to load a SNES game\nSet emulator path in Settings > Set Emulator Path...")
        
        self.controls_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        button_style = {"bg": self.button_color, "fg": self.text_color, "width": 8, 
                        "relief": tk.RAISED, "padx": 5, "pady": 3, "borderwidth": 2}
        
        self.start_button = tk.Button(self.controls_frame, text="Start", command=self.start_emulation, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        self.start_button.bind("<Enter>", lambda e: self.status_label.config(text="Start emulation"))
        self.start_button.bind("<Leave>", lambda e: self.status_label.config(text=""))
        
        self.pause_button = tk.Button(self.controls_frame, text="Pause", command=self.not_implemented, **button_style)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.pause_button.bind("<Enter>", lambda e: self.status_label.config(text="Pause emulation (not supported)"))
        self.pause_button.bind("<Leave>", lambda e: self.status_label.config(text=""))
        
        self.reset_button = tk.Button(self.controls_frame, text="Reset", command=self.reset_emulation, **button_style)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.bind("<Enter>", lambda e: self.status_label.config(text="Reset emulation"))
        self.reset_button.bind("<Leave>", lambda e: self.status_label.config(text=""))
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Frame(self.root, bg=self.accent_color, height=20)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", bg=self.accent_color, fg=self.text_color, anchor=tk.W, padx=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.fps_label = tk.Label(self.status_bar, text="FPS: --", bg=self.accent_color, fg=self.text_color, padx=5)
        self.fps_label.pack(side=tk.RIGHT)
    
    def draw_message(self, text):
        """Draw multi-line text on the canvas with a 'message' tag"""
        self.canvas.delete("message")
        lines = text.split('\n')
        y = 100
        for i, line in enumerate(lines):
            self.canvas.create_text(
                256, y + i * 30,
                text=line,
                fill="white",
                font=("Arial", 12),
                tags="message"
            )
    
    def set_emulator_path(self):
        """Set the path to the SNES emulator executable"""
        emulator_path = filedialog.askopenfilename(
            title="Select SNES Emulator Executable",
            filetypes=[("Executable files", "*.exe" if os.name == 'nt' else "*")]
        )
        if emulator_path:
            self.emulator_path = emulator_path
            messagebox.showinfo("Emulator Path Set", f"Emulator path set to: {emulator_path}")
        else:
            messagebox.showwarning("No File Selected", "No emulator executable selected.")
    
    def open_rom(self):
        """Open a ROM file"""
        filetypes = [
            ("SNES ROM files", "*.sfc *.smc"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select SNES ROM",
            filetypes=filetypes
        )
        
        if filename and os.path.isfile(filename) and (filename.lower().endswith('.sfc') or filename.lower().endswith('.smc')):
            self.current_rom = filename
            rom_name = os.path.basename(filename)
            self.rom_label.config(text=f"ROM: {rom_name}")
            self.status_label.config(text=f"Loaded: {rom_name}")
            self.is_running = False
            self.reset_emulation()
        else:
            messagebox.showerror("Invalid File", "Please select a valid .sfc or .smc file.")
    
    def start_emulation(self):
        """Start emulation by launching external emulator"""
        if not self.current_rom:
            messagebox.showinfo("No ROM", "Please open a ROM file first.")
            return
        
        if not self.emulator_path:
            messagebox.showwarning("Emulator Not Set", "Please set the emulator path in Settings > Set Emulator Path...")
            return
        
        try:
            self.emulator_process = subprocess.Popen([self.emulator_path, self.current_rom])
            self.is_running = True
            self.status_label.config(text=f"Running: {os.path.basename(self.current_rom)} (external)")
            self.fps_label.config(text="FPS: N/A")
            self.check_emulator_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch emulator: {str(e)}")
    
    def check_emulator_status(self):
        """Periodically check if the emulator process is still running"""
        if self.is_running and self.emulator_process.poll() is None:
            self.root.after(100, self.check_emulator_status)
        else:
            self.is_running = False
            self.status_label.config(text=f"Emulation stopped: {os.path.basename(self.current_rom)}")
            self.fps_label.config(text="FPS: --")
    
    def reset_emulation(self, event=None):
        """Reset emulation"""
        self.is_running = False
        if self.emulator_process and self.emulator_process.poll() is None:
            self.emulator_process.terminate()
        self.canvas.delete("all")
        if self.current_rom:
            rom_name = os.path.basename(self.current_rom)
            self.draw_message(f"ROM loaded: {rom_name}\nPress Start to begin emulation")
            self.status_label.config(text=f"Reset: {rom_name}")
        else:
            self.draw_message("EMUSNESV0.1\nSelect File > Open ROM to load a SNES game\nSet emulator path in Settings > Set Emulator Path...")
            self.status_label.config(text="Ready")
    
    def toggle_emulation(self, event):
        """Toggle between start and pause emulation"""
        if self.is_running:
            self.not_implemented()  # Pause not supported for external emulation
        else:
            self.start_emulation()
    
    def not_implemented(self):
        """Placeholder for features not implemented"""
        messagebox.showinfo("Not Implemented", "This feature is not implemented in this version.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """EMUSNESV0.1

A simple SNES emulator launcher created with Tkinter.
        
This application allows you to select and launch SNES ROMs with an external emulator.

Developed as a demonstration of Tkinter capabilities."""
        messagebox.showinfo("About EMUSNESV0.1", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SNESEmulator(root)
    root.mainloop()
