import tkinter as tk
from tkinter import ttk
import image_selector_page
import attribute_predictor_page
import outfit_generator_page
import occasion_outfit_page
import delete_image_page 
import ConfigPath
from ConfigPath import USER_MEN, USER_WOMEN, USER_MEN_DIR, USER_WOMEN_DIR, IMAGE_PREDICTIONS_MEN_JSON_PATH, IMAGE_PREDICTIONS_WOMEN_JSON_PATH, CLIP_EMBEDDING_MEN_PKL_PATH, CLIP_EMBEDDING_WOMEN_PKL_PATH
class MultiTabApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fashion Transformer")
        self.geometry("1000x700")
        
        # Frame for user selection dropdown
        top_frame = tk.Frame(self)
        top_frame.pack(fill='x', pady=5)
        
        # push the dropdown to the right
        spacer = tk.Label(top_frame, text="")
        spacer.pack(side='left', expand=True, fill='x')
        
        # User selection dropdown
        self.user_var = tk.StringVar()
        self.user_var.set("MEN") 
        self.prev_value = "MEN"
        
        # label for the dropdown
        user_label = tk.Label(top_frame, text="User Mode:")
        user_label.pack(side='left', padx=5)
        
        # User dropdown
        user_dropdown = tk.OptionMenu(top_frame, self.user_var, "MEN", "WOMEN", command=self.on_user_change)
        user_dropdown.pack(side='left', padx=10)

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        page1_frame = ttk.Frame(notebook)
        page2_frame = ttk.Frame(notebook)
        page3_frame = ttk.Frame(notebook)
        page4_frame = ttk.Frame(notebook)
        page5_frame = ttk.Frame(notebook)

        notebook.add(page1_frame, text="Image Selector")
        notebook.add(page2_frame, text="Predict Attributes")
        notebook.add(page3_frame, text="Full Outfit Generator")
        notebook.add(page4_frame, text="Occasion Outfit")
        notebook.add(page5_frame, text="Delete Images")

        self.page1 = image_selector_page.ResponsiveGridLayoutWithSave(page1_frame)
        self.page2 = attribute_predictor_page.AttributePredictorPage(page2_frame)
        self.page3 = outfit_generator_page.FullOutFitGenerator(page3_frame)
        self.page4 = occasion_outfit_page.OccasionOutfitPage(page4_frame)
        self.page5 = delete_image_page.DeleteImagePage(page5_frame)
    
    def on_user_change(self, selected_value):
        if self.prev_value == "MEN" and selected_value == "WOMEN":
            self.update_for_women()

        elif self.prev_value == "WOMEN" and selected_value == "MEN":
            self.update_for_men()
            
        self.prev_value = selected_value
    
    def update_for_women(self):
        ConfigPath.USER = USER_WOMEN
        ConfigPath.USER_DIR = USER_WOMEN_DIR
        ConfigPath.IMAGE_PREDICTIONS_JSON_PATH=IMAGE_PREDICTIONS_WOMEN_JSON_PATH
        ConfigPath.CLIP_EMBEDDING_PKL_PATH = CLIP_EMBEDDING_WOMEN_PKL_PATH
        self.page1.destination_folder=USER_WOMEN_DIR
        self.page2.destination_folder=USER_WOMEN_DIR
        self.page3.destination_folder=USER_WOMEN_DIR
        self.page5.destination_folder=USER_WOMEN_DIR
    
    def update_for_men(self):
        ConfigPath.USER = USER_MEN
        ConfigPath.USER_DIR = USER_MEN_DIR
        ConfigPath.IMAGE_PREDICTIONS_JSON_PATH=IMAGE_PREDICTIONS_MEN_JSON_PATH
        ConfigPath.CLIP_EMBEDDING_PKL_PATH=CLIP_EMBEDDING_MEN_PKL_PATH
        self.page1.destination_folder=USER_MEN_DIR
        self.page2.destination_folder=USER_MEN_DIR
        self.page3.destination_folder=USER_MEN_DIR
        self.page5.destination_folder=USER_MEN_DIR

if __name__ == "__main__":
    app = MultiTabApp()
    app.mainloop()
