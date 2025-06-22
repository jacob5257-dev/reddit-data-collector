import os
from time import sleep

import pandas as pd
import requests  # used to make http requests to ollama
from tqdm import tqdm  # used to show progress of ai
from google import genai  # google ai package
from google.api_core import exceptions
from dotenv import load_dotenv  # gets secret stores

load_dotenv()


def call_ollama_api(prompt, model="gemma3:4b-it-qat"):
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
    except exceptions.ResourceExhausted as e:
        print(f"API limit reached. Taking a break for a few seconds...")
        sleep(15)
        return None


def call_google_api(prompt, model="gemma3", api_key=os.getenv("GOOGLE_API_KEY")):
    """
    Calls the google/gemini api to get their ai's answers
    :param prompt: The prompt to ask the ai
    :param model: Which ai model to ask - default is gemma 3
    :param api_key: Google api key
    :return: String response of the ai
    """
    # get google gen ai client object
    client = genai.Client(api_key=api_key)

    try:
        # get response from api and return it
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text
    except exceptions.ResourceExhausted as e:
        print(f"API limit reached. Taking a break for a few seconds...")
        sleep(15)
        return None


# open file with comments
posts = pd.read_csv("posts.csv")
# get the number of comments
num_comments = int(posts.columns[-1][7:])

column_names = [f"Comment{i}"
                for i in range(1, num_comments + 1)] + ["Content"]

# get all quotes into a list
quotes = posts[column_names].values.flatten().tolist()
# remove any empty values or comments that were deleted
quotes = [x for x in quotes if (type(x) is str and x != '[removed]')]

results = []
for quote in tqdm(quotes, desc="AI Progress"):
    # call the ollama api to determine role
    result = call_ollama_api(
        prompt="Read the following message about the PowerSchool data breach and determine the role of the person who wrote it. "
               "Respond with only one word from the following list: parent, student, teacher, admin, general, or unsure. "
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
out = pd.DataFrame({
    "quote": quotes,
    "role": results
})

out.to_csv("roles.csv")
