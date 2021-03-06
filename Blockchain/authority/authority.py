import hashlib
import json
import copy

from time import time,sleep
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

import cryptography

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

from cryptography.exceptions import InvalidSignature

import _thread

class Authority:
    def __init__(self):
        self.retrived_data=None
        self.govData=self.getFileData('govpub.pem')
        self.users=0

    def getFileData(self,filename):
        input=open(filename,'rb')
        res=input.read()
        input.close()
        return res

    def fsign(self, data, private_key, pubkey, node='128.153.187.131:5001'):
        self.users = self.users+1
        key=self.getFileData(private_key)
        public=self.getFileData(pubkey)
        prikey = serialization.load_pem_private_key(
            key,
            password=None,
            backend=default_backend()
        )

        hashfile='info'+str(self.users)+'.txt'
        datafs=open(hashfile,'w')
        datafs.write(data)
        datafs.close()

        signature = prikey.sign(
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        sigfile='fromgov'+str(self.users)+'.bin'
        sigfs = open(sigfile, 'wb')
        sigfs.write(signature)
        sigfs.close()

        signature_string=base64.b64encode(signature).decode()
        key_string=public.decode()
        requests.post(f'http://{node}/data/new',json={'pubkey':key_string,'info':data,'govsig':signature_string})
        return signature

    def hashimage(self,img):
        data=self.getFileData(img)
        hash = hashlib.sha256(data).hexdigest()
        return hash

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Node
authority = Authority()

@app.route('/hsign', methods=['POST'])
def hash_and_sign():
    values = request.get_json()
    required = ['image','govpri','user_pubkey','node']
    if not all(k in values for k in required):
        return 'Missing values', 400
    hash = authority.hashimage(values['image'])
    signature = authority.fsign(hash,values['govpri'],values['user_pubkey'],values['node'])
    return 'Signature done\n', 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port, threaded=True)
