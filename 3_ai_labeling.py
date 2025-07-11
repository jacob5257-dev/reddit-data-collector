import os

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from ai import openai_ai

load_dotenv()

# initially label messages
posts: pd.DataFrame = pd.read_csv("roles.csv")

# get all quotes into a list
quotes: list[str] = posts["quote"].values.flatten().tolist()
responses: list[str] = []

for quote in tqdm(quotes, desc="AI Progress"):
    # ai_response: str | None = openai_ai(
    #    prompt="Below is a quote about the PowerSchool data breach. "
    #           "Label the data based on what was included. "
    #           "For example, if the author of the message complained about the delay in notification, you can label the message as 'lack of communication'. "
    #           "Additionally, if the author of the message worried about their children's data, you can label the message as 'worried about child data'. "
    #           "You can label messages with as many labels as necessary and you may generate as many labels as you need. "
    #           f"Message: {quote}",
    #    api_key=os.getenv("OPENAI_API_KEY")
    # )

    ai_response: str | None = openai_ai(
        prompt="Below is a quote about the PowerSchool data breach. "
               "Label the data based on what was included. Respond with a list of labels that fit the message. "
               "You can select as many labels as necessary, but you may not add labels that are not on this list: "
               "Lack of communication - This label means the author was not notified about the breach before they posted. "
               "Bad communication - This label means the author was notified about the breach before they posted, but they were still unsure about some aspect of the breach. "
               "Worried about data - This label means the author was worried about the impact of this data breach. For example, posters could be worried about identity theft or fraud. "
               "Not worried about data - This label means the author was not concerned about the data breach. For example, posters may assume that their data is already on the dark web, so this breach didn't affect them. "
               "Issues with remediation - This label means the author had problems when trying to protect themselves. For example, they may have encountered issues when signing up for credit monitoring. "
               "Feeling of inevitability - This label means the author felt that they had no other choice but to give data to insecure companies. "
               "Insufficient remedies - This label means the author felt that actions taken after the breach were not enough to fully protect themselves. "
               "Confused - This label means that the author did not know what to do after the data breach to protect themselves. "
               "Surprised - This label means that the author was surprised that PowerSchool was breached. "
               "Lost trust - This label means that the author no longer trusts companies with their data after the breach. "
               "Lack of funding - This label means that the author believes that schools do not have enough money to afford better systems. "
               "Outdated technology - This label means that the author believes that schools' technologies are so old they cause security vulnerabilities. "
               "High stress - This label means that the author believes that administrators and IT professionals do not have the ability to protect their systems due to high workloads. "
               "Lack of accountability - This label means that the author feels like PowerSchool was not adequately punished for the data breach. "
               f"Message: {quote}",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    responses.append(ai_response)

posts["labels"] = responses
posts.to_csv("labels.csv", index=False)
