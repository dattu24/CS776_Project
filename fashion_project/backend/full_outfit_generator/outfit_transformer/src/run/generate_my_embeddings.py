import os
import sys
import pickle
import json
import numpy as np
from tqdm import tqdm
from PIL import Image

import torch
from ..models.load import load_model
import sys

from ..data.datatypes import FashionItem


# ======= Setup paths =======
script_dir = os.path.dirname(os.path.abspath(__file__))
description_file = os.path.join(script_dir, "/content/image_predictions (2).json")
image_folder = os.path.join(script_dir, "/content/DATASET/DATASET/Men")
output_path = os.path.join(script_dir, "/content/my_clip_embeddings (3).pkl")

# ======= Load descriptions from JSON =======
with open(description_file, "r") as f:
    item_descriptions = json.load(f)

# ======= Load model =======
model = load_model(model_type="clip")
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ======= Encode items =======
all_ids = []
all_embeddings = []

for item in tqdm(item_descriptions, desc="Encoding items"):
    item_id = item["id"]
    description = item["articleType"]
    image_path = os.path.join(image_folder, f"{item_id}.jpg")

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

    except Exception as e:
        print(f"[Error] Failed to process {item_id}: {e}")

# ======= Save to pickle =======
if all_embeddings:
    all_embeddings = np.stack(all_embeddings)
    with open(output_path, "wb") as f:
        pickle.dump({"ids": all_ids, "embeddings": all_embeddings}, f)
    print(f"\n Saved {len(all_ids)} embeddings to {output_path}")
else:
    print("\nNo embeddings were saved. Check for missing images or errors.")
