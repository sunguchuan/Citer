import web3
from web3 import Web3
import json
from web3.auto.gethdev import w3
import codecs
from operations import deploy_setup,data,transact
import sys
import ipfsapi
import hashlib

def create_hash(file):  #CREATE A cryptographic HASHID FROM IPFS SERVER
    try:
        connect = ipfsapi.connect('127.0.0.1',5001)  #LOCAL IPFS SERVER, PREVOUSLY INSTALLED
        print("Successful connected to IPFS nectwork")
    except Exception as e:
        print("Unexpected Error, on IPFS::")
        print(e)
        exit(-1)

    res = connect.add(file)
    if res["Hash"]:
        return res["Hash"]
    else:
        return None

def set_data(user,hash):    # Calls operations.py
    contract_address=deploy_setup("userWithConstructor.json",user,hash)
    print('Contract address:',contract_address)

def revoke(address):
    print('Contract address:',address)
    return transact(address,data['abi'],'revoke',source=w3.eth.accounts[0])

if __name__=='__main__':    # arguments:fingerprint file name,contract owner
    id=create_hash(sys.argv[1])
    print('Actural ID:',id)
    hash=hashlib.sha256(id.encode()).hexdigest()    # Hashes the IPFS ID
    print('Hash value:',hash)
    set_data(sys.argv[2],hash)
    # print(revoke(sys.argv[1]))
