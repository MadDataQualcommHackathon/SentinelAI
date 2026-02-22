import requests

API_KEY = "6SNXMKS-TFW4X9G-PC1AJEE-40K0JZS"
WORKSPACE_SLUG = "sentinel"
BASE_URL = "http://localhost:3001"


def call_llm(message: str) -> str:
    """
    Send a message to AnythingLLM and return the text response.

    Args:
        message: The full prompt/message string to send.

    Returns:
        The LLM's textResponse as a string.
    """
    url = f"{BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"message": message, "mode": "query"}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json().get("textResponse", "")


if __name__ == "__main__":
    import time

    TEST_MESSAGE = "Hey Llama, are you ready for the hackathon?"
    url = f"{BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"message": TEST_MESSAGE, "mode": "query"}

    print(f"Sending request to {url}")
    print(f"Workspace: {WORKSPACE_SLUG}")
    print(f"Message: {TEST_MESSAGE}\n")

    start = time.time()
    response = requests.post(url, headers=headers, json=payload)
    elapsed = time.time() - start

    print(f"Status code:   {response.status_code}")
    print(f"Response time: {elapsed:.2f}s")
    print(f"\n--- Full response JSON ---")
    print(response.json())
    print(f"\n--- textResponse ---")
    print(response.json().get("textResponse", "(empty)"))