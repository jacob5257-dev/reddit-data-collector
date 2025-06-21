from datetime import datetime as dt  # imports datetime to deal with dates
import os
import sys
import praw  # imports praw for reddit access
import pandas as pd  # imports pandas for data manipulation
from dotenv import load_dotenv  # get login secrets

load_dotenv()  # gets secrets

# log into reddit api
reddit = praw.Reddit(client_id=os.getenv("CLIENT_ID"),
                     client_secret=os.getenv("CLIENT_SECRET"),
                     user_agent='data collector for u/Delicious-Corner6100',
                     username=os.getenv("REDDIT_USERNAME"),
                     password=os.getenv("REDDIT_PASSWORD"))

# make sure that we are logged in correctly
if reddit.user.me() != os.getenv("REDDIT_USERNAME"):
    print("Failed to log in to Reddit :(")
    sys.exit(1)
print(f"Logged in to Reddit as {os.getenv("REDDIT_USERNAME")}")

# create a DataFrame to store posts
# posted date in epoch, comments as list, everything else is a string
posts = pd.DataFrame(columns=["Posted Time",
                              "Title",
                              "Author",
                              "Link",
                              "Content",
                              "Comments"])

# list subreddits to search
# set subreddits = ["all"] to search all of reddit
subreddits = ['cybersecurity',
              'technology',
              'k12sysadmin',
              'toronto',
              'canada',
              'askTO',
              'raleigh',
              'linustechtips']

# look through every subreddit
for subreddit_name in subreddits:
    # get the subreddit via api
    subreddit = reddit.subreddit(subreddit_name)
    # get the messages that meet a query (the same as the search bar)
    # sorts by recency and gets only messages from the most recent year
    # change limit to the most appropriate limit
    for post in subreddit.search("powerschool", sort="new", time_filter="year", limit=100):  # skipcq: FLK-E501
        # check the time of the post
        # 12/28/2024, the date of the breach, in epoch time
        breach_time = 1735344000
        if post.created_utc <= breach_time:
            # do not process comments if they occur after the breach
            continue
        time = dt.fromtimestamp(post.created_utc)

        # gets the link so we can review the post
        link = f"https://www.reddit.com/r/{subreddit}/comments/{post.id}/"

        # collects the data necessary
        # replace newlines with spaces because they are easier to work with
        data = [time,
                post.title,
                post.author.name,
                link,
                post.selftext.replace("\n", " "),
                post.comments.list()]
        # adds the data to the dataframe
        posts.loc[len(posts)] = data

# find the post with the most amount of comments
num_comments = 0
for comment_list in posts["Comments"]:
    num_comments = (len(comment_list)
                    if len(comment_list) > num_comments
                    else num_comments)

# create columns in the dataframe
comments = pd.DataFrame(
    columns=[f"Comment{i}" for i in range(1, num_comments + 1)]
)

for comment_list in posts["Comments"]:
    text = []
    # get every comment in every post
    for comment in comment_list:
        # replaces newlines with spaces because they are easier to work with
        text.append(comment.body.replace("\n", " "))
    # fill any empty spaces with NoneType
    text.extend([None] * (num_comments - len(text)))
    # add it to the dataframe
    comments.loc[len(comments)] = text

# merge the two tables together
res = pd.concat([posts, comments], axis=1)
# delete the list of comments because they have been converted to strings
res = res.drop("Comments", axis=1)


# write the final dataframe to a csv
res.to_csv("posts.csv")
