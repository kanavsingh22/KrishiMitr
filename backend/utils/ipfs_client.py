import json
import hashlib

class IPFSSimulator:
    """
    A simulator for IPFS. In a real application, this would use the
    'ipfshttpclient' library to connect to a real IPFS daemon.
    """
    def __init__(self):
        self.storage = {}
        print("Initialized IPFS Simulator.")

    def add_json(self, data_object):
        """
        Simulates adding a JSON object to IPFS.
        It returns a hash of the content, similar to how IPFS returns a CID.
        """
        # Serialize the dictionary to a consistent string format
        serialized_data = json.dumps(data_object, sort_keys=True).encode('utf-8')
        # Create a SHA256 hash as a stand-in for the IPFS CID
        cid = hashlib.sha256(serialized_data).hexdigest()
        
        # Store the data against the 'cid'
        self.storage[cid] = serialized_data
        print(f"Stored data in IPFS simulator with CID: {cid}")
        return cid

    def get_json(self, cid):
        """Retrieves a JSON object from the simulated storage."""
        data = self.storage.get(cid)
        if data:
            return json.loads(data.decode('utf-8'))
        return None

# Singleton instance
ipfs_client = IPFSSimulator()