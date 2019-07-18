import web3
from web3 import Web3
import json
from web3.auto.gethdev import w3
import codecs
from operations import data,transact,get_return_value
import sys
import os
import ipfsapi
import hashlib

# import keras
# from keras.preprocessing import image

# sys.path.append('../BioHash-master-3')
# from BioHash import connect2IPFS, train_model, generate_biohash, compare_biohash, train_fingerprint_model, compare_biohashEuclidianDistance

authority='0x64a20b6347347444a970C5B8ad099125C3f01EbD'
user='0x8699c6B603735B661D58E51F5dA23744Be0Abe41'


# def get_data(id):
#     try:
#         connect = ipfsapi.connect('127.0.0.1',5001)  #LOCAL IPFS SERVER, PREVOUSLY INSTALLED
#         print("Successful connected to IPFS nectwork")
#     except Exception as e:
#         print("Unexpected Error, on IPFS::")
#         print(e)
#         exit(-1)
#     return connect.cat(id)


def compare_finger(id): # Uses NBIS verification
    os.system('ipfs get '+id+' -o ./Issuer/original.bmp')   # Get IPFS ID
    os.system('/usr/local/NBIS/Main/bin/cwsq .75 wsq ./Issuer/original.bmp -r 300,400,8')
    os.system('/usr/local/NBIS/Main/bin/cwsq .75 wsq ./Verifier/collected.bmp -r 300,400,8')
    os.system('/usr/local/NBIS/Main/bin/mindtct -b -m1 ./Issuer/original.wsq ./Issuer/original')
    os.system('/usr/local/NBIS/Main/bin/mindtct -b -m1 ./Verifier/collected.wsq ./Verifier/collected')
    os.system('/usr/local/NBIS/Main/bin/bozorth3 -o score.txt ./Issuer/original.xyt ./Verifier/collected.xyt')
    scorefs=open('score.txt')
    score=scorefs.read()
    scorefs.close()
    if int(score)>=20:
        return 1
    else:
        return 0

def check_data(contract_address,id):    # Used to make verification
    #verify authority address
    auth=get_return_value(contract_address,data['abi'],'get_auth',source=user)
    if auth==authority:
        print('Valid authority')
        res=get_return_value(contract_address,data['abi'],'retrieve',source=user)
        res2=hashlib.sha256(codecs.encode(id)).digest()
        if res2==res:
            # print('ID data match')
            # retrieve=get_data(id)
            # ifs=open(file,'rb')
            # content=ifs.read()
            # biohash1 = generate_biohash(retrieve)
            # biohash2 = generate_biohash(content)
            # print('Biohash 1:',biohash1)
            # print('Biohash 2:',biohash2)
            # if compare_biohash(biohash1, biohash2, True)==0:
            if compare_finger(id)==1:
                print('Fingerprint data match')
                return 1
            else:
                print('Fingerprint data do not match')
                return 0
        else:
            # print(res)
            # print(res2)
            print('ID data do not match')
            return -1
    else:
        print('Invalid authority')


if __name__=='__main__':    # arguments:contract address, ipfs id
    res=check_data(sys.argv[1],sys.argv[2])
    print(res)
