from concurrent.futures import ProcessPoolExecutor
import cv2
import os
from flask import Flask, render_template, request, redirect
from web3 import Web3
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Connect to the Ethereum node
web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))

# Load the deployed contract
contract_address = "0x168A4b8619C9A99D97A8F638a7C73f0258a52E13"
contract_abi = [{"inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}], "name": "getBlockchainAddress", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "imageHashToBlockchainAddress", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}, {"internalType": "string", "name": "blockchainAddress", "type": "string"}], "name": "storeImageHash", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Configure the upload folder and allowed file extensions
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "123456789#"

# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to save the uploaded image
def save_uploaded_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_path)
        return saved_path
    return None

# Function to process the uploaded image (e.g., face detection)
def process_image(filename):
    img = cv2.imread(filename)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    _, ext = os.path.splitext(filename)
    processed_filename = 'file' + ext
    processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
    cv2.imwrite(processed_path, img)

    return processed_path

# Function to generate the image hash
def generate_image_hash(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_hash = hashlib.sha256(image_data).hexdigest()
    return image_hash

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    uploaded_image = None
    processed_image = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        saved_path = save_uploaded_image(file)
        if saved_path:
            uploaded_image = saved_path

            # Process the image (detect faces) in parallel
            with ProcessPoolExecutor() as executor:
                processed_image = executor.submit(process_image, saved_path).result()

            # Perform smart contract interaction here if needed
            image_hash = generate_image_hash(saved_path)
            blockchain_address = "0xd2C159Da7CB087C5c1a6Aa08aFA68cdF03F943a9"
            contract.functions.storeImageHash(image_hash, blockchain_address).transact({'from': '0xd2C159Da7CB087C5c1a6Aa08aFA68cdF03F943a9'})

    return render_template('index.html', uploaded_image=uploaded_image, processed_image=processed_image)

if __name__ == '__main__':
    app.run(debug=True)
