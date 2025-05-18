Find a Friend - AI-Powered Pet Detection and Adoption App
Find a Friend is a web application that allows users to upload an image of a dog and enter a ZIP code. The app identifies the dog's breed using a YOLOv8 model and searches for adoptable pets of that breed nearby using the Petfinder API.
________________


Features
* Detects dog breed from an uploaded image using a custom YOLOv8 model
* Searches for adoptable pets of that breed near a given ZIP code
* Clean, responsive frontend built with Bootstrap
* Flask backend for model inference and API communication
________________


Setup Instructions
1. Create and Activate the Virtual Environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows


2. Install Dependencies
pip install -r requirements.txt


Note: API credentials are already included in the .env file. No additional setup is needed for environment variables.
________________


Running the Application
python app.py


Once the server starts, open your browser and go to:


http://127.0.0.1:5000


________________


Project Structure
├── app.py               # Main Flask application
├── main.py              # Model inference and Petfinder API logic
├── index.html           # Frontend interface
├── requirements.txt     # List of Python dependencies
├── .env                 # Contains API keys (preconfigured)
├── uploads/             # Stores uploaded images (auto-created)
├── .gitignore           # Files/folders excluded from version control


________________


.gitignore Contents
.env
__pycache__/
uploads/
*.pt


________________


Model
The project uses a fine-tuned YOLOv8 model named petfinder_best.pt located in the root directory.
________________


API
* Petfinder API (https://www.petfinder.com/developers/)
________________


Troubleshooting
* Make sure the virtual environment is activated before running the app
* Ensure petfinder_best.pt is present in the root directory
* Use valid image files (JPG, PNG) for accurate detection
License
Joseph LaBarbera