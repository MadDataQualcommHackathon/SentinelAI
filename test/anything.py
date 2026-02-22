import requests

API_KEY = "6SNXMKS-TFW4X9G-PC1AJEE-40K0JZS"
WORKSPACE_SLUG = "sentinel"  
BASE_URL = "http://localhost:3001"     

url = f"{BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "message": "Hey Llama, are you ready for the hackathon?",
    "mode": "chat"
}

try:
    print("Sending request to AnythingLLM...")
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status() 
    
    result = response.json()
    print("\n--- AI Response ---")
    print(result.get("textResponse", "No text response found."))
    print("-------------------")
    
except requests.exceptions.RequestException as e:
    print(f"Connection Error: {e}")
    if response is not None:
         print(f"Details: {response.text}")