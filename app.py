from flask_cors import CORS
from flask import Flask, request, jsonify
from main import run_detection
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template

import os
from main import get_pet_breed, format_breed, get_petfinder_token, find_pets_nearby, get_organization_details

#Must active .venv
#
# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Set static upload folder for results
app.config['UPLOAD_FOLDER'] = 'static/results'

# Handle file uploads and return pet matches
@app.route('/upload', methods=['POST'])
@app.route('/upload', methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Detect breed from image
    breed = run_detection(filepath)
    formatted_breed = format_breed(breed)

    # Get token and search pets
    token = get_petfinder_token()
    location = request.form.get("location", "10001")
    results = find_pets_nearby(formatted_breed, location, token)

    if not isinstance(results, dict):
        return jsonify({
            "success": False,
            "error": "Failed to fetch Petfinder results. Check API credentials."
        }), 500

    pets = []
    for pet in results.get("animals", []):
        name = pet.get("name", "Unknown")
        pet_breed = pet.get("breeds", {}).get("primary", "Unknown")
        contact = pet.get("contact", {})
        city = contact.get("city", "")
        state = contact.get("state", "")
        org_id = pet.get("organization_id")

        # Fallback for missing location
        if not city and org_id:
            org_name, city, state = get_organization_details(org_id, token)
        else:
            org_name = org_id

        location_text = f"{city}, {state}" if city or state else f"Org: {org_name}"
        distance = pet.get("distance", "N/A")

        pets.append({
            "name": name,
            "breed": pet_breed,
            "location": location_text,
            "distance": distance,
            "url": pet.get("url", "#")
        })

    return jsonify({
        "success": True,
        "predicted_breed": breed,
        "formatted_breed": formatted_breed,
        "results": pets
    })

# Alternate endpoint for image and location input
@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files or "location" not in request.form:
        return jsonify({"error": "Image and location required"}), 400

    image = request.files["image"]
    location = request.form["location"]
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    try:
        # Full pipeline: detect breed, format, get token, find pets
        ai_breed = get_pet_breed(image_path)
        breed = format_breed(ai_breed)
        token = get_petfinder_token()
        results = find_pets_nearby(breed, location, token)

        pets = []
        for pet in results.get("animals", []):
            name = pet.get("name", "Unknown")
            pet_breed = pet.get("breeds", {}).get("primary", "Unknown")
            contact = pet.get("contact", {})
            city = contact.get("city", "")
            state = contact.get("state", "")
            org_id = pet.get("organization_id")

            if not city and org_id:
                org_name, org_city, org_state = get_organization_details(org_id, token)
                city = org_city
                state = org_state
            else:
                org_name = org_id

            location_text = f"{city}, {state}" if city or state else f"Org: {org_name}"
            distance = pet.get("distance", "N/A")

            pets.append({
                "name": name,
                "breed": pet_breed,
                "location": location_text,
                "distance": distance
            })

        return jsonify({
            "ai_breed": ai_breed,
            "formatted_breed": breed,
            "results": pets
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
