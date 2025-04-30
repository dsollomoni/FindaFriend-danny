from flask_cors import CORS
from flask import Flask, request, jsonify
import os
from main import get_pet_breed, format_breed, get_petfinder_token, find_pets_nearby, get_organization_details

app = Flask(__name__)
CORS(app) 
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files or "location" not in request.form:
        return jsonify({"error": "Image and location required"}), 400

    image = request.files["image"]
    location = request.form["location"]
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    try:
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

if __name__ == "__main__":
    app.run(debug=True)
