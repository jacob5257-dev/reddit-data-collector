import sys

import praw # imports praw for reddit access
import pandas as pd # imports pandas for data manipulation
from datetime import datetime as dt # imports datetime to deal with dates
from dotenv import load_dotenv # get login secrets
import os, sys

load_dotenv() # gets secrets

# log into reddit api
reddit = praw.Reddit(client_id=os.getenv("CLIENT_ID"),
                     client_secret=os.getenv("CLIENT_SECRET"),
                     user_agent='reddit data collector for u/Delicious-Corner6100',
                     username=os.getenv("REDDIT_USERNAME"),
                     password=os.getenv("REDDIT_PASSWORD"))

# make sure that we are logged in correctly
if reddit.user.me() != os.getenv("REDDIT_USERNAME"):
    print("Failed to log in to Reddit :(")
    sys.exit(1)
print(f"Logged in to Reddit as {os.getenv("REDDIT_USERNAME")}")

# create a DataFrame to store posts
# posted date in epoch, comments as list, everything else is a string
posts = pd.DataFrame(columns=["Posted Time", "Title", "Author", "Link", "Comments"])

# list subreddits to search
subreddits = ['cybersecurity']#, 'technology', 'k12sysadmin', 'toronto', 'canada', 'askTO', 'raleigh', 'linustechtips']

# look through every subreddit
for subreddit_name in subreddits:
    # get the subreddit via api
    subreddit = reddit.subreddit(subreddit_name)
    # get the messages that meet a query (the same as the search bar)
    # sorts by recency and gets only messages from the most recent year (will narrow down further later)
    for submission in subreddit.search("powerschool", sort="new", time_filter="year"):
        # check the time of the post
        # 12/28/2024, the date of the breach, in epoch time
        breach_time = 1735344000
        if submission.created_utc <= breach_time:
            # do not process comments if they occur after the breach
            continue
        time = dt.fromtimestamp(submission.created_utc)

        # manipulates some properties to make them more useful
        link = f"https://www.reddit.com/r/{subreddit}/comments/{submission.id}/"
        comments = submission.comments.list()
        comment_text = []
        for comment in comments:
            comment_text.append(comment.body)

        # collects the data necessary
        data = [time, submission.title, submission.author.name, link, comments]
        # adds the data to the dataframe
        posts.loc[len(posts)] = data

# exports data to csv
posts.to_csv("posts.csv")