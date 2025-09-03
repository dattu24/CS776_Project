import spacy
import re
from ConfigPath import USER_MEN
import ConfigPath
# from generate_base.m import find_top_k_images_in_subcat
# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# # Your supported fashion subcategories for men
# subcategories = [
#     "Blazers", "Casualshoes", "Flipflops", "formalshoes", "heels", "jackets",
#     "jeans", "Kurtas", "Kurtis", "NehruJackets", "nightsuits", "rainjackets",
#     "sandals", "shirts", "shorts", "sportssandals", "sportsshoes", "sweaters",
#     "sweatshirts", "trackpants", "tracksuits", "Trousers", "Tshirts", "WaaistCoat"
# ]

# # Occasion to outfit mapping (flat and clean)
# occasion_to_outfit = {
#     "wedding": ["shirts", "Blazers", "Trousers", "formalshoes"],
#     "office": ["shirts", "Blazers", "Trousers", "formalshoes"],
#     "interview": ["shirts", "Blazers", "Trousers", "formalshoes"],  # New
#     "gym": ["Tshirts", "trackpants", "sportsshoes"],
#     "party": ["shirts", "jeans", "Casualshoes"],
#     "casual outing": ["Tshirts", "shorts", "Casualshoes"],
#     "beach": ["Tshirts", "shorts", "FlipFlops"],  # New
#     "rainy day": ["rainjackets","Tshirts", "jeans", "sportssandals"],
#     "festive": ["Kurtas",  "Trousers", "formalshoes"],
#     "ethnic": ["Kurtas", "Trousers", "formalshoes"],  # New
#     "sports event": ["Tshirts", "shorts", "sportsshoes"]
# }

def extract_occasion_with_spacy(description, known_occasions):
    """Try to extract the occasion using spaCy NER, fallback to keyword match."""
    doc = nlp(description.lower())

    for ent in doc.ents:
        if ent.label_ in ["EVENT", "ORG", "GPE", "DATE"]:
            ent_text = ent.text.strip()
            if ent_text in known_occasions:
                return ent_text

    text = description.lower()
    for occasion in known_occasions:
        if occasion in text:
            return occasion
        # Handle variations
        if occasion == "ethnic" and "ethnic wear" in text:
            return "ethnic"
        if occasion == "interview" and "interview" in text:
            return "interview"
        if occasion == "rainy day" and "rainy" in text:
            return "rainy day"
        if occasion == "sleepwear" and any(w in text for w in ["sleepwear", "sleep", "bedtime"]):
            return "sleepwear"
        if occasion == "beach" and "beach" in text:
            return "beach"
        if occasion == "shopping" and "shopping" in text:
            return "shopping"
        if occasion == "presentation" and "presentation" in text:
            return "presentation"
        if "sport" in text:
            return "sports event"
    return "unknown"

def suggest_flat_outfit(description, subcategories, outfit_map):
    """Return a flat list of outfit subcategories based on the detected occasion."""
    occasion = extract_occasion_with_spacy(description, outfit_map.keys())
    print("ocassion")
    if occasion == "unknown":
        if(ConfigPath.USER==USER_MEN):
            return description, ["shirts","Jeans","FlipFlops"]
        else:
            return description, ["Tops","Jeans","Flats"]

    # Filter to valid subcategories only
    outfit = [item for item in outfit_map[occasion]]
    print(outfit_map)
    return occasion,outfit
