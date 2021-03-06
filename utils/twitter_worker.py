# -*- coding: utf-8 -*-
"""

@author: Ashu Gupta

"""
import csv
import pandas as pd
import tweepy

class TwitterWorker(object):
    #Getting twitter names and handles.
    max_tweets = 100
    max_display_tweets = 5
    default_handle = 'realDonaldTrump'
    def __init__(self):
        self.api = self._get_twitter_api()

    def _get_twitter_api(self):
        auth = tweepy.OAuthHandler('eHcU05mx45dXC0l3gOLUTAXyg', 'YVdIkqzw91L6dU5hEwcQkyQdcPyThb8gIOlyOdWiYNrMlGSvwJ')
        auth.set_access_token('3311641620-NlexlsblK99LbXUA51quO5Tvsq7CQA7KEUkYB3c', '4UqeUPc02BLaS00sXstFJLlo8dfmxIPlCX5Kr9syTAKLa')
        api = tweepy.API(auth)
        return api

    def validate_handle(self, handle):
        try:
            user = self.api.get_user(handle)
        except tweepy.TweepError as e:
            return False
        return user

    def getHandleFromUid(self, uid):
        try:
            handle = self.api.get_user(uid).screen_name
        except tweepy.TweepError as e:
            handle = self.default_handle
        return handle

    def _tweet_yielder(self, cursor):
        while True:
            try:
                yield cursor.next()
            except:
                break

    def get_tweets(self, handle):
        # posts = []
        # if self.validate_handle(handle):
        #     try:
        #         i = 0
        #         cursor = tweepy.Cursor(self.api.user_timeline, screen_name=handle, tweet_mode="extended",
        #                                include_rts=True).items()
        #         for status in self._tweet_yielder(cursor):
        #             i += 1
        #             try:
        #                 tweet = status._json['retweeted_status']['full_text']
        #             except:
        #                 tweet = status._json['full_text']
        #             posts.append(tweet)
        #             if i >= self.max_tweets: break
        #     except tweepy.TweepError as e:
        #         return []
        # # import unicodecsv as csv
        # # with open('/Users/salvatoregiorgi/Documents/' + handle + '.csv', "wb") as csv_file:
        # #     writer = csv.writer(csv_file, delimiter=',')
        # #     for line in posts:
        # #         writer.writerow([line])
        # # print("LENGTH", len(posts))
        # return posts
        all_tweets = []
        all_the_tweets = []
        if self.validate_handle(handle):
            try:
                new_tweets = self.api.user_timeline(screen_name=handle, count=100)
                all_the_tweets.extend(new_tweets)

                outtweets = [[tweet.text] for tweet in all_the_tweets]
                if len(outtweets) == 0:
                    return

                for tweet in outtweets:
                    for actual_tweet in tweet:
                        string_form = actual_tweet.encode("ascii", errors="ignore").decode()
                        all_tweets.append(string_form)
            except tweepy.TweepError as e:
                return []
        
        return all_tweets
        

    def get_profile(self, handle):
        user = self.validate_handle(handle)
        name = user.name
        profile_image = user.profile_image_url.replace("_normal", "_400x400")
        desc = user.description
        return {'name': name, 'profile_image': profile_image}

