from pathlib import Path
PROJECT_ROOT = Path.cwd()
IMAGE_PREDICTIONS_WOMEN_JSON_PATH = PROJECT_ROOT/"full_outfit_generator"/"generate_base"/"women.json"
IMAGE_PREDICTIONS_MEN_JSON_PATH = PROJECT_ROOT/"full_outfit_generator"/"generate_base"/"image_predictions (2).json"
IMAGE_PREDICTIONS_JSON_PATH = IMAGE_PREDICTIONS_MEN_JSON_PATH

CLIP_EMBEDDING_MEN_PKL_PATH=PROJECT_ROOT/"full_outfit_generator"/"generate_base"/"my_clip_embeddings (3).pkl"
CLIP_EMBEDDING_WOMEN_PKL_PATH=PROJECT_ROOT/"full_outfit_generator"/"generate_base"/"women_embeddings.pkl"
CLIP_EMBEDDING_PKL_PATH=CLIP_EMBEDDING_MEN_PKL_PATH

ATTRIBUTE_PRED_PKL_DIR =PROJECT_ROOT/"AttributePredictor"/"PKL_files"

CHECKPOINT_CLIP_BEST_PKL_PATH = PROJECT_ROOT/"full_outfit_generator"/"outfit_transformer"/"checkpoints"/"complementary_clip_best.pth"

USER_MEN_DIR = PROJECT_ROOT/"DATASET_used"/"Men"
USER_WOMEN_DIR = PROJECT_ROOT/"DATASET_used"/"Women"
USER_DIR = USER_MEN_DIR

OUR_IMAGE_DIR = PROJECT_ROOT/"our_dataset"
TEMP_DIR=PROJECT_ROOT/"temp"

USER_MEN = "MEN"
USER_WOMEN = "WOMEN"
USER = USER_MEN