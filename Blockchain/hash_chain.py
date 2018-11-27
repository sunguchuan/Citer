import sys, os
import _thread
import time
import subprocess

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
# time.sleep(5)
# os.system('''Curl -X POST -H "Content-Type:application/json" -d '{"nodes":["http://localhost:5001/"]}' "http://localhost:5000/nodes/register"''')
#
# os.system('''Curl -X POST -H "Content-Type:application/json" -d '{"nodes":["http://localhost:5001/"]}' "http://localhost:5002/nodes/register"''')
#
# os.system('''Curl -X POST -H "Content-Type:application/json" -d '{"nodes":["http://localhost:5002/"]}' "http://localhost:5000/nodes/register"''')
#
# os.system('''curl -X POST -H "Content-Type:application/json" -d '{"pubkey":"/Users/user/Desktop/sgc/Project/Data/code/test/public.pub", "info":"/Users/user/Desktop/sgc/Project/Data/code/test/info.txt", "govsig": "/Users/user/Desktop/sgc/Project/Data/code/test/fromgov.bin"}' "http://localhost:5000/data/new"''')

#,stdin=subprocess.PIPE, stderr=subprocess.PIPE,stdout=subprocess.PIPE
