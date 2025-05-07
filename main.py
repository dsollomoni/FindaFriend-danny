from ultralytics import YOLO
import requests
import os
import cv2
from dotenv import load_dotenv

load_dotenv()

# API STUFF
PETFINDER_API_KEY = os.getenv("PETFINDER_API_KEY")
PETFINDER_API_SECRET = os.getenv("PETFINDER_API_SECRET")
MODEL_PATH = "petfinder_best.pt"

# AI MODEL
def get_pet_breed(image_path):
    model = YOLO(MODEL_PATH)
    results = model(image_path)

    for result in results:
        class_ids = result.boxes.cls.tolist()
        for cls_id in class_ids:
            return result.names[int(cls_id)]

# FORMAT BREED NAME FOR PETFINDER
def format_breed(ai_breed):
    breed = ai_breed.replace("dog-", "").replace("_", " ")
    return breed.title()

# GET PETFINDER ACCESS TOKEN
def get_petfinder_token():
    res = requests.post("https://api.petfinder.com/v2/oauth2/token", data={
        "grant_type": "client_credentials",
        "client_id": PETFINDER_API_KEY,
        "client_secret": PETFINDER_API_SECRET
    })

    if res.status_code != 200:
        print("Failed to get token:", res.json())
        return None

    return res.json().get("access_token")

# SEARCH PETS
def find_pets_nearby(breed, location, token):
    if not token:
        return []

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "type": "dog",
        "breed": breed,
        "location": location,
        "distance": 100,
        "limit": 15,
        "sort": "distance"
    }

    res = requests.get("https://api.petfinder.com/v2/animals", headers=headers, params=params)
    return res.json()

# GET ORG DETAILS IF LOCATION IS MISSING
def get_organization_details(org_id, token):
    url = f"https://api.petfinder.com/v2/organizations/{org_id}"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        org = res.json().get("organization", {})
        name = org.get("name", org_id)
        city = org.get("address", {}).get("city", "")
        state = org.get("address", {}).get("state", "")
        return name, city, state
    return org_id, "", ""

# Load the model once at module level
model = YOLO("petfinder_best.pt")

def run_detection(input_path):
    img = cv2.imread(input_path)
    results = model(img)

    predicted_class = "Unknown"

    for r in results:
        class_ids = r.boxes.cls.tolist()
        if class_ids:
            predicted_class = r.names[int(class_ids[0])]
        break

    return predicted_class
