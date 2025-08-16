import requests
import json
import os
import time

class OfflineSyncClient:
    def __init__(self, api_url, queue_file='offline_queue.json'):
        self.api_url = api_url
        self.queue_file = queue_file
        self.queue = self._load_queue()

    def _is_online(self):
        """Checks for an active internet connection."""
        try:
            requests.get("http://www.google.com", timeout=3)
            return True
        except requests.ConnectionError:
            return False

    def _load_queue(self):
        """Loads pending requests from the queue file."""
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        return []

    def _save_queue(self):
        """Saves the current queue to a file."""
        with open(self.queue_file, 'w') as f:
            json.dump(self.queue, f)

    def send_query(self, query):
        """
        Sends a query. If online, sends directly. If offline,
        queues it for later.
        """
        if self._is_online():
            print("Client is online. Sending query directly.")
            try:
                response = requests.post(self.api_url, json={'query': query})
                print(f"Server Response: {response.json()}")
            except requests.RequestException as e:
                print(f"Failed to send request even when online: {e}")
                self._queue_request(query)
        else:
            print("Client is offline. Queuing request.")
            self._queue_request(query)
    
    def _queue_request(self, query):
        """Adds a request to the local queue."""
        self.queue.append({'query': query, 'timestamp': time.time()})
        self._save_queue()

    def sync_pending_requests(self):
        """
        If online, sends all pending requests from the queue to the server.
        """
        if self._is_online() and self.queue:
            print(f"Online. Found {len(self.queue)} pending requests. Syncing...")
            
            remaining_queue = []
            for request_data in self.queue:
                try:
                    response = requests.post(self.api_url, json={'query': request_data['query']})
                    if response.status_code == 200:
                        print(f"Successfully synced query: {request_data['query']}")
                    else:
                        print(f"Failed to sync query: {request_data['query']}. Server returned {response.status_code}")
                        remaining_queue.append(request_data) # Keep in queue
                except requests.RequestException as e:
                    print(f"Sync failed due to connection error: {e}")
                    remaining_queue.append(request_data) # Keep in queue
                    break # Stop trying if connection fails
            
            self.queue = remaining_queue
            self._save_queue()
        elif not self.queue:
            print("No pending requests to sync.")
        else:
            print("Still offline. Cannot sync.")


if __name__ == '__main__':
    # This is a simulation of the client's behavior
    client = OfflineSyncClient(api_url='http://127.0.0.1:5000/api/ask')

    # Simulate sending a query (run this while your internet is ON/OFF)
    client.send_query("What is the price of onions in Delhi?")

    # In a real app, this sync process would run periodically in the background
    print("\nAttempting to sync pending requests...")
    client.sync_pending_requests()