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

# delete when running in prod
quotes = ['I spent 2 days talking with lawyers after we were notified. Basically what our attorney and the attorney from our cyber insurance said was that we did need to notify to an extent, but we had to be careful in what we said. We want to appear as transparent as possible, but not say something that oversteps and puts liability on us. They advised that we avoid the term "breach". I would highly suggest discussing whatever you do with an attorney, I would hope you have cyber insurance. One of your first calls should have been to your cyber insurance company to make sure they are ready to pick up anywhere that PowerSchool fails. There is a lot of legal speak in what they are saying about notifications, like they will notify "in compliance with regulatory and contractual obligations." Does your state have regulation that requires them to notify or does it fall on you, if your state doesn\'t have regulations does your contract state that PowerSchool will be required to make the notifications? If you answered no to both of those, you may end up being responsible for all notifications. While we\'re all hoping that PowerSchool does the right thing, we won\'t know until they tell us exactly what they are going to do.',
 'On Monday, for instance, the Toronto District School Board notified parents, students, and former students that the breach exposed sensitive information of all students in the district between 1985 and 2024. Oh so i graduated high school more than a decade ago, i never saw, registered, or acknowledged this software, and my info might still be leaked. Awesome.',
 'Coming from the perspective of K12 I.T.  This is my worst nightmare.  And then finding out that the ransomware was paid, and deletion was validated via a video... would probably have me experiencing night terrors for the remainder of my life.   Hell our cyber security insurance would have a field day dropping us over that one. ',
 "My son's school board only notified us of the breach, not yet what data was stored with them. It's definitely much worse for our American neighbours as it looks like schools kept SSN stored there. In Canada (not sure about Quebec), we don't have to provide SIN to enrol in school.",
 "THIS. As a teacher and someone who isn't naive, it's like... we're just trusting them? What? That shit's already on the dark web, it has to be.",
 'Yeah our students school tried to downplay this. Clearly this is much bigger than originally thought. Insane.',
 'This is terrifying, I got the email just now and I thought it was a joke.. I signed up for child monitoring and my 15 year old sons SSN is being used by some dude in Colorado!!!',
 'But the PowerSchool paid the hackers to ransom their data, and made them pinky swear to delete it all, so the criminals sent PowerSchool a video of them "deleting" the data, so I\'m sure it\'s all fine. Criminals would never lie about something like that!  I\'m sure everything is fine!  ...  I\'m furious - my children and I are both impacted. It\'s a terrible idea to concentrate data at such scale in organizations that cannot secure the data. And I don\'t mean the organizations are doing a bad job with security (though many probably are), but rather that, if you understand technology well enough, you understand that nothing that can be accessed by anyone is "secure." It\'s just a question of risk appetite - information security will never be a profit incentive for corporations, except possibly for financial institutions operating at large scale, so it will always be inadequate. And by paying the ransom, this only further validates this "business model" for bad actors who seek to access and hold data hostage for financial gain.  This $200 cheque is nice and all, but I\'d like to see our school boards and healthcare funded well enough that these important functions don\'t need to be farmed out to massive corporations, thereby concentration risk in a single breakpoint, in the name of "fiscal (ir)responsibility."  The cat is out of the bag, though. That data is out there now - anyone who believes that it has actually been deleted is being misled, or very naive.',
 'I\x19m not too concern, 90% of the compromised information isn\x19t relevant to me today. And I graduated from high school 10 years ago. Let the hackers see my terrible grades from high school lol',
 "Another PowerSchool data breach has occurred on Dec 28, 2024 exposing students' & educators' info. including names, dates of birth, & more. Powerschool is sending impacted parties information on identity theft, filing police report, etc. Below is a portion of the email I received today G When I first examined the concerns with Powerschool/Schoology I reached out to the Homeschool Charter we used to be with and expressed the concerns and followed-up with telling the school to have Powerschool/Schoology completely expunge any and all data stored on our children and family. Schools are crossing the line with immense data collection and monitoring of students and thwir families and it will continue to put your personal information at risk to hackers.",
 'Anyone else just now finding out about the PowerSchool data breach from DECEMBER?! I received a letter yesterday for one of my children \x14 and then another one at 3:45 AM this morning for my other child. Why are these notifications being sent out MONTHS later and at such random times? This breach happened back in December 2024, and it may have exposed our children\x19s personal info \x14 names, birthdates, contact info, and possibly even Social Security Numbers. They\x19re offering two years of identity protection, but this late notice is unacceptable. As parents, we should have been informed immediately. The lack of urgency and transparency is disturbing. Check your emails and mailboxes, y\x19all. If you got a letter, speak up \x14 we deserve better communication and accountability when it comes to our kids.',
 "i suggest y'all check your emails from powerschool regarding data breach if your children are enrolled in schools using this platform. ** mine go to andalusia ** i just used activation code for experian minor plus from email & one of my children's information has been fully breached and someone else is using her social--  experian minor plus has shown her social has been listed on the dark web, shown me their name, address, and companies of the person that has been using my child's social & when it first started.  this is about to be a long journey. *** due to post being made by andalusia city schools saying no socials have been released. i'm posting this for awareness. if it werent for that email and me checking i would have never thought or known to check my children's information. my child's information has been to the school & insurance companies & that is it. regardless of how it has happened people should be aware and keep monitoring their children's information as you never know when it can happen to you & all you're going to have to deal with once something arises. so if you've got an email with an activation code to get free monitoring -- use it.",
 'PowerSchool had a cybersecurity attack in December 2024. It was not released to the public until January that this data breach occurred. They promised extra protection for anyone whose information was compromised. That email was sent to me on Feb 13th from PowerSchool. I finally (March 3rd) got around to going through the process of using the activation code with https://lnkd.in/eQD2UHGb that will help me to monitor my children\x19s identities and prevent fraud.  Luckily I found they are safe for now, but my phone number and email are all over the place. No wonder I get so many spam calls! #powerschool #cyberattack #identitytheft #protectyourkids',
 'Shit that means my data could\x19ve been leaked too and I graduated nearly 15 years ago',
 'I\x19ve been getting emails from my kids school about this. I don\x19t understand.',
 'As a student, this is infuriating. We have no control over how our data is used, stored or "protected". There are children affected by these breaches before they can read. What annoys me further is that PowerSchool and the boards assured us that the data was deleted, but it never was. I\'m losing trust in this. This is lawsuit fuel.',
 "Thank you. I'm in western NC, and there has been no word of this from my daughter's school. They're still on this system.",
 'This is the long list of breached information, going back - 40 years / . I don\x19t recall hearing about this at the time. My kids are no longer with the TDSB but their information would have been compromised. Perhaps they should have been in touch with everyone affected and not only current students. ',
 'Our SIS currently does not even offer MFA, never has. I\'ve been asking(see: gently bitching to) them about it for years. I asked them last week because of this powerschool attack and was told due to other issues, there is now no ETA for additional security. It frustrates me greatly, but is completely out of our control. We cannot afford a "better SIS" and powerschool getting hacked removes any argument that paying more equates to better security.',
 'I work in a school system as a technician. PowerSchool has been awful about communicating anything to systems. Most of the information about what has happened has been collaboration between school systems.  It\x19s still shocking to me that PowerSchool has not been enforcing two factor on anyone even its employees. This is tens of thousands of students and staff personal information leaked, and PowerSchool let it happen.  The best part is PowerSchool says they got a video that shows the deletion of the data. So therefore everything is good, and we shouldn\x19t need to worry!',
 "PowerSchool didn't send the credit monitoring offer to more than a handful of our users. I've lost all faith in PowerSchool, we all know that you shouldn't trust a bad actor to be anything more than that. If they are going to steal your data, you can't trust them to be honest when they say they are going to delete it."]

results = []
for quote in tqdm(quotes, desc="AI Progress"):
    # call the ollama api to determine role
    result = call_ollama_api(
        prompt="Read the following message about the PowerSchool data breach and determine the role of the person who wrote it. "
               "Respond with only one word from the following list: parent, student, teacher, admin, general, or unsure. "
               "If you are not more than 50% confident in your classification, respond with unsure. "
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
