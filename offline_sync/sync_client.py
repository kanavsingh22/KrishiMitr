import requests
import json
import os
import time

class KioskSyncClient:
    def __init__(self, api_url, user_queue_file='offline_queue.json'):
        self.api_url = api_url
        self.user_queue_file = user_queue_file
        self.queue = self._load_queue()

    def _is_online(self):
        try:
            # Check connection to the local backend server
            requests.get("http://127.0.0.1:5000", timeout=3)
            return True
        except requests.ConnectionError:
            print("Kiosk is OFFLINE. Cannot connect to the main server.")
            return False

    def _load_queue(self):
        if os.path.exists(self.user_queue_file):
            try:
                with open(self.user_queue_file, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded {len(data)} messages from {self.user_queue_file} for processing.")
                    return data
            except json.JSONDecodeError:
                print(f"Error: Could not read {self.user_queue_file}. It might be empty or corrupted.")
                return []
        print("No user queue file found. Nothing to sync.")
        return []

    def sync_queued_messages(self):
        if not self._is_online():
            print("Sync check complete. Kiosk is offline.")
            return
        if not self.queue:
            print("Sync check complete. Queue is empty.")
            return

        print(f"Kiosk is ONLINE. Syncing {len(self.queue)} messages from the user.")
        
        failed_requests = []
        for i, request_data in enumerate(self.queue):
            try:
                print(f"  -> Sending ({i+1}/{len(self.queue)}): '{request_data['query']}'")
                response = requests.post(self.api_url, json={'query': request_data['query']})
                if response.status_code == 200:
                    print(f"     SUCCESS. Server replied.")
                else:
                    print(f"     FAILED. Server returned status {response.status_code}.")
                    failed_requests.append(request_data)
                time.sleep(0.5) 
            except requests.RequestException as e:
                print(f"     ERROR sending request: {e}")
                failed_requests.append(request_data)
        
        if failed_requests:
            print(f"\n{len(failed_requests)} messages failed to send. Saving them back to the queue.")
            with open(self.user_queue_file, 'w') as f:
                json.dump(failed_requests, f)
        else:
            print("\nAll messages synced successfully. Clearing the user queue file.")
            os.remove(self.user_queue_file)

if __name__ == '__main__':
    print("--- KrishiMitr Kiosk Sync Client v2.0 ---")
    kiosk_client = KioskSyncClient(
        api_url='http://127.0.0.1:5000/api/ask',
        user_queue_file='frontend/offline_queue.json' 
    )
    kiosk_client.sync_queued_messages()