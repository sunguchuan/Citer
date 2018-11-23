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

import asyncio
from kademlia.network import Server

from random import random

import _thread

class Blockchain:
    def __init__(self):
        self.current_data=[]    # Used to store the current ID information
        self.chain = [
        {   "data":[],
            "index": 1,
            "previous_hash": "1",
            "proof": 100}
        ]
        # Create the genesis block
        self.nodes = set()
        self.mining=False
        self.govData=self.getFileData('govpub.pem')
        self.govPubkey=serialization.load_pem_public_key(
            self.govData,
            backend=default_backend()
        )

    def register_node(self, address):   #Original
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
            return parsed_url.netloc

        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
            return parsed_url.path

        else:
            # raise ValueError('Invalid URL')
            print('Invalid URL')
            return False

    def return_node(self,node):
        requests.post(f'http://{node}/nodes/register_return',json={'node':request.host})

    def register_node2(self,address):
        """
        Add a new node to the list of nodes through Kademlia
        param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        # parsed_url = urlparse(address)
        # if parsed_url.netloc:
        #     self.nodes.add(parsed_url.netloc)
        # elif parsed_url.path:
        #     # Accepts an URL without scheme like '192.168.0.5:5000'.
        #     self.nodes.add(parsed_url.path)
        # else:
        #    raise ValueError('Invalid URL')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(node.bootstrap([(address[0], address[1])]))

    def getneighbours(self):
        return node.bootstrappableNeighbors()

    def valid_chain(self, chain):       #Original
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # print(f'{last_block}')
            # print(f'{block}')
            # print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                print('invalid chain')
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], block['previous_hash'],self.hash(block['data'])):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):        #Original
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            # res=requests.post(f'http://{node}/nodes/register',json={'nodes':["http://localhost:5000/"]})
            # print(res.json())
            # requests.get(f'http://{node}/mine')
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, previous_hash, data):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': data,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        return block

    def check_block(self,block,chain):
        # self.checking=True
        if block['previous_hash'] == self.hash(chain[-1]) and self.valid_proof(chain[-1]['proof'], block['proof'], block['previous_hash'], self.hash(block['data'])): #
            # self.checking=False
            if len(chain)>=len(self.chain):
                self.mining=False
                for entry in block['data']:
                    if entry in self.current_data:
                        self.current_data.remove(entry)
                        # print('Data removed')
                self.resolve_conflicts()
            print('block is valid')
            return True
        else:
            # self.checking=False
            print('block is invalid')
            return False

    def new_data(self, pubkey, info, govSig):
        sig = self.govVerify(govSig,info)
        if sig is True:
            self.resolve_conflicts()

            for node in self.nodes: # Broadcast the information
                res=requests.post(f'http://{node}/data/check',json={'pubkey':pubkey,'info':info,'govsig':govSig})   # Route /transaction/send
                if res.status_code != 201:
                    return -1

            if pubkey not in self.current_data:
                self.current_data.append({
                    'public key': pubkey,
                    'info': info,
                    'signature':govSig,
                    # 'white list': [],
                })
                # print(len(self.current_data))
                # if len(self.current_data)>=2 and self.mining is False:
                _thread.start_new_thread( self.mine, ( ) )
                    #self.mine()
                return self.last_block['index']+1
            else:
                return 0
        else:
            return -1

    def check_data(self, pubkey, info, govSig):
        sig=self.govVerify(govSig,info)
        if sig is True:
            print('data is correct')

            for entry in self.current_data:
                if pubkey == entry['public key'] :
                    return 0
            if pubkey not in self.current_data:
                self.current_data.append({
                    'public key': pubkey,
                    'info': info,
                    'signature':govSig,
                    # 'white list': [],
                })
            # print(len(self.current_data))
            # if len(self.current_data)>=2 and self.mining is False:
            self.mine()
            return self.last_block['index']+1
        else:
            print('data is incorrect')
            return -1

    def mine(self):
        # print('start mining')
        if self.mining is False:
            while len(self.current_data)>=1:
                self.mining = True
                last_block = self.last_block
                data = self.current_data[:1]
                proof = self.proof_of_work(last_block,data) #
                if proof!=0:
                    # Forge the new Block by adding it to the chain
                    previous_hash = self.hash(last_block)
                    block = self.new_block(proof, previous_hash, data)

                    if block['previous_hash'] == self.hash(self.chain[-1]) and self.valid_proof(self.chain[-1]['proof'], block['proof'], block['previous_hash'],self.hash(block['data'])):
                        self.chain.append(block)
                        #Broadcast the block
                        for node in self.nodes:
                            requests.post(f'http://{node}/block/check',json={'Chain':self.chain})
                        for entry in data:
                            try:
                                self.current_data.remove(entry)
                            except:
                                print('Data already removed')
                        print(block)
                    else:
                        # print(block)
                        print('A mined block is discarded')
                else:
                    print('Mining stopped because a new block has been created')
                self.mining= False
        # print('mining complete')
        # else:
        #     print('Mining is already running')

    def govVerify(self,sigData,infoData):
        indata =infoData.encode()
        signature =base64.b64decode(sigData.encode())
        try:
            self.govPubkey.verify(signature,indata,padding.PKCS1v15(), hashes.SHA256())
        except InvalidSignature:
            print('invalid signature!')
            return False
        else:
            return True

    # def verify(self,pubkey,sig,data):  # padding=PKCS1v15, hash=sha256
    #     indata=self.getFileData(data)
    #     signature=self.getFileData(sig)
    #     keydata=self.getFileData(pubkey)
    #
    #     pub=serialization.load_pem_public_key(
    #         keydata,
    #         backend=default_backend()
    #     )
    #
    #     res=False;
    #     try:
    #         pub.verify(signature,indata,padding.PKCS1v15(), hashes.SHA256())
    #     except InvalidSignature:
    #         print('invalid signature!')
    #     else:
    #         res=True
    #     return res

    # def authorization(self,index,target,pubkey):
        # targetfs=open(target)
        # targetData=targetfs.read()
        # targetfs.close()
        #
        # pubkeyfs=open(pubkey)
        # pubkeyData=pubkeyfs.read()
        # pubkeyfs.close()
        #
        # for entry in self.chain[index-1]['data']:
        #     if entry['public key']==targetData:
        #         if pubkeyData not in entry['white list']:
        #             for current_entry in self.current_data:
        #                 if current_entry['public key'] == pubkeyData:
        #                     if pubkeyData not in current_entry['white list']:
        #                         current_entry['white list'].append(pubkeyData)
        #                         return self.last_block['index']+1
        #                     else:
        #                         return 0
        #             new_entry = copy.deepcopy(entry)     #public key not in currentd data
        #             new_entry['white list'].append(pubkeyData)
        #             self.current_data.append(new_entry)
        #             return self.last_block['index']+1
        #         else:
        #             return 0
        # return -1

    # def retrieve(self, index, target, pubkey, resfile):
    #     targetfs=open(target)
    #     targetData=targetfs.read()
    #     targetfs.close()
    #
    #     for entry in self.chain[index-1]['data']:
    #         if entry['public key']==targetData:
    #             pubkeyfs=open(pubkey)
    #             pubkeyData=pubkeyfs.read()
    #             pubkeyfs.close()
    #
    #             if pubkeyData in entry['white list']:
    #                 pubkeyfs=open(pubkey,'rb')
    #                 bytes=pubkeyfs.read()
    #                 pubkeyfs.close()
    #                 pub=serialization.load_pem_public_key(
    #                     bytes,
    #                     backend=default_backend()
    #                 )
    #                 res=pub.encrypt(
    #                 (entry['info'].encode()),
    #                 padding.PKCS1v15()
    #                 )
    #                 resfs=open(resfile,'wb')
    #                 resfs.write(res)
    #                 resfs.close()
    #
    #                 return 1
    #             else:
    #                 print ('Access denied')
    #                 return -1
    #     print ('Target not found')
    #     return -1

    # def check_image(self,index,pubkey,datafile):
    #     # self.resolve_conflicts()
    #
    #     pubkeyfs=open(pubkey)
    #     pubkeyData=pubkeyfs.read()
    #     pubkeyfs.close()
    #
    #     imagefs=open(datafile)
    #     imageData=imagefs.read()
    #     imagefs.close()
    #
    #     for entry in self.chain[index-1]['data']:
    #         if entry['public key']==pubkeyData and entry['info']==imageData:
    #             return True
    #     return False

    @property
    def last_block(self):       #Original
        return self.chain[-1]

    @staticmethod
    def hash(block):            #Original
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # @staticmethod
    # def hash_transaction(transaction):
    #     transaction_string = json.dumps(transaction, sort_keys=True).encode()
    #     hash=hashlib.sha256(transaction_string).hexdigest()
    #     return hash

    def proof_of_work(self, last_block, data):        #Original
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        transaction_hash=self.hash(data)

        proof = 0

        while self.mining is True:
            if self.valid_proof(last_proof, proof, last_hash, transaction_hash) is False: #
                proof = random()
            else:
                return proof
        proof=0
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash, transaction_hash):      #Original
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}{last_hash}{transaction_hash}'.encode() #
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"

    def encrypt(self,pubkey, data):
        content=data.encode('utf-8')
        crypto=rsa.encrypt(content,pubkey)
        return crypto

    # def decrypt(prikey,data):
    #     content=rsa.decrypt(data,prikey)
    #     con=content.decode('utf-8')
    #     return con

    def getFileData(self,filename):
        input=open(filename,'rb')
        res=input.read()
        input.close()
        return res

# Instantiate the Node
app = Flask(__name__)           #Original

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')         #Original

# Instantiate the Blockchain
blockchain = Blockchain()           #Original


@app.route('/mine', methods=['GET'])
def mine():
    # # We run the proof of work algorithm to get the next proof...
    # last_block = blockchain.last_block
    # proof = blockchain.proof_of_work(last_block)
    #
    # # We must receive a reward for finding the proof.
    # # The sender is "0" to signify that this node has mined a new coin.
    # '''
    # blockchain.new_transaction(
    #     sender="0",
    #     recipient=node_identifier,
    #     amount=1,
    # )
    # '''
    # # Forge the new Block by adding it to the chain
    #
    # # blockchain.resolve_conflicts()
    # previous_hash = blockchain.hash(last_block)
    # block = blockchain.new_block(proof, previous_hash)
    block=blockchain.mine()

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/block/check',methods=['POST'])     #resolve after checking, check duplication
def check_block():
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['Chain']
    if not all(k in values for k in required):
        return 'Missing values', 400
    _thread.start_new_thread(blockchain.check_block,(values['Chain'][-1],values['Chain'][:-1],))
    return 'Block received',200

@app.route('/data/new', methods=['POST'])
def new_data():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['pubkey', 'info','govsig']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_data(values['pubkey'], values['info'],values['govsig'])
    if index == -1:
        return 'Permission denied', 400
    elif index == 0:
        return 'Public key already exists in current data', 400
    else:
        response = {'message': f'New data will be added to Block {index}'}
        return jsonify(response), 201

@app.route('/data/check', methods=['POST'])
def check_data():
    values = request.get_json()
    #response
    # Check that the required fields are in the POST'ed data
    required = ['pubkey', 'info','govsig']
    if not all(k in values for k in required):
        return 'Missing values', 400
    _thread.start_new_thread( blockchain.check_data, (values['pubkey'], values['info'],values['govsig'],) )

    return 'Message received', 201

# @app.route('/data/authorize',methods=['POST'])
# def author():
#     values=request.get_json()
#     required=['index','target','signature','data','pubkey']
#     if not all(k in values for k in required):
#         return 'Missing values', 400
#
#     if blockchain.verify(values['target'],values['signature'],values['data']) is False:
#         return 'Signature verification fail\n', 400
#     res = blockchain.authorization(values['index'],values['target'],values['pubkey'])
#     if res==-1:
#         return 'Target not found\n', 400
#     elif res==0:
#         return 'pubkey already authorized\n', 400
#     else:
#         response={'message':f'Authorization succeed. New data will be added to Block {res}'}
#         return jsonify(response),201

# @app.route('/data/retrieve',methods=['POST'])
# def retrieve():
#     values=request.get_json()
#     required=['index','target','pubkey','resfile']
#     if not all(k in values for k in required):
#         return 'Missing values', 400
#
#     res=blockchain.retrieve(values['index'],values['target'],values['pubkey'],values['resfile'])
#     if res == -1:
#         return 'No data found or access denied\n', 400
#     else:
#         response={'message':f'Retrieve succeed'}
#         return jsonify(response), 200

@app.route('/chain', methods=['GET'])       #Original
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])     #Original
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        url=blockchain.register_node(node)
        if url is not False:
            blockchain.return_node(url)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/register_return', methods=['POST'])     #Original
def register_return():
    values = request.get_json()
    node=values.get('node')
    if node is None:
        return "Error: Please supply a valid node", 400

    blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])       #Original
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':      #Original
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # node = Server()
    # node.listen(port)
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(node.bootstrap([("0.0.0.0", port)]))

    app.run(host='0.0.0.0', port=port, threaded=True)
    # print('Run the node')


    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(node.bootstrap([("0.0.0.0", port)]))
