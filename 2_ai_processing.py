import os
import random

import pandas as pd
from dotenv import load_dotenv  # gets secret stores
from tqdm import tqdm  # used to show progress of AI

from ai import openai_ai

load_dotenv()

# open file with comments
posts: pd.DataFrame = pd.read_csv("posts.csv")
# get the number of comments
num_comments: int = int(posts.columns[-1][7:])

column_names: list[str] = [f"Comment{i}"
                           for i in range(1, num_comments + 1)] + ["Content"]

# get all quotes into a list
quotes: list[str] = posts[column_names].values.flatten().tolist()
# remove any empty values or comments that were deleted
quotes = [x for x in quotes if (type(x) is str and x != '[deleted]')]

results: list[str] = []
for quote in tqdm(quotes, desc="AI Progress"):
    # call the openai api to determine role
    result: str | None = openai_ai(
        prompt="Read the following message about the PowerSchool data breach and determine the role of the person who wrote it. "
               "The author has one of the following roles: parent, student, teacher, admin. "
               "The first word of your response should be the role of the person. "
               "Provide an explanation for why you chose the role for that message. "
               "If you are not more than 50% confident in your classification, respond with unsure. "
               "Parents generally talk about their children, using words such as 'my son', 'my daughter', 'my child(ren)', etc. "
               "They also mention receiving messages from school boards about the data breach. "
               "Students have generally graduated since we can't collect data from people under 18. "
               "They usually mention that they graduated some years ago. "
               "Teachers usually mention that they have experience teaching. "
               "Administrators usually have more technical knowledge, but that is not a guaranteed factor. "
               "They talk with PowerSchool directly and manage a school's or district's powerschool instance. "
               "Note that administrators must be from a K-12 school, so postsecondary admins, admins that worked on tech other than PowerSchool, and PowerSchool employees should be classified as general. "
               "Additionally, simply knowing technical terms does not automatically make them an administrator. "
               "They need to have experience working in a K-12 school's IT department. "
               "If the person does not fit any of the labels, respond with the best fit label that you can think of. "
               "If the message does not relate to the PowerSchool data breach, respond with not relevant. "
               "Message: "
               f"{quote}",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    if result:
        # add the result so we can track it
        results.append(result)

# put the quote to the role and save as csv
out: pd.DataFrame = pd.DataFrame({
    "quote": quotes,
    "role": results
})

out.to_csv("roles.csv", index=False)
