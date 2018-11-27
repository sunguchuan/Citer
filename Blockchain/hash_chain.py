import sys, os
import _thread
import time

import requests
from flask import Flask, jsonify, request

import hashlib
import json

def get_hash(node):
    response = requests.get(f'http://{node}/chain')
    if response.status_code == 200:
        length = response.json()['length']
        chain = response.json()['chain']

        chain_string = json.dumps(chain, sort_keys=True).encode()
        return hashlib.sha256(chain_string).hexdigest()

if __name__ == '__main__':
    for i in range(int(sys.argv[1])):
        j=5000+i
        node=f'localhost:{j}'
        print(f'Hashed blockchain from {node}:',get_hash(node))
