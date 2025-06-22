import os
import sys
from datetime import datetime as dt  # imports datetime to deal with dates

import pandas as pd  # imports pandas for data manipulation
import praw  # imports praw for reddit access
from dotenv import load_dotenv  # get login secrets
from praw.models import MoreComments
from tqdm import tqdm  # show progress bars

load_dotenv()  # gets secrets


# helper function to get all comments from a post
def get_all_comments(comments_list, limit=None):
    """
    Gets all comments from a list, even if there are MoreComments
    :param comments_list: The list of comments
    :param limit: Optional - the limit of MoreComments to read, or None for no limit
    :return: A list of all comments, with only Comments
    """
    all_comments = []
    more_comments_count = 0

    for item in comments_list:
        if isinstance(item, MoreComments):
            if limit is None or more_comments_count < limit:
                try:
                    # Get comments from MoreComments object
                    new_comments = item.comments()

                    # Recursively process in case there are nested MoreComments
                    processed_comments = get_all_comments(new_comments, limit)
                    all_comments.extend(processed_comments)

                    more_comments_count += 1

                except Exception as e:
                    print(f"Error expanding MoreComments: {e}")
                    continue
            else:
                break
        else:
            # Regular Comment object
            all_comments.append(item)

    return all_comments


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
# skipcq: FLK-E501
# subreddits = ['cybersecurity', 'technology', 'k12sysadmin', 'toronto', 'canada', 'askTO', 'raleigh', 'linustechtips']
subreddits = ["all"]

# look through every subreddit
for subreddit_name in subreddits:
    # get the subreddit via api
    subreddit = reddit.subreddit(subreddit_name)
    # get the messages that meet a query (the same as the search bar)
    # sorts by relevance and gets only messages from the most recent year
    # change limit to the most appropriate limit
    # tqdm shows progress bar
    for post in tqdm(subreddit.search("powerschool data breach",
                                      sort="relevance",
                                      time_filter="year",
                                      limit=2),
                     desc=f"r/{subreddit} progress"):
        # check the time of the post
        # 12/28/2024, the date of the breach, in epoch time
        breach_time = 1735344000
        if post.created_utc <= breach_time:
            # do not process comments if they occur before the breach
            continue
        time = dt.fromtimestamp(post.created_utc)

        # gets the link so we can review the post
        link = f"https://www.reddit.com/r/{post.subreddit.display_name}/comments/{post.id}/"

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

# First, expand all MoreComments objects in all comment lists
expanded_comments_lists = []

for comment_list in tqdm(posts["Comments"], desc="Expanding MoreComments"):
    expanded_list = get_all_comments(comment_list)
    expanded_comments_lists.append(expanded_list)

# Now find the maximum number of comments after expansion
num_comments = 0
for expanded_comment_list in expanded_comments_lists:
    num_comments = (len(expanded_comment_list)
                    if len(expanded_comment_list) > num_comments
                    else num_comments)

# Create columns in the dataframe based on the actual expanded comment counts
comments = pd.DataFrame(
    columns=[f"Comment{i}" for i in range(1, num_comments + 1)]
)

# Process the already-expanded comment lists
for expanded_comment_list in tqdm(expanded_comments_lists, desc="Processing comments"):
    text = []

    # Get every comment in every post (already expanded)
    for comment in expanded_comment_list:
        # Replace newlines with spaces because they are easier to work with
        text.append(comment.body.replace("\n", " "))

    # Fill any empty spaces with None
    text.extend([None] * (num_comments - len(text)))

    # Add it to the dataframe
    comments.loc[len(comments)] = text

# merge the two tables together
res = pd.concat([posts, comments], axis=1)
# delete the list of comments because they have been converted to strings
res = res.drop("Comments", axis=1)

# write the final dataframe to a csv
res.to_csv("posts.csv")
