import pandas as pd
import requests  # used to make http requests to ollama


def call_ollama_api(prompt, model="gemma3"):
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


# open file with comments
posts = pd.read_csv("posts.csv")
# get the number of comments
num_comments = int(posts.columns[-1][7:])

column_names = [f"Comment{i}" for i in range(1, num_comments + 1)] + ["Content"]

# get all quotes into a list
quotes = posts[column_names].values.flatten().tolist()
# remove any empty values or comments that were deleted
quotes = [x for x in quotes if (type(x) == str and x != '[removed]')]

results = []
for quote in quotes:

    # call the ollama api to determine role
    result = call_ollama_api(
        prompt="The following is a quote regarding the PowerSchool data breach. "
               "Determine whether the person who posted it was a parent, former student, teacher, or district administrator. "
               "Answer with one word, either parent, student, teacher, admin, or none. Quote: "
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
