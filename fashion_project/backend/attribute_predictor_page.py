import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from AttributePredictor.attribute_predictor import predict_labels 
import ConfigPath

def predict_attributes(image_path):
    articleType, category, event =predict_labels(image_path)
    return {
        "articleType": articleType,
        "category": category
    }

class AttributePredictorPage:
    def __init__(self, root):
        self.root = root
        self.image_label = None
        self.attribute_labels = []
        self.destination_folder = ConfigPath.USER_DIR

        self.create_widgets()

    def create_widgets(self):

        # Frame for "Select Image" button
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        select_btn = tk.Button(top_frame, text="Select Image", command=self.select_image)
        select_btn.pack()

        self.preview_canvas = tk.Canvas(self.root, width=300, height=300, bg="lightgray")
        self.preview_canvas.pack(pady=10)

        # Frame to show predicted attributes
        self.attr_frame = tk.Frame(self.root)
        self.attr_frame.pack(pady=10)

    def select_image(self):
        filetypes = (("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),)
        image_path = filedialog.askopenfilename(initialdir=self.destination_folder, filetypes=filetypes)

        if image_path:
            self.display_image(image_path)
            self.display_attributes(image_path)

    def display_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        self.tk_image = ImageTk.PhotoImage(img)
        self.preview_canvas.create_image(150, 150, image=self.tk_image)

    def display_attributes(self, image_path):
        for label in self.attribute_labels:
            label.destroy()

        attributes = predict_attributes(image_path)

        self.attribute_labels = []
        for key, value in attributes.items():
            lbl = tk.Label(self.attr_frame, text=f"{key}: {value}", font=("Arial", 12))
            lbl.pack(anchor="w")
            self.attribute_labels.append(lbl)
