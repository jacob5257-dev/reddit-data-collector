import requests  # used to make http requests to ollama

# runs an ollama prompt
def call_ollama_api(prompt, model="gemma3:1b"):
    """
    Makes a request to a local ollama server to run an AI query.
    :param prompt: String - the query for the AI.
    :param model: String - the model for ollama to run. Default is Gemma 3 1b.
    :return: A JSON object with response data from the API.
    """
    # url of the server
    url = "http://jacobs-ubuntu:11434/api/generate"

    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        # makes a request to the ollama server
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

# Usage
result = call_ollama_api(
    prompt="Why is the sky blue?"
)

if result:
    print(result["response"])