import os
import tkinter as tk
from tkinter import filedialog, StringVar
from PIL import Image, ImageTk
from full_outfit_generator.outfit_transformer.src.run.full_out import build_outfit
import ConfigPath


def full_outfit_predict(input_image_path, selected_categories=None):

    files = os.listdir(ConfigPath.USER_DIR)
    image_paths = [os.path.join(ConfigPath.USER_DIR, f) for f in files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return image_paths[:3] if len(image_paths) >= 3 else image_paths

class FullOutFitGenerator:
    def __init__(self, root):
        self.root = root
        self.outfit_images = []
        self.tk_images = []
        self.selected_image_path = None
        self.destination_folder = ConfigPath.USER_DIR
        
        # List of subcategories
        self.subcategories = [
            "Blazers", "Casualshoes", "Flipflops", "formalshoes", "heels", "jackets",
            "jeans", "Kurtas", "Kurtis", "NehruJackets", "nightsuits", "rainjackets",
            "sandals", "shirts", "shorts", "sportssandals", "sportsshoes", "sweaters",
            "sweatshirts", "trackpants", "tracksuits", "Trousers", "Tshirts", "WaaistCoat", "FlipFlops",
        ]
        
        self.dropdown_vars = [StringVar(root) for _ in range(4)]
        
        for var in self.dropdown_vars:
            var.set("")
        
        self.create_scrollable_container()
        
        self.create_widgets()

    def create_scrollable_container(self):

        self.scroll_container = tk.Frame(self.root)
        self.scroll_container.pack(fill=tk.BOTH, expand=True)
        
        self.main_canvas = tk.Canvas(self.scroll_container)
        
        self.v_scrollbar = tk.Scrollbar(self.scroll_container, orient=tk.VERTICAL, 
                                        command=self.main_canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = tk.Scrollbar(self.scroll_container, orient=tk.HORIZONTAL, 
                                        command=self.main_canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.main_canvas.configure(xscrollcommand=self.h_scrollbar.set,
                                   yscrollcommand=self.v_scrollbar.set)
        
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.main_frame = tk.Frame(self.main_canvas)
        
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.main_frame, 
                                                           anchor="nw")
        
        self.main_frame.bind("<Configure>", self.update_scroll_region)
        
        self.main_canvas.bind("<Configure>", self.resize_canvas_window)
        
        # Add mousewheel scrolling
        self.bind_mousewheel()

    def update_scroll_region(self, event=None):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def resize_canvas_window(self, event):
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mousewheel(self):
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.main_canvas.bind_all("<Button-4>", 
                                 lambda e: self.main_canvas.yview_scroll(-1, "units"))
        self.main_canvas.bind_all("<Button-5>", 
                                 lambda e: self.main_canvas.yview_scroll(1, "units"))

    def create_widgets(self):
        top_frame = tk.Frame(self.main_frame)
        top_frame.pack(pady=10)

        btn = tk.Button(top_frame, text="Select Base Image", command=self.select_image)
        btn.pack()

        self.preview_canvas = tk.Canvas(self.main_frame, width=300, height=300, bg="lightgray")
        self.preview_canvas.pack(pady=10)
        
        dropdown_frame = tk.LabelFrame(self.main_frame, padx=10, pady=10)
        dropdown_frame.pack(fill="x", padx=10, pady=10)
        

        categories_frame = tk.Frame(dropdown_frame)
        categories_frame.pack(fill="x")
        
        for i in range(4):
            categories_frame.columnconfigure(i, weight=1)
        
        for i in range(4):
            label = tk.Label(categories_frame, text=f"Category {i+1}")
            label.grid(row=0, column=i, padx=5, pady=2)
            
            options = [""] + self.subcategories
            dropdown = tk.OptionMenu(categories_frame, self.dropdown_vars[i], *options)
            dropdown.grid(row=1, column=i, padx=5, pady=2, sticky="ew")
        
        generate_btn = tk.Button(dropdown_frame, text="Generate Outfit", command=self.generate_outfit)
        generate_btn.pack(pady=10)

        self.generated_frame = tk.Frame(self.main_frame)
        self.generated_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def get_selected_categories(self):
        selected = []
        for var in self.dropdown_vars:
            value = var.get()
            if value:  
                selected.append(value)
        return selected if selected else None

    def select_image(self):
        filetypes = (("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),)
        image_path = filedialog.askopenfilename(initialdir=self.destination_folder, filetypes=filetypes)

        if image_path:
            self.selected_image_path = image_path
            self.display_input_image(image_path)
    
    def generate_outfit(self):
        if not self.selected_image_path:
            for widget in self.generated_frame.winfo_children():
                widget.destroy()
            error_label = tk.Label(self.generated_frame, text="Please select an image first", fg="red")
            error_label.pack(pady=10)
            return
            
        categories = self.get_selected_categories()
        file_name = os.path.basename(self.selected_image_path)
        file_id = os.path.splitext(file_name)[0] 
        print(categories, file_id)

        final_outfit = build_outfit(file_id, categories)
        return_imgs=[]
        for i, item in enumerate(final_outfit):
            img_path = os.path.join(self.destination_folder, f"{item.item_id}.jpg")
            return_imgs.append(img_path)
        
        self.display_generated_outfit(return_imgs[1:])
        
        self.update_scroll_region()

    def display_input_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((280, 280))
        self.input_img = ImageTk.PhotoImage(img)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(150, 150, image=self.input_img)
        
    def display_generated_outfit(self, image_paths):
        for widget in self.generated_frame.winfo_children():
            widget.destroy()
        self.tk_images.clear()

        selected_cats = self.get_selected_categories()
        if selected_cats:
            cat_text = f"Using categories: {', '.join(selected_cats)}"
        else:
            cat_text = "No categories selected - showing all recommendations"
            
        cat_label = tk.Label(self.generated_frame)
        cat_label.grid(row=0, column=0, columnspan=len(image_paths), pady=0)

        total_images = len(image_paths)
        for col in range(total_images):
            self.generated_frame.grid_columnconfigure(col, weight=1)

        for idx, path in enumerate(image_paths):
            try:
                img = Image.open(path)
                img.thumbnail((300, 300))
                tk_img = ImageTk.PhotoImage(img)
                self.tk_images.append(tk_img)

                outer_frame = tk.Frame(self.generated_frame)
                outer_frame.grid(row=1, column=idx, sticky="n", padx=10, pady=10)

                frame = tk.Frame(outer_frame, padx=5, pady=5)
                frame.pack(anchor="center")

                label = tk.Label(frame, image=tk_img)
                label.pack()

                caption = tk.Label(frame, text=os.path.basename(path), wraplength=180)
                caption.pack()

            except Exception as e:
                print(f"Error loading generated outfit image: {e}")
                error_frame = tk.Frame(self.generated_frame)
                error_frame.grid(row=1, column=idx, padx=10, pady=10)
                error_label = tk.Label(error_frame, text=f"Error loading image: {e}", fg="red", wraplength=200)
                error_label.pack(pady=50)
        
        self.update_scroll_region()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fashion Outfit Generator")
    root.geometry("1000x800")
    app = FullOutFitGenerator(root)
    root.mainloop()
