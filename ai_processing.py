import os
from time import sleep

import pandas as pd
import requests  # used to make http requests to ollama
from dotenv import load_dotenv  # gets secret stores
from google import genai  # google ai package
from google.ai.generativelanguage_v1 import GenerateContentResponse
from google.api_core import exceptions
from google.genai import Client
from requests import Response
from tqdm import tqdm  # used to show progress of AI

load_dotenv()


def call_ollama_api(prompt: str, model: str = "gemma3:12b") -> dict[str, str] | None:
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
        response: Response = requests.post(url, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


def call_google_api(prompt: str, model: str = "gemma3", api_key: str = os.getenv("GOOGLE_API_KEY")) -> dict[str, str] | None:
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


# open file with comments
posts: pd.DataFrame = pd.read_csv("posts.csv")
# get the number of comments
num_comments: int = int(posts.columns[-1][7:])

column_names: list[str] = [f"Comment{i}"
                for i in range(1, num_comments + 1)] + ["Content"]

# get all quotes into a list
quotes: list[str] = posts[column_names].values.flatten().tolist()[:20]
# remove any empty values or comments that were deleted
quotes = [x for x in quotes if (type(x) is str and x != '[deleted]')]

results: list[str] = []
for quote in tqdm(quotes, desc="AI Progress"):
    # call the ollama api to determine role
    result: dict[str, str] | None = call_ollama_api(
        prompt="Read the following message about the PowerSchool data breach and determine the role of the person who wrote it. "
               "The author has one of the following roles: parent, student, teacher, admin, general. "
               "Walk me through how you determined their role. "
               "Provide an explanation for why you chose the role for that message. "
               "If you are not more than 50% confident in your classification, respond with unsure. "
               "Parents generally talk about their children, using words such as 'my son', 'my daughter', 'my child(ren)', etc. "
               "They also mention receiving messages from school boards about the data breach. "
               "Students have generally graduated since we can't collect data from people under 18. "
               "They usually mention that they graduated some years ago. "
               "Teachers usually mention that they have experience teaching. "
               "Administrators usually have more technical knowledge, but that is not a guaranteed factor. "
               "They talk with PowerSchool directly and manage a school's or district's powerschool instance. "
               "Message: "
               f"{quote}"
    )

    if result:
        # add the result so we can track it
        results.append(result["response"])

# put the quote to the role and save as csv
out: pd.DataFrame = pd.DataFrame({
    "quote": quotes,
    "role": results
})

out.to_csv("roles.csv")
