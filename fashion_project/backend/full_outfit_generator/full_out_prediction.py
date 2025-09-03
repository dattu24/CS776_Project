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
#ALL files path
Checkpoint_path = "/content/outfit_transformer/checkpoints/complementary_clip_best.pth"
Embeddings= "/content/drive/MyDrive/embeddings/polyvore_0.pkl"
Image_dir = "/content/outfit_transformer/datasets/polyvore/images"
meta_file= "/content/outfit_transformer/datasets/polyvore/item_metadata.json"
#LOAD ITEM DESCRIPTIONS
with open(meta_file) as f:
    desc_data = json.load(f)
# Step 1: Load the categories CSV
df_cat = pd.read_csv("/content/categories.csv", header=None)
df_cat.columns = ["category_id", "fine_grained_category", "semantic_category"]
df_cat["fine_grained_category"] = df_cat["fine_grained_category"].str.replace(" ", "")
catid_to_name = dict(zip(df_cat["category_id"], df_cat["fine_grained_category"]))
id_to_desc = {d["item_id"]: catid_to_name.get(d["category_id"], "unknown") for d in desc_data}
#LOAD PRECOMPUTED EMBEDDINGS
embeddings_data = np.load(Embeddings, allow_pickle=True)
ids_to_embeddings = {id: emb for id, emb in zip(embeddings_data["ids"], embeddings_data["embeddings"])}
#BUILD FASHION ITEM 
def build_item(item_id, use_image=True):
    #print("step1",item_id)
    embeddings = ids_to_embeddings[item_id]
    description = id_to_desc.get(item_id, "")
    image = Image.open(os.path.join(Image_dir, f"{item_id}.jpg")).convert("RGB") if use_image else None
    return FashionItem(item_id=item_id, description=description, embedding=embeddings, image=image)
#LOAD MODEL
model = load_model(model_type="clip", checkpoint=Checkpoint_path)
model.eval()
#STEPWISE OUTFIT BUILDER
def build_outfit(start_item_id, target_descriptions):
    outfit = [build_item(start_item_id, use_image=True)]  # First item has image
    filled_ids = [start_item_id]
    for target_desc in target_descriptions:
        #FILTER CANDIDATES BY DESCRIPTION ---
        candidate_ids = [item_id for item_id, desc in id_to_desc.items() if desc == target_desc and item_id not in filled_ids]
        if not candidate_ids:
            print(f"No candidates found for description '{target_desc}'")
            continue
        candidate_items = [build_item(cid, use_image=False) for cid in candidate_ids]
        # WRAP CURRENT QUERY
        query= FashionComplementaryQuery(outfit=outfit, category="")
        batch_query = [query]
        #PREDICT BEST CANDIDATE
        with torch.no_grad():
            query_emb = model(batch_query, use_precomputed_embedding=True).unsqueeze(1)  
            candiate_emb = model(candidate_items, use_precomputed_embedding=True)           
            candiate_emb = candiate_emb.view(1, len(candidate_items), -1)                       
            dists = torch.norm(query_emb - candiate_emb, dim=-1)                                
            pred_idx = torch.argmin(dists, dim=1).item()
        best_item = candidate_items[pred_idx]
        outfit.append(best_item)
        filled_ids.append(best_item.item_id)
        print(f"Added item: {best_item.item_id} — {best_item.description}")
    return outfit

#VISUALIZE FINAL OUTFIT
def visualize_outfit(outfit, save_path="/content/predicted_full__outfit.png"):
    fig, axs = plt.subplots(1, len(outfit), figsize=(5 * len(outfit), 5))
    for i, item in enumerate(outfit):
        img_path = os.path.join(Image_dir, f"{item.item_id}.jpg")

        img = Image.open(img_path).convert("RGB")
        axs[i].imshow(img)
        axs[i].axis('off')
        axs[i].set_title(f"ID: {item.item_id}\n{item.description}")
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Outfit saved to {save_path}")

#input
parser = argparse.ArgumentParser(description="Build outfit stepwise using a CLIP model.")
parser.add_argument("--start_item", type=int, required=True, help="ID of the starting fashion item (with image).")
parser.add_argument("--target_descs", type=str, nargs="+", required=True, help="List of target descriptions to fill (e.g., pant bag shoes).")
parser.add_argument("--save_path", type=str, default="/content/predicted_full_outfit.png", help="Path to save the final outfit visualization.")

args = parser.parse_args()

final_outfit = build_outfit(args.start_item, args.target_descs)
visualize_outfit(final_outfit, save_path=args.save_path)

