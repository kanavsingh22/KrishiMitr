import hashlib
import time
import json

class BlockchainSimulator:
    """
    A simulator for a permissioned blockchain like Hyperledger Fabric.
    This mimics the behavior of submitting a transaction to a chaincode.
    """
    def __init__(self):
        self.chain = []
        # Create a genesis block
        self.create_block(proof=1, previous_hash='0', data_hash="genesis_hash")
        print("Initialized Blockchain Simulator.")

    def create_block(self, proof, previous_hash, data_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'proof': proof,
            'previous_hash': previous_hash,
            'data_hash': data_hash
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def submit_transaction(self, asset_id, data_hash, owner):
        """
        Simulates submitting a transaction to the 'CreateAsset' chaincode function.
        In a real scenario, this would involve using the Fabric SDK.
        """
        # Simple proof-of-work simulation
        previous_block = self.get_previous_block()
        previous_hash = self.hash(previous_block)
        
        # In a real system, this transaction would be signed and sent to peers.
        # Here, we just add it to our simulated chain.
        new_block = self.create_block(proof=asset_id, previous_hash=previous_hash, data_hash=data_hash)
        
        # The transaction ID is the hash of the block containing the data
        tx_id = self.hash(new_block)
        print(f"Transaction successful. Hash anchored on-chain. TxID: {tx_id}")
        return tx_id

    def query_transaction(self, data_hash):
        """
        Simulates querying the blockchain to verify if a hash exists.
        """
        for block in self.chain:
            if block['data_hash'] == data_hash:
                return True
        return False

# Singleton instance
blockchain_client = BlockchainSimulator()