import web3
from web3 import Web3
import json
from web3.auto.gethdev import w3
import codecs

# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
w3.eth.defaultAccount = w3.eth.accounts[0]


def deploy_setup(jsonfile,user,hash):   # Used to deploy smart contracts
    with open(jsonfile, 'r') as f:
        data= json.load(f)
    contract = w3.eth.contract(abi=data['abi'], bytecode=data['bytecode'])
    tx_hash = contract.constructor(user,hash).transact(transaction={'from': w3.eth.accounts[0],'gas':1000000})
    # tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0],'gas':1000000}) # default account: transaction={'from': w3.eth.accounts[0]}
    # hexhash=codecs.encode(tx_hash,'hex')
    # hash=codecs.decode(hexhash)
    w3.eth.waitForTransactionReceipt(tx_hash)
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return tx_receipt['contractAddress']

def transact(address,abi,function_name,argv={},source=w3.eth.defaultAccount):   # Used to make transactions like authorization
    valid_address = w3.toChecksumAddress(address)
    contract=w3.eth.contract(address=valid_address,abi=abi)
    tx_hash=getattr(contract.functions,function_name)(**argv).transact({'from': source,'gas':500000})
    w3.eth.waitForTransactionReceipt(tx_hash)
    hexhash=codecs.encode(tx_hash,'hex')
    hash=codecs.decode(hexhash)
    return hash

def get_return_value(address,abi,function_name,argv={},source=w3.eth.defaultAccount): # Used to get information without making changes to the contract
    valid_address = w3.toChecksumAddress(address)
    contract=w3.eth.contract(address=valid_address,abi=abi)
    res=getattr(contract.functions,function_name)(**argv).call({'from':source})
    return res;

# if __name__=='__main__':
    # 0. deploy
# contract_address=deploy_json("userRecord.json")
# print('Contract address:',contract_address)

# get abi and contract address for other operations
# contract_address='0x227FD6E7eE87377eBdaC5E5d881aEB61b34f8453'
with open("userRecord.json", 'r') as f:
    data= json.load(f)

    # 1. setup
# user='0xC5B3fdb9B3119Fc680e8A992E080F7CDAa867d95'
# hash='0x922eef94c9acf086f496a838863b77521c77a5cfb4cfb23a3aee1d53b0bffbbe'
# hash='0x5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5'
# print(transact(contract_address,data['abi'],'setup',{'user':user,'hash':hash},w3.eth.accounts[0]))

    # 2. authorize
    # authorized_user='0x8699c6B603735B661D58E51F5dA23744Be0Abe41'
    # print(transact(contract_address,data['abi'],'authorize',{'user':authorized_user,'valid_time':300},w3.eth.accounts[1]))

    # 3. retrieve
# res=get_return_value(contract_address,data['abi'],'retrieve',source=w3.eth.accounts[2])
# print(res)
