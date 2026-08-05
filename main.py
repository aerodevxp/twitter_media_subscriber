import asyncio


from twikit import Client #pip install git+https://github.com/PawiX25/twifork.git
from dotenv import load_dotenv
import yt_dlp
import os
from time import sleep



load_dotenv()
USERNAME = os.environ['USERNAME_LOGIN']
EMAIL = os.environ['EMAIL_LOGIN']
PASSWORD = os.environ['PASS_LOGIN']

SUBS = os.environ['SUBSCRIPTIONS'].split(',')
tweetsToCheck = int(os.environ['TWEET_AMOUNT']) #per user. set to 0 to always fetch all available tweets.


# Initialize client
client = Client('en-US', impersonate='chrome124')

async def main():
    client.load_cookies(os.environ['COOKIE_FILE_JSON'])

    await client.is_logged_in()

    print(f"Subscribed to: {SUBS}")

    to_download = []

    for subscribed_user in SUBS:
        user = await client.get_user_by_screen_name(subscribed_user)
        print(f"Tackling @{subscribed_user}.")
        tweets = []
        _count = 15
        if tweetsToCheck <= 15 and tweetsToCheck >= 1:
            _count = tweetsToCheck
        
        _tweets = await client.get_user_tweets(user.id, 'Tweets', count=_count)
        for tweet in _tweets:
            if (tweet.retweeted_tweet):
                tweets.append(tweet.retweeted_tweet)
            else:
                tweets.append(tweet)
        print(f"Fetched new tweets: {len(tweets)} tweets total from {subscribed_user}.")

        print(f"{subscribed_user} has {user.statuses_count} tweets. The script will fetch tweets until all are fetched or your set limit is reached.")
        
        if tweetsToCheck < 1:
            while len(tweets) < user.statuses_count:
                sleep(10)
                print(f"Fetching new tweets. Currently at {len(tweets)}.")
                _tweets = await _tweets.next()
                for tweet in _tweets:
                    if tweet.retweeted_tweet:
                        tweets.append(tweet.retweeted_tweet)
                    else:
                        tweets.append(tweet)
                print(f"Fetched new tweets: {len(tweets)} tweets total from {subscribed_user}.")
        else:
            while len(tweets) < tweetsToCheck and len(tweets) < user.statuses_count:
                sleep(3)
                print(f"Fetching new tweets. Currently at {len(tweets)}.")
                _tweets = await _tweets.next()
                for tweet in _tweets:
                    if tweet.retweeted_tweet:
                        tweets.append(tweet.retweeted_tweet)
                    else:
                        tweets.append(tweet)
                print(f"Fetched new tweets: {len(tweets)} tweets total from {subscribed_user}.")
            


        for tweet in tweets:
            if tweet.media:
                for file in tweet.media:
                    to_download.append(file.url)
        
    i = 0
    print(f"{len(to_download)} medias available for downloading.")
    for fileurl in to_download:
        i = i + 1
        print(f"{i}/{len(to_download)}")
        ydl_opts = {
            'cookiefile':os.environ['COOKIE_FILE_TXT'],
            "format": "bv*+ba/best",
            "merge_output_format": "mp4",
            "prefer_free_formats": False,
            "ignoreerrors": True,
            "nooverwrites": True,
            "windowsfilenames": True,
            "restrictfilenames": True,
            "outtmpl": os.environ['OUTPUT_MPL']
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([fileurl])


asyncio.run(main())