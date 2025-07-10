import hashlib
import time
import json

class Block:
    def __init__(self, data, previous_hash='0'):
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def __repr__(self):
        return f"Block(hash={self.hash[:10]}..., data={self.data})"
