from transformers import AutoModel, AutoProcessor
import torch
from PIL import Image
import pickle
import json
import numpy as np
from transformers import CLIPTokenizer, CLIPTextModelWithProjection
import ConfigPath
# 
# ConfigPath.IMAGE_PREDICTIONS_JSON_PATH= ConfigPath.IMAGE_PREDICTIONS_JSON_PATH


# Device config
device_v = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load metadata from new JSON format
with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH, "r") as f:
    metadata_v = json.load(f)

# Load CLIP image embeddings
with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "rb") as f:
    data_v = pickle.load(f)
    all_ids_v = np.array(data_v['ids'])
    all_embeds_v = torch.tensor(data_v['embeddings'], dtype=torch.float32).to(device_v)

# Load text encoder
model_name_v = "patrickjohncyh/fashion-clip"
tokenizer_v = CLIPTokenizer.from_pretrained(model_name_v)
text_model_v = CLIPTextModelWithProjection.from_pretrained(model_name_v).to(device_v)
text_model_v.eval()

def get_item_ids(semantic_query=None, fine_grained_query=None, event_query=None):
    item_ids = []
    for item in metadata_v:
        matches = False

        if semantic_query and item["Category"].lower() == semantic_query.lower():
            matches = True
        if fine_grained_query and item["articleType"].lower() == fine_grained_query.lower():
            matches = True
        if event_query and item["Event"].lower() == event_query.lower():
            matches = True

        # Add item if any condition matched
        if matches:
            item_ids.append(item["id"].replace(".jpg", ""))  # match embedding ID format

    return item_ids

# Text Encoder that matches training setup
def encode_text_concat_style(text):
    inputs = tokenizer_v(
        text, return_tensors="pt", truncation=True, padding="max_length", max_length=77
    ).to(device_v)
    with torch.no_grad():
        text_embed = text_model_v(**inputs).text_embeds  # [1, 512]
    concat_embed = torch.cat([text_embed, text_embed], dim=-1)  # [1, 1024]
    return concat_embed / concat_embed.norm(p=2, dim=-1, keepdim=True)

# Find top-k matching images from category
def find_top_k_images_in_subcat(query_text, semantic_query=None, fine_grained_query=None, k=5):
    global metadata_v, data_v, all_ids_v, all_embeds_v
    with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH, "r") as f:
        metadata_v = json.load(f)
    
    with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "rb") as f:
        data_v = pickle.load(f)
        all_ids_v = np.array(data_v['ids'])
        all_embeds_v = torch.tensor(data_v['embeddings'], dtype=torch.float32).to(device_v)

    # print("ConfigPath.IMAGE_PREDICTIONS_JSON_PATH:",ConfigPath.IMAGE_PREDICTIONS_JSON_PATH)
    query_embed = encode_text_concat_style(query_text)  # [1, 1024]
    # print("query_embed",query_embed)
    filtered_ids_list = get_item_ids(event_query=query_text,semantic_query=semantic_query, fine_grained_query=fine_grained_query)
    # print("filtered_ids_list",filtered_ids_list)
    if not filtered_ids_list:
        raise ValueError("No items found for the given semantic/fine-grained category.")

    filtered_ids_set = set(filtered_ids_list)
    mask = np.isin(all_ids_v, list(filtered_ids_set))
    filtered_embeds = all_embeds_v[mask]
    filtered_ids = all_ids_v[mask]

    similarities = (filtered_embeds @ query_embed.T).flatten()  # [N] #[CHANGE]
    print("similarities",similarities)
    topk_indices = torch.topk(similarities, k=min(k, len(similarities))).indices.cpu().numpy()

    topk_ids = filtered_ids[topk_indices]
    topk_scores = similarities[topk_indices].cpu().numpy()
    return list(zip(topk_ids, topk_scores))

