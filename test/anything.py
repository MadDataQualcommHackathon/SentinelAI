import requests

# 1. Define your configuration
API_KEY = "6SNXMKS-TFW4X9G-PC1AJEE-40K0JZS"
WORKSPACE_SLUG = "sentinel"  # e.g., "my-hackathon-workspace"
BASE_URL = "http://localhost:3001"      # 3001 is the default AnythingLLM Desktop port

# 2. Set up the endpoint and headers
url = f"{BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# 3. Construct your payload
payload = {
    "message": "Hey Llama, are you ready for the hackathon?",
    "mode": "chat" # Use "chat" for conversation, or "query" to force RAG/document search
}

# 4. Make the call!
try:
    print("Sending request to AnythingLLM...")
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status() # Check for HTTP errors
    
    # Extract the AI's response
    result = response.json()
    print("\n--- AI Response ---")
    print(result.get("textResponse", "No text response found."))
    print("-------------------")
    
except requests.exceptions.RequestException as e:
    print(f"Connection Error: {e}")
    if response is not None:
         print(f"Details: {response.text}")