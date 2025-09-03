import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from full_outfit_generator.m import suggest_flat_outfit
from full_outfit_generator.generate_base.m import find_top_k_images_in_subcat
from full_outfit_generator.outfit_transformer.src.run.full_out import build_outfit
from ConfigPath import USER_MEN
import ConfigPath

subcategories = [
    "Blazers", "Casualshoes", "Flipflops", "formalshoes", "heels", "jackets",
    "jeans", "Kurtas", "Kurtis", "NehruJackets", "nightsuits", "rainjackets",
    "sandals", "shirts", "shorts", "sportssandals", "sportsshoes", "sweaters",
    "sweatshirts", "trackpants", "tracksuits", "Trousers", "Tshirts", "WaaistCoat","FlipFlops",
]


def predict_occassion_outfit(description):
    if ConfigPath.USER==USER_MEN:
        occasion_to_outfit = {
            "wedding": ["shirts", "Blazers", "Trousers", "formalshoes"],
            "office": ["shirts", "Blazers", "Trousers", "formalshoes"],
            "interview": ["shirts", "Blazers", "Trousers", "formalshoes"],
            "gym": ["Tshirts", "trackpants", "sportsshoes"],
            "party": ["shirts", "jeans", "Casualshoes"],
            "casual": ["Tshirts", "shorts", "FlipFlops"],
            "beach": ["Tshirts", "shorts", "FlipFlops"],
            "rain": ["rainjackets", "jeans", "sportssandals"],
            "festival": ["Kurtas",  "Trousers", "formalshoes"],
            "temple": ["Kurtas", "Trousers", "formalshoes"],
            "sport": ["Tshirts", "trackpants", "sportsshoes"],
            "presentation": ["shirts", "Trousers", "Casualshoes"],
            "shopping": ["Tshirts", "Trousers", "sandals"],
        }
    else:
        # Occasion to women's outfit subcategories
        occasion_to_outfit = {
            "party": ["Dresses", "Heels"],
            "wedding": ["LehengaCholi", "Dupatta", "Heels"],
            "office": ["Shirts", "Trousers", "Casualshoes"],
            "interview": ["Trousers", "Blazers", "formalshoes"],
            "gym": ["Tshirts", "trackPants", "sportsshoes"],
            "casual": ["Tops", "Jeans", "FlipFlops"],
            "beach": ["Tops", "Shorts", "FlipFlops"],
            "shopping": ["Tops", "Trousers", "Flats"],
            "rain": ["Jackets", "trackpants", "Sandals"],
            "temple": ["Kurtis", "Leggings", "Flats"],
            "festival": ["Sarees", "Heels"],
            "sport": ["Tshirts", "trackpants", "sportsshoes"],
            "presentation": ["Shirts", "Blazers","Trousers" "formalshoes"]
        }

    desc_s = description
    occasion_s, outfit_s = suggest_flat_outfit(desc_s, subcategories, occasion_to_outfit)

    print(f"Occasion: {occasion_s}")
    desc_s = occasion_s
    if("pant" in description):
        semantic_query_s = "Bottomwear"
        fine_grained_query_s = outfit_s[0]
        query_text_s = f"{fine_grained_query_s}: {desc_s}"

        top_k_results_s = find_top_k_images_in_subcat(query_text_s, semantic_query_s, fine_grained_query_s, k=1)
        target_descriptions = ["shirts","CasualShoes"]
    else:
        semantic_query_s = "topwear"
        fine_grained_query_s = outfit_s[0]
        query_text_s = f"{fine_grained_query_s}: {desc_s}"
        target_descriptions = outfit_s[1:]
        print("query_text_s, semantic_query, fine_grained_query_s:", query_text_s, semantic_query_s, fine_grained_query_s)
        top_k_results_s = find_top_k_images_in_subcat(query_text_s, semantic_query_s, fine_grained_query_s, k=1)

    return_imgs = []
    
    print("top_k_results_s:",top_k_results_s)
    
    start_id =int(top_k_results_s[0][0])

    desc_str = " ".join(target_descriptions)
    
    
    final_outfit = build_outfit(start_id, target_descriptions)
    
    for i, item in enumerate(final_outfit):
        img_path = os.path.join(ConfigPath.USER_DIR, f"{item.item_id}.jpg")
        return_imgs.append(img_path)
    return return_imgs

class OccasionOutfitPage:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        # frame to take text input
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(input_frame, text="Enter Description:").grid(row=0, column=0, sticky="w")
        self.description_entry = tk.Text(input_frame, height=4, wrap="word")
        self.description_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        submit_button = ttk.Button(input_frame, text="Generate Outfit", command=self.generate_outfit)
        submit_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Layout behavior
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=0)

        # to scroll horizontal
        self.canvas = tk.Canvas(self.frame, height=250)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.scroll_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.image_labels = []

    def generate_outfit(self):
        # clear previous images
        for label in self.image_labels:
            label.destroy()
        self.image_labels.clear()

        # Get user inputs
        description = self.description_entry.get("1.0", "end").strip()

        image_paths = predict_occassion_outfit(description)

        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                img.thumbnail((200, 200))
                img_tk = ImageTk.PhotoImage(img)

                lbl = ttk.Label(self.scroll_frame, image=img_tk)
                lbl.image = img_tk
                lbl.pack(side="left", padx=5, pady=10)
                self.image_labels.append(lbl)
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
