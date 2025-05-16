import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import winsound  # For basic audio (Windows)

# Simplified SNES Emulation Core
class Snes9xCore:
    def __init__(self):
        self.frame_width = 256
        self.frame_height = 224
        self.memory = bytearray(0x10000)  # 64KB RAM
        self.rom = bytearray()  # ROM data
        self.pc = 0x8000  # Program counter
        self.reg_a = 0  # Accumulator
        self.running = False
        self.last_frame = time.time()
        self.input_state = [0] * 16  # SNES controller buttons
        self.frame_buffer = [0] * (self.frame_width * self.frame_height)  # RGB pixels
        self.cycle_count = 0

    def load_game(self, rom_path):
        """Load a ROM file or use a hardcoded demo."""
        if rom_path and os.path.exists(rom_path):
            with open(rom_path, 'rb') as f:
                self.rom = bytearray(f.read())
        else:
            # Hardcoded demo: Move a red square and beep
            self.rom = bytearray([
                0xA9, 0x01,  # LDA #1 (move right)
                0x85, 0x10,  # STA $10 (store direction)
                0x4C, 0x00, 0x80  # JMP $8000 (loop)
            ])
        self.pc = 0x8000
        self.memory[0x10] = 0  # Direction variable
        self.memory[0x20] = 128  # X position
        self.memory[0x21] = 112  # Y position

    def reset(self):
        """Reset the emulator state."""
        self.pc = 0x8000
        self.reg_a = 0
        self.memory[0x10] = 0
        self.memory[0x20] = 128
        self.memory[0x21] = 112
        self.frame_buffer = [0] * (self.frame_width * self.frame_height)

    def set_input_state(self, button, state):
        """Update controller input state."""
        self.input_state[button] = state

    def run(self):
        """Execute one frame’s worth of instructions (simplified)."""
        if not self.running or not self.rom:
            return
        cycles_per_frame = 1000  # Simplified cycle count
        for _ in range(cycles_per_frame):
            if self.pc >= len(self.rom):
                self.pc = 0x8000
            opcode = self.rom[self.pc]
            self.pc += 1
            if opcode == 0xA9:  # LDA immediate
                self.reg_a = self.rom[self.pc]
                self.pc += 1
            elif opcode == 0x85:  # STA absolute
                addr = self.rom[self.pc]
                self.pc += 1
                self.memory[addr] = self.reg_a
            elif opcode == 0x4C:  # JMP absolute
                self.pc = (self.rom[self.pc + 1] << 8) | self.rom[self.pc]
            self.cycle_count += 1

        # Update game state based on input
        x, y = self.memory[0x20], self.memory[0x21]
        speed = 2
        if self.input_state[14]:  # Left
            x -= speed
        if self.input_state[15]:  # Right
            x += speed
        if self.input_state[12]:  # Up
            y -= speed
        if self.input_state[13]:  # Down
            y += speed
        x = max(0, min(x, self.frame_width - 20))
        y = max(0, min(y, self.frame_height - 20))
        self.memory[0x20], self.memory[0x21] = x, y

        # Generate audio (beep on A button)
        if self.input_state[0]:
            winsound.Beep(440, 10)  # 440 Hz for 10 ms

    def render_frame(self):
        """Render the frame buffer (software PPU)."""
        self.frame_buffer = [0] * (self.frame_width * self.frame_height)  # Clear buffer
        x, y = self.memory[0x20], self.memory[0x21]
        for dy in range(20):
            for dx in range(20):
                pos = (y + dy) * self.frame_width + (x + dx)
                if 0 <= pos < len(self.frame_buffer):
                    self.frame_buffer[pos] = 0xFF0000  # Red square

