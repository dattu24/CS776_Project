import os
import sys
import pickle
import json
import numpy as np
from tqdm import tqdm
from PIL import Image

import torch
# from ..models.load import load_model
# from ..data.datatypes import FashionItem
from full_outfit_generator.outfit_transformer.src.models.load import load_model
from full_outfit_generator.outfit_transformer.src.data.datatypes import FashionItem
from AttributePredictor.attribute_predictor import remove_background, save_prediction_one

import os
import shutil

import ConfigPath

def update_embedding_online(new_image_path):

    # Make sure the target folder exists
    os.makedirs(ConfigPath.USER_DIR, exist_ok=True)

    # Build the destination path
    destination = os.path.join(ConfigPath.USER_DIR, os.path.basename(new_image_path))

    # Move the image
    shutil.move(new_image_path, destination)

    print(f"Image moved to: {destination}")


    img_path = destination
    remove_background(img_path)
    save_prediction_one(img_path,json_path=ConfigPath.IMAGE_PREDICTIONS_JSON_PATH)
    



    # ======= Setup paths =======
    # script_dir = os.path.dirname(os.path.abspath(_file_))
    # description_file = os.path.join(script_dir, "/content/image_predictions (2).json")
    # ConfigPath.USER_DIR = os.path.join(script_dir, "/content/DATASET/DATASET/Men")
    # output_path = os.path.join(script_dir, "/content/my_clip_embeddings (3).pkl")


    # ConfigPath.IMAGE_PREDICTIONS_JSON_PATH = ConfigPath.IMAGE_PREDICTIONS_JSON_PATH
    # ======= Load descriptions from JSON =======
    with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH, "r") as f:
        item_descriptions = json.load(f)

    # ======= Load model =======
    model = load_model(model_type="clip")
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # ======= Load existing embeddings if present =======
    if os.path.exists(ConfigPath.CLIP_EMBEDDING_PKL_PATH):
        with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "rb") as f:
            data = pickle.load(f)
            existing_ids = set(data["ids"])
            all_ids = data["ids"]
            all_embeddings = list(data["embeddings"])
        print(f"Loaded {len(existing_ids)} existing embeddings.")
    else:
        existing_ids = set()
        all_ids = []
        all_embeddings = []
        print("No existing embeddings found. Starting fresh.")

    # ======= Encode missing items =======
    new_count = 0

    for item in tqdm(item_descriptions, desc="Encoding items"):
        item_id = item.get("id")
        if not item_id or item_id in existing_ids:
            continue

        description = item.get("articleType", "")
        image_path = os.path.join(ConfigPath.USER_DIR, f"{item_id}.jpg")
        print(image_path)
        if not os.path.exists(image_path):
            print(f"[Warning] Skipping {item_id}, image not found.")
            continue

        try:
            item_image = Image.open(image_path).convert("RGB")
            item_obj = FashionItem(item_id=item_id, image=item_image, description=description)

            with torch.no_grad():
                embedding = model.precompute_clip_embedding([item_obj])[0]
                all_ids.append(item_id)
                all_embeddings.append(embedding)
                new_count += 1

        except Exception as e:
            print(f"[Error] Failed to process {item_id}: {e}")

    # ======= Save updated embeddings =======
    if new_count > 0:
        all_embeddings = np.stack(all_embeddings)
        with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "wb") as f:
            pickle.dump({"ids": all_ids, "embeddings": all_embeddings}, f)
        print(f"\nUpdated embeddings saved to {ConfigPath.CLIP_EMBEDDING_PKL_PATH}")
    else:
        print("\nNo new embeddings were added.")
    al=set(all_ids)
    print(f"\nSummary:")
    print(f"Total items with 'id' in JSON: {sum(1 for item in item_descriptions if 'id' in item)}")
    print(f"Embeddings before update: {len(existing_ids)}")
    print(f"New embeddings added: {new_count}")
    print(f"Total embeddings after update: {len(al)}")

# new_image_path = "D:\\Yash\\MTech\\IITK\\SEM-2\\computer vision\\project\\interface\\DATASET_used\\Footwear\\Casual Shoes\\2540.jpg"
# update_embedding_online(new_image_path)