import hashlib
import json
from time import time
from datetime import datetime
import time
from bitcoin.transaction import mktx, sign


class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []

    def new_block(self, proof, previous_hash=None):
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_now_hex = hex(int(time.mktime(time.strptime(date_now, '%Y-%m-%d %H:%M:%S'))) - time.timezone)
        block = {
            'version': hex(len(self.chain) + 1)[2:].zfill(8),
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'merkle': self.merkle_root(self.current_transactions),
            'timestamp': date_now_hex,
            'bits': '0x1745fb53',
            'nonce': proof,
            'transactions': self.current_transactions,
        }
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, input_count, previous_output, sender, receiver, amount):
        self.current_transactions.append({
            'input_count': input_count,
            'previous_output': previous_output,
            # 'script_sig': script_sig,
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
        })
        return self.current_transactions[-1]

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    @staticmethod
    def merkle_root(transactions):
        t_copy = transactions.copy()
        t_len = len(t_copy)
        if t_len==0:
            return hashlib.sha256(str('').encode()).hexdigest()
        if t_len%2 == 1 :
            t_copy.append(t_copy[-1])
            t_len+=1
        while True:
            t = []
            for i in range(0, t_len, 2):
                t.append(hashlib.sha256((str(t_copy[i])+str(t_copy[i+1])).encode()).hexdigest())
            t_copy = t
            t_len = t_len//2
            if t_len == 1:
                return t[0]

    def getChainLength(self):
        return len(self.chain)