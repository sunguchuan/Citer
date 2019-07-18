import web3
from web3 import Web3
import json
from web3.auto.gethdev import w3
import codecs
from operations import data,transact
import sys
import ipfsapi
import hashlib

my_account='0xC5B3fdb9B3119Fc680e8A992E080F7CDAa867d95'

def authorize(contract_address,authorized_user,time):
    return transact(contract_address,data['abi'],'authorize',{'user':authorized_user,'valid_time':time},my_account)

if __name__=='__main__':    # arguments:contract_address,authorized_user,time
    tx_hash=authorize(sys.argv[1],sys.argv[2],int(sys.argv[3]))
    print(tx_hash)
