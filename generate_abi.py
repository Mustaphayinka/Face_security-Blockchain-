from solcx import compile_standard
import json

# Solidity source code for your contract
solidity_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FaceSecurity {
    struct DataEntry {
        string imageHash;
        string blockchainAddress;
    }

    mapping(uint256 => DataEntry) public dataEntries;
    uint256 public numEntries;

    event DataStored(uint256 indexed index, string imageHash, string blockchainAddress);

    function storeImageHash(string memory imageHash, string memory blockchainAddress) public {
        dataEntries[numEntries] = DataEntry(imageHash, blockchainAddress);
        emit DataStored(numEntries, imageHash, blockchainAddress);
        numEntries++;
    }

    function getNumEntries() public view returns (uint256) {
        return numEntries;
    }

    function getDataEntry(uint256 index) public view returns (string memory, string memory) {
        require(index < numEntries, "Index out of range");
        DataEntry storage entry = dataEntries[index];
        return (entry.imageHash, entry.blockchainAddress);
    }
}
"""

# Compile the Solidity source code and return the output
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "FaceSecurity.sol": {
            "content": solidity_source
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi"]
            }
        }
    }
})

# Extract the ABI from the compilation output
contract_abi = compiled_sol["contracts"]["FaceSecurity.sol"]["FaceSecurity"]["abi"]

# Write the ABI to a JSON file
with open("FaceSecurity.abi", "w") as abi_file:
    json.dump(contract_abi, abi_file)


print("done with it")