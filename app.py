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
contract_address = "0x60aD80F54B293EB964f061eEf73c13830DdB170f"
contract_abi = [{"inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}], "name": "getBlockchainAddress", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "imageHashToBlockchainAddress", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}, {"internalType": "string", "name": "blockchainAddress", "type": "string"}], "name": "storeImageHash", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Configure the upload folder and allowed file extensions
UPLOAD_FOLDER = 'static'

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "123456789#"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file):
    if file and allowed_file(file.filename):
        filename = 'file.' + file.filename.rsplit('.', 1)[1].lower()
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_path)
        return saved_path
    return None


def process_image(filename):
    img = cv2.imread(filename)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    processed_filename = 'file.' + filename.rsplit('.', 1)[1].lower()
    processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
    cv2.imwrite(processed_path, img)

    return processed_path


def generate_image_hash(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_hash = hashlib.sha256(image_data).hexdigest()
    return image_hash


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
            processed_image = process_image(saved_path)

            image_hash = generate_image_hash(saved_path)
            blockchain_address = "0xd2C159Da7CB087C5c1a6Aa08aFA68cdF03F943a9"
            contract.functions.storeImageHash(image_hash, blockchain_address).transact({'from': '0xd2C159Da7CB087C5c1a6Aa08aFA68cdF03F943a9'})

    return render_template('index.html', uploaded_image=uploaded_image, processed_image=processed_image)

@app.route('/blocks', methods=['GET'])
def view_blocks():
    # Fetch data from the blockchain using your contract's functions
    blockchain_data = []
    
    # Get the latest block number
    latest_block_number = web3.eth.block_number
    print("latest_block_number", latest_block_number)
    # Iterate through blocks and fetch necessary data
    for block_number in range(latest_block_number, 0, -1):
        block = web3.eth.get_block(block_number)
        block_data = {
            'block_number': block['number'],
            'timestamp': block['timestamp'],
            'hash': block['hash'],
            'parent_hash': block['parentHash'],
            'transactions': block['transactions']
            # Add more data fields as needed
        }
        blockchain_data.append(block_data)

    return render_template('blocks.html', blockchain_data=blockchain_data)



if __name__ == '__main__':
    app.run(debug=True)