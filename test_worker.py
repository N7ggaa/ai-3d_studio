import requests
import sys

try:
    r = requests.get('http://127.0.0.1:5000/health', timeout=5)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text}')
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)