class Snes9xEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Snes9x Python - Tkinter Edition")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.bg_color = "#343434"
        self.text_color = "#FFFFFF"
        self.button_color = "#565656"
        self.accent_color = "#6D2D92"
        self.root.configure(bg=self.bg_color)

        self.core = Snes9xCore()
        self.current_rom = None
        self.is_running = False
        self.save_state = None

        self.create_gui()
        self.bind_inputs()

    def create_gui(self):
        """Set up the Tkinter GUI."""
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM...", command=self.open_rom)
        file_menu.add_command(label="Save State", command=self.save_state_func)
        file_menu.add_command(label="Load State", command=self.load_state_func)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.rom_label = tk.Label(self.main_frame, text="No ROM loaded", fg=self.text_color,
                                  bg=self.bg_color, font=("Arial", 10, "bold"))
        self.rom_label.pack(side=tk.TOP, pady=5)

        # Canvas for rendering
        self.canvas = tk.Canvas(self.main_frame, bg="black", width=512, height=448)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_message("Snes9x Python\nLoad a ROM to start")

        # Controls
        controls_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        controls_frame.pack(side=tk.BOTTOM, pady=10)
        tk.Button(controls_frame, text="Start", bg=self.button_color, fg=self.text_color,
                  command=self.start_emulation).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Pause", bg=self.button_color, fg=self.text_color,
                  command=self.pause_emulation).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Reset", bg=self.button_color, fg=self.text_color,
                  command=self.reset_emulation).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bg=self.accent_color,
                                   fg=self.text_color, anchor=tk.W, padx=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_inputs(self):
        """Bind keyboard inputs to SNES controls."""
        self.root.bind("<space>", self.toggle_emulation)
        self.root.bind("r", self.reset_emulation)
        key_map = {"Up": 12, "Down": 13, "Left": 14, "Right": 15, "z": 0, "x": 1, "Return": 8}
        for key, button in key_map.items():
            self.root.bind(f"<KeyPress-{key}>", lambda e, b=button: self.core.set_input_state(b, 1))
            self.root.bind(f"<KeyRelease-{key}>", lambda e, b=button: self.core.set_input_state(b, 0))

    def draw_message(self, text):
        """Display a text message on the canvas."""
        self.canvas.delete("all")
        lines = text.split("\n")
        y = 200
        for i, line in enumerate(lines):
            self.canvas.create_text(256, y + i * 30, text=line, fill="white", font=("Arial", 12))

    def open_rom(self):
        """Prompt user to select a ROM file."""
        filetypes = [("SNES ROM files", "*.sfc *.smc"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select SNES ROM", filetypes=filetypes)
        if filename and os.path.isfile(filename) and filename.lower().endswith(('.sfc', '.smc')):
            self.current_rom = filename
            rom_name = os.path.basename(filename)
            self.rom_label.config(text=f"ROM: {rom_name}")
            self.status_bar.config(text=f"Loaded: {rom_name}")
            self.core.load_game(filename)
            self.reset_emulation()
        else:
            messagebox.showerror("Invalid File", "Please select a valid .sfc or .smc file.")

    def start_emulation(self):
        """Start the emulation loop."""
        if not self.current_rom:
            messagebox.showinfo("No ROM", "Load a ROM first!")
            return
        self.is_running = True
        self.core.running = True
        self.status_bar.config(text=f"Running: {os.path.basename(self.current_rom)}")
        self.emulation_loop()

    def emulation_loop(self):
        """Main emulation loop targeting 60 FPS."""
        if not self.is_running:
            return
        current_time = time.time()
        if current_time - self.core.last_frame >= 0.016:  # 60 FPS
            self.core.last_frame = current_time
            self.core.run()
            self.core.render_frame()
            self.update_canvas()
        self.root.after(1, self.emulation_loop)  # Fine-grained scheduling

    def update_canvas(self):
        """Draw the frame buffer to the canvas."""
        self.canvas.delete("all")
        scale = 2  # 256x224 to 512x448
        for y in range(self.frame_height):
            for x in range(self.frame_width):
                color = self.core.frame_buffer[y * self.frame_width + x]
                if color:
                    hex_color = f"#{color:06x}"
                    self.canvas.create_rectangle(
                        x * scale, y * scale, (x + 1) * scale, (y + 1) * scale,
                        fill=hex_color, outline=hex_color
                    )

    def pause_emulation(self):
        """Pause the emulation."""
        if self.is_running:
            self.is_running = False
            self.core.running = False
            self.status_bar.config(text=f"Paused: {os.path.basename(self.current_rom)}")

    def reset_emulation(self, event=None):
        """Reset the emulator."""
        self.is_running = False
        self.core.running = False
        self.core.reset()
        self.draw_message(f"ROM loaded: {os.path.basename(self.current_rom) if self.current_rom else 'None'}\nPress Start")
        self.status_bar.config(text="Ready")

    def toggle_emulation(self, event):
        """Toggle between start and pause."""
        if self.is_running:
            self.pause_emulation()
        else:
            self.start_emulation()

    def save_state_func(self):
        """Save the current emulator state."""
        if self.current_rom and self.is_running:
            self.save_state = {
                'memory': self.core.memory[:],
                'pc': self.core.pc,
                'reg_a': self.core.reg_a,
                'x': self.core.memory[0x20],
                'y': self.core.memory[0x21]
            }
            self.status_bar.config(text="State saved")

    def load_state_func(self):
        """Load a previously saved state."""
        if self.save_state:
            self.core.memory = bytearray(self.save_state['memory'])
            self.core.pc = self.save_state['pc']
            self.core.reg_a = self.save_state['reg_a']
            self.core.memory[0x20] = self.save_state['x']
            self.core.memory[0x21] = self.save_state['y']
            self.status_bar.config(text="State loaded")

if __name__ == "__main__":
    root = tk.Tk()
    app = Snes9xEmulator(root)
    root.mainloop()
