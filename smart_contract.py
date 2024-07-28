from web3 import Web3

# Connect to your Ethereum node (replace with your Ethereum node URL)
web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))

# Your smart contract ABI
contract_abi = [{"inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}], "name": "getBlockchainAddress", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "imageHashToBlockchainAddress", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}, {"internalType": "string", "name": "blockchainAddress", "type": "string"}], "name": "storeImageHash", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]


# Replace this with your deployed contract address
contract_address = "0xE3Bd8ab97fc41017620c69d300940CF3A52E3A01"

contract = web3.eth.contract(abi=contract_abi, address=contract_address)

def store_image_hash(image_hash, blockchain_address):
    # Replace with your Ethereum address and private key
    sender_address = "0xDFE8c96961D79740123f26875A765622a107fA29"
    private_key = "0x074682f4facd855d0499841dfd5a0fc6b8347c4a117f9359d8d178be19909ab2"

    account = web3.eth.account.from_key(private_key)

    tx = contract.functions.storeImageHash(image_hash, blockchain_address).buildTransaction({
        'chainId': 5777,  # Replace with the correct chain ID
        'gas': 2000000,
        'gasPrice': web3.toWei('20', 'gwei'),
        'nonce': web3.eth.getTransactionCount(sender_address),
    })

    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    return tx_hash

def get_blockchain_address(image_hash):
    blockchain_address = contract.functions.getBlockchainAddress(image_hash).call()
    return blockchain_address
