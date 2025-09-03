from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import json
import pickle

# Import your existing functions
from AttributePredictor.attribute_predictor import predict_labels
from full_outfit_generator.outfit_transformer.src.run.full_out import build_outfit
from full_outfit_generator.m import suggest_flat_outfit
from full_outfit_generator.generate_base.m import find_top_k_images_in_subcat
from update_embedding import update_embedding_online
import ConfigPath
from ConfigPath import USER_MEN

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

TEMP_FOLDER = ConfigPath.TEMP_DIR
os.makedirs(TEMP_FOLDER, exist_ok=True)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


subcategories = [
    "Blazers", "Casualshoes", "Flipflops", "formalshoes", "heels", "jackets",
    "jeans", "Kurtas", "Kurtis", "NehruJackets", "nightsuits", "rainjackets",
    "sandals", "shirts", "shorts", "sportssandals", "sportsshoes", "sweaters",
    "sweatshirts", "trackpants", "tracksuits", "Trousers", "Tshirts", "WaaistCoat","FlipFlops",
]

# --- Image Upload and Attribute Prediction Endpoint ---
@app.route('/api/predict', methods=['POST'])
def predict_attributes():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get predictions
        articleType, category, event = predict_labels(filepath)

        return jsonify({
            'filename': filename,
            'articleType': articleType,
            'category': category,
            'event': event
        })

# --- Outfit Generation Endpoint ---
@app.route('/api/generate-outfit', methods=['POST'])
def generate_outfit_api():
    data = request.json
    start_item_id = data.get('start_item_id')
    target_descriptions = data.get('target_descriptions') # This will be a list of strings

    if not start_item_id:
        return jsonify({'error': 'A starting item ID is required.'}), 400

    # If target_descriptions is not provided or is empty, you might want to have a default behavior
    if not target_descriptions:
        # Example default, adjust as needed
        target_descriptions = ["shirts", "Trousers", "Casualshoes"] 
        
    try:
        # The build_outfit function from your project
        final_outfit = build_outfit(start_item_id, target_descriptions)
        
        # Construct full URLs for the frontend
        base_url = request.host_url
        outfit_image_urls = [f"{base_url}images/{item.item_id}.jpg" for item in final_outfit]

        return jsonify({'outfit_images': outfit_image_urls})
    except Exception as e:
        print(f"Error during outfit generation: {e}")
        return jsonify({'error': 'Failed to generate outfit.'}), 500

# --- Occasion-Based Outfit Generation Endpoint ---
@app.route('/api/generate-occasion-outfit', methods=['POST'])
def generate_occasion_outfit_api():
    data = request.json
    description = data.get('description')

    if not description:
        return jsonify({'error': 'Description is required.'}), 400

    try:
        # --- This logic is adapted directly from your occasion_outfit_page.py ---
        
        # 1. Define the occasion-to-outfit mapping based on user gender
        if ConfigPath.USER == USER_MEN:
            occasion_to_outfit = {
            "wedding": ["shirts", "Blazers", "Trousers", "formalshoes"],
            "office": ["shirts", "Blazers", "Trousers", "formalshoes"],
            "interview": ["shirts", "Blazers", "Trousers", "formalshoes"],
            "gym": ["Tshirts", "trackpants", "sportsshoes"],
            "party": ["shirts", "jeans", "Casualshoes"],
            "casual": ["Tshirts", "shorts", "FlipFlops"],
            "beach": ["Tshirts", "shorts", "FlipFlops"],
            "rain": ["rainjackets", "jeans", "sportssandals"],
            "festival": ["Kurtas",  "Trousers", "formalshoes"],
            "temple": ["Kurtas", "Trousers", "formalshoes"],
            "sport": ["Tshirts", "trackpants", "sportsshoes"],
            "presentation": ["shirts", "Trousers", "Casualshoes"],
            "shopping": ["Tshirts", "Trousers", "sandals"],
        }
        else: # Women
            occasion_to_outfit = {
            "party": ["Dresses", "Heels"],
            "wedding": ["LehengaCholi", "Dupatta", "Heels"],
            "office": ["Shirts", "Trousers", "Casualshoes"],
            "interview": ["Trousers", "Blazers", "formalshoes"],
            "gym": ["Tshirts", "trackPants", "sportsshoes"],
            "casual": ["Tops", "Jeans", "FlipFlops"],
            "beach": ["Tops", "Shorts", "FlipFlops"],
            "shopping": ["Tops", "Trousers", "Flats"],
            "rain": ["Jackets", "trackpants", "Sandals"],
            "temple": ["Kurtis", "Leggings", "Flats"],
            "festival": ["Sarees", "Heels"],
            "sport": ["Tshirts", "trackpants", "sportsshoes"],
            "presentation": ["Shirts", "Blazers","Trousers", "formalshoes"]
        }
        # 2. Suggest an outfit template based on the description
        occasion_s, outfit_s = suggest_flat_outfit(description, subcategories, occasion_to_outfit)
        print(f"Occasion: {occasion_s}")
        if not outfit_s:
            return jsonify({'error': f"Could not determine an outfit for '{occasion_s}'."}), 404

        # 3. Find the best starting item
        # For simplicity, we assume the first item is 'topwear'. You might need more robust logic here.
        semantic_query = "topwear" 
        fine_grained_query_s = outfit_s[0]
        query_text_s = f"{fine_grained_query_s}: {description}"
        target_descriptions = outfit_s[1:]
        # find_top_k_images_in_subcat returns a list of tuples (id, score)
        print("query_text_s, semantic_query, fine_grained_query_s:", query_text_s,"|", semantic_query,"|", fine_grained_query_s)
        top_k_results_s = find_top_k_images_in_subcat(query_text_s, semantic_query, fine_grained_query_s, k=1)
        print("top_k_results_s:", top_k_results_s)
        if not top_k_results_s:
            return jsonify({'error': f"No matching base items found for '{fine_grained_query_s}'."}), 404

        start_item_id = top_k_results_s[0][0]

        # 4. Build the rest of the outfit
        final_outfit = build_outfit(start_item_id, target_descriptions)
        print("final_outfit:", final_outfit)
        # 5. Return the image URLs
        base_url = request.host_url
        outfit_image_urls = [f"{base_url}images/{item.item_id}.jpg" for item in final_outfit]
        
        return jsonify({'outfit_images': outfit_image_urls})

    except Exception as e:
        print(f"Error during occasion outfit generation: {e}")
        return jsonify({'error': 'Failed to generate occasion-based outfit.'}), 500

