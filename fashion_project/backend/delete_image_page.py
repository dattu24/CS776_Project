import os
import tkinter as tk
import json
import pickle
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from math import floor
import ConfigPath


class DeleteImagePage:
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

        # Select Images Button
        self.select_images_btn = tk.Button(
            control_frame, text="Select Images", command=self.select_images, width=15
        )
        self.select_images_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete images Button
        self.save_images_btn = tk.Button(
            control_frame,
            text="Delete Images",
            command=self.delete_images,
            width=15,
            state=tk.DISABLED,
        )
        self.save_images_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Columns:").pack(side=tk.LEFT)
        self.columns_spin = tk.Spinbox(
            control_frame,
            from_=1,
            to=10,
            width=3,
            command=self.update_columns,
            state="readonly",
        )
        self.columns_spin.pack(side=tk.LEFT, padx=5)
        self.columns_spin.delete(0, tk.END)
        self.columns_spin.insert(0, self.current_columns)

        tk.Label(control_frame, text="Thumb Size:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar()
        self.size_var.set("150x150")
        size_options = ["100x100", "150x150", "200x200", "250x250"]
        self.size_menu = ttk.Combobox(
            control_frame,
            textvariable=self.size_var,
            values=size_options,
            width=7,
            state="readonly",
        )
        self.size_menu.pack(side=tk.LEFT, padx=5)
        self.size_menu.bind("<<ComboboxSelected>>", self.change_thumbnail_size)

        self.canvas_frame = tk.Frame(main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = tk.Scrollbar(
            self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Image_container to hold image thumbnails
        self.image_container = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_container, anchor=tk.NW)

        self.image_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        # Scroll vertically using mouse wheel
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_window_resize(self, event=None):
        # Auto adjust column when window is resized
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
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*"),
        )
        paths = filedialog.askopenfilenames(
            title="Select images",
            initialdir=self.destination_folder,
            filetypes=filetypes,
        )
        if paths:
            self.image_paths = list(paths)
            self.calculate_auto_columns()
            self.update_image_preview()
            self.save_images_btn.config(state=tk.NORMAL)

    def change_thumbnail_size(self, event=None):
        size_str = self.size_var.get()
        width, height = map(int, size_str.split("x"))
        self.thumbnail_size = (width, height)
        self.update_image_preview()

    def update_image_preview(self):
        # clearing all current image previews
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
                
                # frame to hold image and label
                row, col = divmod(i, self.current_columns)
                frame = tk.Frame(
                    self.image_container,
                    bd=2,
                    relief=tk.RAISED,
                    width=self.thumbnail_size[0] + 2 * self.padding,
                    height=self.thumbnail_size[1] + 40,
                )
                frame.grid(
                    row=row,
                    column=col,
                    padx=self.padding,
                    pady=self.padding,
                    sticky="nsew",
                )
                frame.grid_propagate(False)

                # showing image and filename
                label = tk.Label(frame, image=photo)
                label.pack(padx=2, pady=2)
                filename = os.path.basename(img_path)
                tk.Label(
                    frame, text=filename, wraplength=self.thumbnail_size[0] - 10
                ).pack(padx=2, pady=2)

            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                row, col = divmod(i, self.current_columns)
                frame = tk.Frame(
                    self.image_container,
                    bd=2,
                    relief=tk.RAISED,
                    width=self.thumbnail_size[0] + 2 * self.padding,
                    height=self.thumbnail_size[1] + 40,
                )
                frame.grid(row=row, column=col, padx=self.padding, pady=self.padding)
                frame.grid_propagate(False)
                tk.Label(
                    frame, text=f"Error loading\n{os.path.basename(img_path)}"
                ).pack()

        for i in range(self.current_columns):
            self.image_container.grid_columnconfigure(i, weight=1)

    def delete_images(self):
        try:

            if os.path.exists(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH):
                with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH, "r") as f:
                    data = json.load(f)
            else:
                data = []

            item_ids = []
            for src_path in self.image_paths:
                item_id, ext = os.path.splitext(os.path.basename(src_path))
                item_ids.append(item_id)
            updated_data = [item for item in data if item["id"] not in item_ids]

            with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH, "w") as file:
                json.dump(updated_data, file, indent=4)

            if os.path.exists(ConfigPath.CLIP_EMBEDDING_PKL_PATH):
                with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "rb") as f:
                    data = pickle.load(f)
                    existing_ids = set(data["ids"])
                    all_ids = data["ids"]
                    all_embeddings = list(data["embeddings"])
                print(f"Loaded {len(all_embeddings)} existing embeddings.")
                for item_id in item_ids:
                    idx = all_ids.index(item_id)
                    all_ids.pop(idx)
                    all_embeddings.pop(idx)
            else:
                existing_ids = set()
                all_ids = []
                all_embeddings = []
                print("No existing embeddings found. Starting fresh.")
            with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "wb") as f:
                pickle.dump({"ids": all_ids, "embeddings": all_embeddings}, f)
            print(f"\nUpdated embeddings saved to {ConfigPath.CLIP_EMBEDDING_PKL_PATH}")

            print(f"Total embeddings after update: {len(all_embeddings)}")
            for src_path in self.image_paths:
                os.remove(src_path)
            print(f"deleted {len(self.image_paths)} images...")
            messagebox.showinfo(
                "Delete Complete", f"Successfully deleted {len(self.image_paths)}"
            )
        except Exception as e:
            print(f"Error while deleting {src_path}: {e}")
            messagebox.showinfo(
                "Delete Failed", f"Error while deleting {src_path} : {str(e)}"
            )
