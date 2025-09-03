import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import pickle
import json
import os
from rembg import remove
from PIL import Image
import io
from rembg import remove
from PIL import Image
import io
from ConfigPath import ATTRIBUTE_PRED_PKL_DIR

PKL_DIR = ATTRIBUTE_PRED_PKL_DIR



def remove_background(input_image_path):
    if not os.path.exists(input_image_path):
        print(f"[Error] File not found: {input_image_path}")
        return

    try:
        with open(input_image_path, 'rb') as f:
            input_data = f.read()

        output_data = remove(input_data)
        result_image = Image.open(io.BytesIO(output_data)).convert("RGBA")

        ext = os.path.splitext(input_image_path)[1].lower()

        if ext in [".jpg", ".jpeg"]:
            white_bg = Image.new("RGB", result_image.size, (255, 255, 255))
            white_bg.paste(result_image, mask=result_image.split()[3])
            white_bg.save(input_image_path, "JPEG")
        elif ext == ".png":
            result_image.save(input_image_path, "PNG")
        else:
            print(f"[Error] Unsupported file format: {ext}")
            return

        print(f"[Success] Processed: {input_image_path}")

    except UnidentifiedImageError:
        print(f"[Error] Cannot identify image: {input_image_path}")
    except Exception as e:
        print(f"[Error] Failed to process {input_image_path}: {e}")

def extract_clip_features(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
    return features.cpu().numpy().squeeze()


def predict_image_articleType(clip_features):
    global  articleType_scaler,articleType_model,articleType_label_encoder
    clip_features_scaled = articleType_scaler.transform([clip_features])
    input_tensor = torch.tensor(clip_features_scaled, dtype=torch.float32).to(device)

    with torch.no_grad():
        output = articleType_model(input_tensor)
        _, predicted_class = torch.max(output, 1)
        predicted_label = articleType_label_encoder.inverse_transform(predicted_class.cpu().numpy())[0]

    return predicted_label

def predict_image_Category(clip_features):
    global  Category_scaler,Category_model,Category_label_encoder
    clip_features_scaled = Category_scaler.transform([clip_features])
    input_tensor = torch.tensor(clip_features_scaled, dtype=torch.float32).to(device)

    with torch.no_grad():
        output = Category_model(input_tensor)
        _, predicted_class = torch.max(output, 1)
        predicted_label = Category_label_encoder.inverse_transform(predicted_class.cpu().numpy())[0]

    return predicted_label

def predict_image_Event(clip_features):
    global  Event_scaler,Event_model,Event_label_encoder
    clip_features_scaled = Event_scaler.transform([clip_features])
    input_tensor = torch.tensor(clip_features_scaled, dtype=torch.float32).to(device)

    with torch.no_grad():
        output = Event_model(input_tensor)
        _, predicted_class = torch.max(output, 1)
        predicted_label = Event_label_encoder.inverse_transform(predicted_class.cpu().numpy())[0]

    return predicted_label

def predict_labels(image_path):
    clip_features = extract_clip_features(image_path)
    articleType =predict_image_articleType(clip_features)
    category = predict_image_Category(clip_features)
    event = predict_image_Event(clip_features)
    return articleType, category, event



def save_prediction(image_path, json_path="image_predictions.json"):
    image_name = os.path.basename(image_path)

    articleType, category, event = predict_labels(image_path)

    prediction = {
        "id": image_name,
        "articleType": articleType,
        "Category": category,
        "Event": event
    }

    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(prediction)

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Details of {image_name} is updated in the files")

def save_prediction_one(image_path, json_path="image_predictions.json"):
    image_name = os.path.basename(image_path)

    articleType, category, event = predict_labels(image_path)

    prediction = {
        "id": image_name.replace(".jpg",""),
        "articleType": articleType,
        "Category": category,
        "Event": event
    }

    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(prediction)

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Details of {image_name} is updated in the files")


class MLP(torch.nn.Module):
    def __init__(self, input_size, num_classes):
        super(MLP, self).__init__()
        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_size, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(512, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.model(x)




device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


articleType_model_path = PKL_DIR/'16_clip_mlp_model.pth'
articleType_scaler_path = PKL_DIR/'16_clip_scaler.pkl'
articleType_label_encoder_path = PKL_DIR/'16_clip_label_encoder.pkl'



Category_model_path = PKL_DIR/'18_clip_mlp_model.pth'
Category_scaler_path = PKL_DIR/'18_clip_scaler.pkl'
Category_label_encoder_path = PKL_DIR/'18_clip_label_encoder.pkl'



Event_model_path = PKL_DIR/'19_clip_mlp_model.pth'
Event_scaler_path = PKL_DIR/'19_clip_scaler.pkl'
Event_label_encoder_path = PKL_DIR/'19_clip_label_encoder.pkl'

input_size = 512



with open(articleType_scaler_path, 'rb') as f:
    articleType_scaler = pickle.load(f)

with open(articleType_label_encoder_path, 'rb') as f:
    articleType_label_encoder = pickle.load(f)

articleType_num_classes = len(articleType_label_encoder.classes_)
articleType_model = MLP(input_size, articleType_num_classes).to(device)
articleType_model.load_state_dict(torch.load(articleType_model_path, map_location=torch.device('cpu')))
articleType_model.eval()

with open(Category_scaler_path, 'rb') as f:
    Category_scaler = pickle.load(f)

with open(Category_label_encoder_path, 'rb') as f:
    Category_label_encoder = pickle.load(f)

Category_num_classes = len(Category_label_encoder.classes_)
Category_model = MLP(input_size, Category_num_classes).to(device)
Category_model.load_state_dict(torch.load(Category_model_path, map_location=torch.device('cpu')))
Category_model.eval()

with open(Event_scaler_path, 'rb') as f:
    Event_scaler = pickle.load(f)

with open(Event_label_encoder_path, 'rb') as f:
    Event_label_encoder = pickle.load(f)

Event_num_classes = len(Event_label_encoder.classes_)
Event_model = MLP(input_size, Event_num_classes).to(device)
Event_model.load_state_dict(torch.load(Event_model_path, map_location=torch.device('cpu')))
Event_model.eval()


# while True:
#     img_path=input()
#     if img_path=="exit":
#         break
#     remove_background(img_path)
#     save_prediction(img_path)