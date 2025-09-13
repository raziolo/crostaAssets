import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

# --- CONFIGURATION ---
# IMPORTANT: Set these paths before running the script.

# 1. The folder of CLEAN images to be labeled (the OUTPUT from the previous script).
IMAGE_DIRECTORY = r"C:\Users\Brumotti\Desktop\DESKTOP\NewDjangoProjects\scratches\OK"

# 2. The JSON file where your labels will be saved.
#    This file will be created automatically.
LABEL_FILE = r"C:\Users\Brumotti\Desktop\DESKTOP\NewDjangoProjects\scratches\labels.json"

# 3. Maximum display size for the images in the GUI.
MAX_IMAGE_WIDTH = 800
MAX_IMAGE_HEIGHT = 600


# ---------------------


class ImageLabelerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeler")

        # --- Data Handling ---
        self.image_dir = IMAGE_DIRECTORY
        self.label_file = LABEL_FILE
        self.labels = self.load_labels()
        self.image_files = self.load_image_files()

        # Filter out already labeled images
        self.files_to_label = [f for f in self.image_files if f not in self.labels]
        self.current_index = 0

        # --- GUI Setup ---
        self.setup_gui()

        # --- Start the process ---
        if not self.files_to_label:
            self.show_completion_message()
        else:
            self.display_image()

    def setup_gui(self):
        """Creates and arranges all the GUI widgets."""
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Image display label
        self.image_label = tk.Label(main_frame)
        self.image_label.pack(pady=10)

        # Info/Status label
        self.status_label = tk.Label(main_frame, text="", font=("Helvetica", 10))
        self.status_label.pack(pady=(0, 10))

        # Entry widget frame
        entry_frame = tk.Frame(main_frame)
        entry_frame.pack(pady=5, fill=tk.X, expand=True)

        tk.Label(entry_frame, text="Label:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=(0, 10))
        self.entry = tk.Entry(entry_frame, font=("Helvetica", 12), width=50)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Bind the Enter key to the next_image function for speed
        self.entry.bind("<Return>", self.next_image)

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.prev_button = tk.Button(button_frame, text="<< Previous", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(button_frame, text="Save & Next >>", command=self.next_image,
                                     font=("Helvetica", 10, "bold"))
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_image_files(self):
        """Scans the directory for supported image files."""
        if not os.path.isdir(self.image_dir):
            messagebox.showerror("Error", f"Image directory not found:\n{self.image_dir}")
            self.root.destroy()
            return []

        supported = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.gif')
        return sorted([f for f in os.listdir(self.image_dir) if f.lower().endswith(supported)])

    def load_labels(self):
        """Loads existing labels from the JSON file."""
        try:
            if os.path.exists(self.label_file):
                with open(self.label_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showwarning("Warning", f"Could not read label file: {e}\nStarting with a new label set.")
        return {}

    def save_labels(self):
        """Saves the current labels dictionary to the JSON file."""
        try:
            with open(self.label_file, 'w') as f:
                json.dump(self.labels, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Could not save labels to file: {e}")

    def display_image(self):
        """Opens, resizes, and displays the current image."""
        if not 0 <= self.current_index < len(self.files_to_label):
            return

        filename = self.files_to_label[self.current_index]
        filepath = os.path.join(self.image_dir, filename)

        try:
            # Open and resize the image
            with Image.open(filepath) as img:
                img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)

                # Convert for tkinter
                self.photo_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.photo_image)
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image: {filename}\n{e}")
            self.image_label.config(image=None, text=f"Error loading {filename}")

        # Update status and clear entry
        total_to_label = len(self.files_to_label)
        status_text = f"Image {self.current_index + 1} of {total_to_label}  |  File: {filename}"
        self.status_label.config(text=status_text)
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

        # Disable/enable buttons
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)

    def next_image(self, event=None):
        """Saves the current label and moves to the next image."""
        if not 0 <= self.current_index < len(self.files_to_label):
            return

        label = self.entry.get().strip()
        if not label:
            messagebox.showwarning("Input Required", "Please enter a label before proceeding.")
            return

        filename = self.files_to_label[self.current_index]
        self.labels[filename] = label
        self.save_labels()  # Progressive save - CRITICAL for safety

        self.current_index += 1
        if self.current_index >= len(self.files_to_label):
            self.show_completion_message()
        else:
            self.display_image()

    def prev_image(self):
        """Moves to the previous image without saving."""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()

    def show_completion_message(self):
        """Displays a message when all images are labeled."""
        self.image_label.config(image=None, text="🎉 All Done! 🎉", font=("Helvetica", 24))
        self.status_label.config(text=f"All {len(self.image_files)} images have been labeled.")
        self.entry.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.prev_button.config(state=tk.DISABLED)
        messagebox.showinfo("Complete", "You have successfully labeled all images!")

    def on_closing(self):
        """Handles the window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit? Your progress is saved."):
            self.root.destroy()


if __name__ == "__main__":
    # Check if paths are default, and warn user if so.
    if "YourUser" in IMAGE_DIRECTORY or "path\\to" in IMAGE_DIRECTORY:
        print("🚨  WARNING: Please update the IMAGE_DIRECTORY and LABEL_FILE paths in the script before running.")
        # We can also show a GUI popup for this
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Configuration Error",
                             "Please update the IMAGE_DIRECTORY and LABEL_FILE paths in the script before running.")
    else:
        root = tk.Tk()
        app = ImageLabelerApp(root)
        root.mainloop()