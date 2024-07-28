import solcx
import os

# solcx.install.install_solc("0.8.0")

# Set the Solidity compiler version you want to use
solcx.set_solc_version('0.8.0')

# Specify the path to your Solidity source file
solidity_source_file = os.path.abspath("FaceSecurity.sol")

with open(solidity_source_file, 'r') as file:
    solidity_source = file.read()

compiled_sol = solcx.compile_source(solidity_source)

# Extract the bytecode for your contract
bytecode = compiled_sol['<stdin>:FaceSecurity']['bin']

with open("FaceSecurity.bin", "w") as bin_file:
    bin_file.write(bytecode)

print('done with it')
