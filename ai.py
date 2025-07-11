from time import sleep

import requests  # used to make http requests to ollama
from google import genai  # google ai package
from google.ai.generativelanguage_v1 import GenerateContentResponse
from google.api_core import exceptions
from google.genai import Client
from openai import OpenAI

def ollama_ai(prompt: str, model: str = "gemma3:12b") -> str | None:
    """
    Makes a request to a local ollama server to run an AI query.
    :param prompt: String - the query for the AI.
    :param model: String - the model for ollama to run. Default is Gemma 3 1b.
    :return: A JSON object with response data from the API.
    """
    # url of the server
    url: str = "http://jacobs-ubuntu:11434/api/generate"

    data: dict[str, str | bool] = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        # makes a request to the ollama server
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


def google_ai(prompt: str, api_key: str, model: str = "gemma3") -> str | None:
    """
    Calls the Google/Gemini api to get their AI's answers
    :param prompt: The prompt to ask the AI
    :param model: Which AI model to ask - default is gemma 3
    :param api_key: Google api key
    :return: String response of the AI
    """
    # get google gen ai client object
    client: Client = genai.Client(api_key=api_key)

    try:
        # get response from api and return it
        response: GenerateContentResponse = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text
    except exceptions.ResourceExhausted as e:
        print(f"{e}\nAPI limit reached. Taking a break for a few seconds...")
        sleep(15)
        return None


def openai_ai(prompt: str, api_key: str, model: str = "o4-mini", instructions: str = "") -> str | None:
    """
    Calls the OpenAI api to get their AI's response.
    :param prompt: The prompt to ask the AI.
    :param model: The model to use. Defaults to o4-mini
    :param api_key: The OpenAI API key. Default to the value set in .env
    :param instructions: The instructions that the model will receive.
    :return: String response from the AI.
    """
    try:
        client: OpenAI = OpenAI(
            api_key=api_key
        )

        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=prompt
        )

        return response.output_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None