def get_id():
    for i in range(1, 101):
        file_path = os.path.join(ConfigPath.USER_DIR, f"{i}.jpg")
        if not os.path.exists(file_path):
            # print(f"Missing file: {i}.jpg")
            return i

# --- New Item Upload Endpoint ---
@app.route('/api/upload-item', methods=['POST'])
def upload_item_api():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    files = request.files.getlist('files')
    if len(files) == 0 or files[0].filename == '':
        return jsonify({'error': 'No files selected for uploading'}), 400
    if not os.path.exists(ConfigPath.TEMP_DIR):
        os.makedirs(ConfigPath.TEMP_DIR)  
    processed_files = []
    errors = []

    for file in files:
        if file:
            try:
                # Save the file temporarily
                file_id = get_id()
                filename_file_id = str(file_id) + ".jpg"
                dest_path = os.path.join(ConfigPath.TEMP_DIR, filename_file_id)
                print("dest_path:",dest_path)
                file.save(dest_path)

                # Use your existing script to process the new image.
                # This function handles moving the file, predicting attributes,
                # and updating the embedding file.
                update_embedding_online(dest_path)
                
                processed_files.append(dest_path)
            except Exception as e:
                error_message = f"Failed to process {file.filename}: {str(e)}"
                print(error_message)
                errors.append(error_message)

    if errors:
         return jsonify({
            'message': 'Some files could not be processed.',
            'processed': processed_files,
            'errors': errors
        }), 500

    return jsonify({
        'message': f'Successfully uploaded and processed {len(processed_files)} item(s).',
        'processed_files': processed_files
    }), 201

# --- Endpoint to LIST all user items ---
@app.route('/api/user-items', methods=['GET'])
def get_user_items():
    try:
        # Get all .jpg files from the user directory
        image_files = [f for f in os.listdir(ConfigPath.USER_DIR) if f.lower().endswith('.jpg')]
        
        # Create a list of objects with id and URL
        base_url = request.host_url
        items = [{
            'id': os.path.splitext(filename)[0],
            'url': f"{base_url}images/{filename}"
        } for filename in image_files]
        
        return jsonify(items)
    except Exception as e:
        print(f"Error listing user items: {e}")
        return jsonify({'error': 'Could not retrieve user items.'}), 500

# --- Endpoint to DELETE selected items ---
@app.route('/api/delete-items', methods=['POST'])
def delete_items_api():
    data = request.json
    item_ids_to_delete = data.get('item_ids') # Expecting a list of strings

    if not item_ids_to_delete:
        return jsonify({'error': 'No item IDs provided for deletion.'}), 400

    # This logic is adapted from your delete_image_page.py
    try:
        # 1. Update JSON metadata
        if os.path.exists(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH):
            with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH, "r") as f:
                json_data = json.load(f)
            updated_json_data = [item for item in json_data if item["id"] not in item_ids_to_delete]
            with open(ConfigPath.IMAGE_PREDICTIONS_JSON_PATH, "w") as f:
                json.dump(updated_json_data, f, indent=4)

        # 2. Update embeddings pickle file
        if os.path.exists(ConfigPath.CLIP_EMBEDDING_PKL_PATH):
            with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "rb") as f:
                embedding_data = pickle.load(f)
            
            # Find indices to remove
            indices_to_remove = [i for i, item_id in enumerate(embedding_data['ids']) if item_id in item_ids_to_delete]
            
            # Remove items by index in reverse order to avoid shifting issues
            for index in sorted(indices_to_remove, reverse=True):
                del embedding_data['ids'][index]
                # Assuming embeddings is a list of arrays, we need to handle it carefully
                embedding_data['embeddings'] = [emb for i, emb in enumerate(embedding_data['embeddings']) if i != index]

            with open(ConfigPath.CLIP_EMBEDDING_PKL_PATH, "wb") as f:
                pickle.dump(embedding_data, f)

        # 3. Delete the image files
        for item_id in item_ids_to_delete:
            image_path = os.path.join(ConfigPath.USER_DIR, f"{item_id}.jpg")
            if os.path.exists(image_path):
                os.remove(image_path)

        return jsonify({'message': f'Successfully deleted {len(item_ids_to_delete)} items.'})

    except Exception as e:
        print(f"Error during item deletion: {e}")
        return jsonify({'error': 'An error occurred while deleting items.'}), 500




# --- Static File Server for Images ---
@app.route('/images/<path:filename>')
def serve_image(filename):
    # This assumes your images are in a folder that the backend can access.
    # You might need to adjust the path based on your `ConfigPath.py`
    # For simplicity, let's assume a single USER_DIR
    from ConfigPath import USER_DIR
    return send_from_directory(USER_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)