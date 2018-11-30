# Enabling Secure and Privacy Preserving Authentication via Blockchain/Smart Contract and Biometrics
Source code of a Citer project

# Requirements for python:
Python 3.6
Commands.txt
Requests

Flask

cryptography

# Requirements for command:
curl

powershell (for windows)

# Test step 1: Create some miner nodes and register them to each other
In miner/

$./startup.sh {# of nodes that you want to create}

# Step 2: Add a set of fingerprints hashes to the blockchain
In authority/

$./add_bio.sh

# Step 3: Verification of one fingerprint
In security_check

See cmd.txt
