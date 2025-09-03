import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from math import floor
import ConfigPath
from ConfigPath import OUR_IMAGE_DIR, TEMP_DIR
from update_embedding import update_embedding_online
class ResponsiveGridLayoutWithSave:
    def __init__(self, root):
        self.root = root

        self.image_paths = []
        self.image_previews = []
        self.current_columns = 4
        self.thumbnail_size = (150, 150)
        self.padding = 5
        self.destination_folder = ConfigPath.USER_DIR
        self.create_widgets()
        self.root.bind("<Configure>", self.on_window_resize)

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.select_images_btn = tk.Button(
            control_frame, text="Select Images", command=self.select_images, width=15
        )
        self.select_images_btn.pack(side=tk.LEFT, padx=5)

        self.save_images_btn = tk.Button(
            control_frame, text="Save Images", command=self.save_images, width=15, state=tk.DISABLED
        )
        self.save_images_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Columns:").pack(side=tk.LEFT)
        self.columns_spin = tk.Spinbox(
            control_frame, from_=1, to=10, width=3, command=self.update_columns, state="readonly"
        )
        self.columns_spin.pack(side=tk.LEFT, padx=5)
        self.columns_spin.delete(0, tk.END)
        self.columns_spin.insert(0, self.current_columns)

        tk.Label(control_frame, text="Thumb Size:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar()
        self.size_var.set("150x150")
        size_options = ["100x100", "150x150", "200x200", "250x250"]
        self.size_menu = ttk.Combobox(
            control_frame, textvariable=self.size_var, values=size_options, width=7, state="readonly"
        )
        self.size_menu.pack(side=tk.LEFT, padx=5)
        self.size_menu.bind("<<ComboboxSelected>>", self.change_thumbnail_size)

        self.canvas_frame = tk.Frame(main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.image_container = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_container, anchor=tk.NW)

        self.image_container.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_window_resize(self, event=None):
        if self.image_paths:
            self.calculate_auto_columns()

    def calculate_auto_columns(self):
        canvas_width = self.canvas.winfo_width() - 20
        min_column_width = self.thumbnail_size[0] + 2 * self.padding
        max_columns = max(1, floor(canvas_width / min_column_width))

        if max_columns != self.current_columns:
            self.current_columns = max_columns
            self.columns_spin.delete(0, tk.END)
            self.columns_spin.insert(0, self.current_columns)
            self.update_image_preview()

    def update_columns(self):
        try:
            new_columns = int(self.columns_spin.get())
            if 1 <= new_columns <= 10 and new_columns != self.current_columns:
                self.current_columns = new_columns
                self.update_image_preview()
        except ValueError:
            pass

    def select_images(self):
        filetypes = (
            ('Image files', '*.jpg *.jpeg *.png *.gif *.bmp'),
            ('All files', '*.*')
        )
        paths = filedialog.askopenfilenames(
            title="Select images", initialdir=OUR_IMAGE_DIR, filetypes=filetypes
        )
        if paths:
            self.image_paths = list(paths)
            self.calculate_auto_columns()
            self.update_image_preview()
            self.save_images_btn.config(state=tk.NORMAL)

    def change_thumbnail_size(self, event=None):
        size_str = self.size_var.get()
        width, height = map(int, size_str.split('x'))
        self.thumbnail_size = (width, height)
        self.update_image_preview()

    def update_image_preview(self):
        for widget in self.image_container.winfo_children():
            widget.destroy()
        self.image_previews = []

        if not self.image_paths:
            return

        for i, img_path in enumerate(self.image_paths):
            try:
                img = Image.open(img_path)
                img.thumbnail(self.thumbnail_size)
                photo = ImageTk.PhotoImage(img)
                self.image_previews.append(photo)

                row, col = divmod(i, self.current_columns)
                frame = tk.Frame(
                    self.image_container,
                    bd=2,
                    relief=tk.RAISED,
                    width=self.thumbnail_size[0] + 2 * self.padding,
                    height=self.thumbnail_size[1] + 40
                )
                frame.grid(row=row, column=col, padx=self.padding, pady=self.padding, sticky="nsew")
                frame.grid_propagate(False)

                label = tk.Label(frame, image=photo)
                label.pack(padx=2, pady=2)
                filename = os.path.basename(img_path)
                tk.Label(frame, text=filename, wraplength=self.thumbnail_size[0] - 10).pack(padx=2, pady=2)

            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                row, col = divmod(i, self.current_columns)
                frame = tk.Frame(
                    self.image_container,
                    bd=2,
                    relief=tk.RAISED,
                    width=self.thumbnail_size[0] + 2 * self.padding,
                    height=self.thumbnail_size[1] + 40
                )
                frame.grid(row=row, column=col, padx=self.padding, pady=self.padding)
                frame.grid_propagate(False)
                tk.Label(frame, text=f"Error loading\n{os.path.basename(img_path)}").pack()

        for i in range(self.current_columns):
            self.image_container.grid_columnconfigure(i, weight=1)
    def get_id(self):
        for i in range(1, 101):
            file_path = os.path.join(self.destination_folder, f"{i}.jpg")
            if not os.path.exists(file_path):
                # print(f"Missing file: {i}.jpg")
                return i
    def save_images(self):
        # Check if the destination folder exists
        # if os.path.exists(USER_DIR):
        #     # Delete all files in the destination folder
        #     for filename in os.listdir(USER_DIR):
        #         file_path = os.path.join(USER_DIR, filename)
        #         try:
        #             if os.path.isfile(file_path):
        #                 os.remove(file_path)  # Remove the file
        #         except Exception as e:
        #             print(f"Error deleting file {file_path}: {e}")
        USER_DIR_temp=TEMP_DIR
        if not os.path.exists(USER_DIR_temp):
            os.makedirs(USER_DIR_temp)  # Create the folder if it doesn't exist

        # Proceed with saving the images
        for src_path in self.image_paths:
            try:
                file_id = self.get_id()
                filename_file_id = str(file_id)+".jpg"
                dest_path = os.path.join(USER_DIR_temp, filename_file_id)

                # counter = 1
                # while os.path.exists(dest_path):
                #     name, ext = os.path.splitext(filename_file_id)
                #     dest_path = os.path.join(USER_DIR_temp, f"{name}{ext}")
                #     counter += 1
                # print("src_path:",src_path)
                # print("dest_path:",dest_path)
                shutil.copy2(src_path, dest_path)
                update_embedding_online(dest_path)
            except Exception as e:
                print(f"Error copying {src_path}: {e}")

        messagebox.showinfo(
            "Save Complete",
            f"Successfully saved {len(self.image_paths)} images to:\n{self.destination_folder}"
        )
