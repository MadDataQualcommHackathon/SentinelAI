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
    payload = {"message": message, "mode": "chat"}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json().get("textResponse", "")


if __name__ == "__main__":
    # Quick test when run directly
    result = call_llm("Hey Llama, are you ready for the hackathon?")
    print("\n--- AI Response ---")
    print(result)
    print("-------------------")