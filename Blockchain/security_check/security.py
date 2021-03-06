import hashlib
import json
import copy

from time import time,sleep
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

import rsa
import cryptography

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

from cryptography.exceptions import InvalidSignature

import sys
import os
import _thread

class Security:
    def __init__(self):
        self.govData=self.getFileData('govpub.pem')
        self.govPubkey=serialization.load_pem_public_key(
            self.govData,
            backend=default_backend()
        )

    def getFileData(self,filename):
        input=open(filename,'rb')
        res=input.read()
        input.close()
        return res

    def hashimage(self,img):
        data=self.getFileData(img)
        hash = hashlib.sha256(data).hexdigest()
        return hash

    def collect_verify(self,original_image):
        # print('Original image hash:',hash1)
        ofs=open('C:/Users/networksLab/Pictures/score.txt')
        score=ofs.read()
        ofs.close()
        if int(score) >= 20:
            hash1=self.hashimage(original_image)
            return hash1

    def hash_verify(self,target,hash,node='128.153.187.131:5002'):
        response = requests.get(f'http://{node}/chain')
        if response.status_code == 200:
            chain = response.json()['chain']
            targetfs=open(target)
            targetData=targetfs.read()
            targetfs.close()
            for block in reversed(chain):
                for entry in block['data']:
                    if entry['public key']==targetData:
                        b=base64.b64decode(entry['signature'])
                        info=entry['info']
                        print('Retrieved hash:',info)
                        print('Index:',block['index'])
                        print('User ID:',targetData)
                        try:
                            self.govPubkey.verify(b,info.encode(),padding.PKCS1v15(), hashes.SHA256())
                        except InvalidSignature:
                            print('invalid signature!')
                            return 0
                        if info==hash:
                            return 1
                        else:
                            return -1

            # Target is not in the blockchain
            print('Target not found')

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
security = Security()

@app.route('/data/verify',methods=['POST'])
def retrieve_verify():
    values=request.get_json()
    required=['node','target','original_image']
    if not all(k in values for k in required):
        return 'Missing values\n', 400

    res1=security.collect_verify(values['original_image'])
    if res1 is None:
        return 'Pictures do not match\n', 200

    res2=security.hash_verify(values['target'],res1,values['node'])
    if res2 is None:
        return 'Connection failed\n', 400
    elif res2==1:
        return 'Verification success\n', 200
    elif res2==-1:
        return 'Target not found\n', 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port, threaded=True)
