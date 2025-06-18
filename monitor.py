!import requests
!import time
!import os

CHANGEDETECTION_URL = os.getenv('CHANGEDETECTION_URL', 'http://localhost:5000')
API_KEY = os.getenv('API_KEY', '')  # If authentication enabled

def create_watch(product_url):
    """Create a new watch in changedetection.io"""
    headers = {'Content-Type': 'application/json'}
    if API_KEY:
        headers['Authorization'] = f'Bearer {API_KEY}'
        
    payload = {
        'url': product_url,
        'track_restock': True,  # Enable built-in restock detection
        'notification_urls': ['json://localhost'],  # Local notifications
        'fetch_backend': 'system'  # Use Chrome browser if JS needed
    }
    
    try:
        response = requests.post(
            f'{CHANGEDETECTION_URL}/api/v1/watch',
            json=payload,
            headers=headers
        )
        return response.json().get('uuid')
    except Exception as e:
        print(f"Error creating watch: {e}")
        return None

def check_restock(watch_uuid):
    """Check if restock detected for given watch UUID"""
    try:
        response = requests.get(
            f'{CHANGEDETECTION_URL}/api/v1/watch/{watch_uuid}',
            headers={'Authorization': f'Bearer {API_KEY}'} if API_KEY else {}
        )
        data = response.json()
        return data.get('last_changed') is not None
    except Exception as e:
        print(f"Error checking restock status: {e}")
        return False

def monitor_product(config):
    """Main monitoring function using changedetection.io"""
    watch_uuid = create_watch(config['product_url'])
    
    if not watch_uuid:
        print("Failed to create watch")
        return

    while True:
        if check_restock(watch_uuid):
            send_notification(
                config['product_url'],
                config['recipient_email'],
                config['sender_email'],
                config['app_password']
            )
            break
            
        print(f"Next check in {config['check_interval']} seconds...")
        time.sleep(config['check_interval'])

if __name__ == "__main__":
    config = {
        'product_url': os.getenv('PRODUCT_URL', 'https://example.com/product'),
        'recipient_email': os.getenv('RECIPIENT_EMAIL', 'user@example.com'),
        'sender_email': os.getenv('SENDER_EMAIL', 'your.email@gmail.com'),
        'app_password': os.getenv('GMAIL_APP_PASSWORD', 'your-app-password'),
        'check_interval': int(os.getenv('CHECK_INTERVAL', 300))
    }
    
    monitor_product(config)