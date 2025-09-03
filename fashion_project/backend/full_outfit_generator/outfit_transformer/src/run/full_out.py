import os
import json
import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import argparse
import pandas as pd
from ..models.load import load_model
from ..data.datatypes import FashionItem, FashionComplementaryQuery
from ConfigPath import CHECKPOINT_CLIP_BEST_PKL_PATH
import ConfigPath
#ALL files path
Checkpoint_path = CHECKPOINT_CLIP_BEST_PKL_PATH
# ConfigPath.CLIP_EMBEDDING_PKL_PATH= ConfigPath.CLIP_EMBEDDING_PKL_PATH
# ConfigPath.IMAGE_PREDICTIONS_JSON_PATH= ConfigPath.IMAGE_PREDICTIONS_JSON_PATH
#LOAD ITEM DESCRIPTIONS
with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH) as f:
    desc_data = json.load(f)
# Step 1: Load the categories CSV
id_to_desc = {str(d["id"]): d["articleType"].replace(" ","") for d in desc_data}
#LOAD PRECOMPUTED EMBEDDINGS
embeddings_data = np.load(ConfigPath.CLIP_EMBEDDING_PKL_PATH, allow_pickle=True)
ids_to_embeddings = {id: emb for id, emb in zip(embeddings_data["ids"], embeddings_data["embeddings"])}
#BUILD FASHION ITEM 
def build_item(item_id, use_image=True):
    # global embeddings_data, ids_to_embeddings, desc_data, id_to_desc
    # embeddings_data = np.load(ConfigPath.CLIP_EMBEDDING_PKL_PATH, allow_pickle=True)
    # ids_to_embeddings = {id: emb for id, emb in zip(embeddings_data["ids"], embeddings_data["embeddings"])}

    # with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH) as f:
    #     desc_data = json.load(f)
    # id_to_desc = {str(d["id"]): d["articleType"].replace(" ","") for d in desc_data}

    embeddings = ids_to_embeddings[str(item_id)]
    description = id_to_desc.get(str(item_id), "")
    image = Image.open(os.path.join(ConfigPath.USER_DIR, f"{item_id}.jpg")).convert("RGB") if use_image else None
    return FashionItem(item_id=item_id, description=description, embedding=embeddings, image=image)
#LOAD MODEL
model = load_model(model_type="clip", checkpoint=Checkpoint_path)
model.eval()
#STEPWISE OUTFIT BUILDER
def build_outfit(start_item_id, target_descriptions):
    global embeddings_data, ids_to_embeddings, desc_data, id_to_desc
    
    embeddings_data = np.load(ConfigPath.CLIP_EMBEDDING_PKL_PATH, allow_pickle=True)
    ids_to_embeddings = {id: emb for id, emb in zip(embeddings_data["ids"], embeddings_data["embeddings"])}

    with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH) as f:
        desc_data = json.load(f)
    id_to_desc = {str(d["id"]): d["articleType"].replace(" ","") for d in desc_data}

    print("ConfigPath.CLIP_EMBEDDING_PKL_PATH",ConfigPath.CLIP_EMBEDDING_PKL_PATH)
    print("ConfigPath.IMAGE_PREDICTIONS_JSON_PATH",ConfigPath.IMAGE_PREDICTIONS_JSON_PATH)
    print("start_item_id",start_item_id)
    outfit = [build_item(start_item_id, use_image=True)]  # First item has image
    filled_ids = [start_item_id]
    
    for target_desc in target_descriptions:
        candidate_ids = [item_id for item_id, desc in id_to_desc.items()
                         if desc.lower() == target_desc.lower() and item_id not in filled_ids]
        if not candidate_ids:
            print(f"No candidates found for description '{target_desc}'")
            continue
        
        candidate_items = [build_item(cid, use_image=False) for cid in candidate_ids]
        query = FashionComplementaryQuery(outfit=outfit, category="")
        batch_query = [query]

        with torch.no_grad():
            query_emb = model(batch_query, use_precomputed_embedding=True).unsqueeze(1)
            candidate_emb = model(candidate_items, use_precomputed_embedding=True)
            candidate_emb = candidate_emb.view(1, len(candidate_items), -1)
            dists = torch.norm(query_emb - candidate_emb, dim=-1).squeeze(0)
            sorted_indices = torch.argsort(dists).tolist()

        for idx in sorted_indices:
            best_item = candidate_items[idx]
            image_path = os.path.join(ConfigPath.USER_DIR, f"{best_item.item_id}.jpg")
            if os.path.exists(image_path):
                best_item.image = Image.open(image_path).convert("RGB")
                outfit.append(best_item)
                filled_ids.append(best_item.item_id)
                print(f"Added item: {best_item.item_id} — {best_item.description}")
                break
        else:
            print(f"No available image found for any candidate matching '{target_desc}'")

    return outfit

#VISUALIZE FINAL OUTFIT
def visualize_outfit(outfit, save_path="/content/predicted_full__outfit.png"):
    fig, axs = plt.subplots(1, len(outfit), figsize=(5 * len(outfit), 5))
    for i, item in enumerate(outfit):
        img_path = os.path.join(ConfigPath.USER_DIR, f"{item.item_id}.jpg")

        img = Image.open(img_path).convert("RGB")
        axs[i].imshow(img)
        axs[i].axis('off')
        axs[i].set_title(f"ID: {item.item_id}\n{item.description}")
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Outfit saved to {save_path}")

#input
parser = argparse.ArgumentParser(description="Build outfit stepwise using a CLIP model.")
# parser.add_argument("--start_item", type=int, required=True, help="ID of the starting fashion item (with image).")
# parser.add_argument("--target_descs", type=str, nargs="+", required=True, help="List of target descriptions to fill (e.g., pant bag shoes).")
# parser.add_argument("--save_path", type=str, default="/content/predicted_full_outfit.png", help="Path to save the final outfit visualization.")

args = parser.parse_args()
# print("args.start_item, args.target_descs:", args.start_item, args.target_descs)
# final_outfit = build_outfit(args.start_item, args.target_descs)
# print(final_outfit)
# visualize_outfit(final_outfit, save_path=args.save_path)

