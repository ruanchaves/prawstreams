import praw
import os
import psycopg2
import random

from utils import Driver

class Streamer(object):
    def __init__(self,*args,**kwargs):
        self.reddit = []
        self.subreddits_names = []
        self.subreddits_table = 'subreddits'
        self.inbox_table = 'inbox'
        self.subreddits = []
        self.results = []
        self.account = {}

        self.inbox = { 'all' : False,
                       'comment_replies' : False,
                       'mentions' : False,
                       'messages' : False,
                       'stream' : False,
                       'submission_replies' : False }

        self.driver = Driver()


    def auth(self):
        return  praw.Reddit(client_id=self.account['CLIENT_ID'],
                           client_secret=self.account['CLIENT_SECRET'],
                           password=self.account['PASSWORD'],
                           user_agent=self.account['USER_AGENT'],
                           username=self.account['USERNAME'])

    def connect(self,mode='local'):
        self.driver.connect(mode=mode)
        self.reddit.append(self.auth())
        self.update_subreddits()
        self.update_inbox()

    def update_subreddits(self):
        subs = self.driver.pull('select * from {0}'.format(self.subreddits_table))
        self.subreddits_names = [ x for t in subs for x in t ]
        self.subreddits_names = [ x for x in self.subreddits_names if isinstance(x,str) ]

    def update_inbox(self):
        self.driver = Driver()
        inbox = self.driver.pull('select * from {0}'.format(self.inbox_table))
        print(inbox)
        values = [ x for t in inbox for x in t ]
        self.inbox = { 'all' : values[1],
                       'comment_replies' : values[2],
                       'mentions' : values[3],
                       'messages' : values[4],
                       'stream' : values[5],
                       'submission_replies' : values[6] }

    def translate(self):
        self.subreddits = [ random.choice(self.reddit).subreddit(x) for x in self.subreddits_names ]

    def get_inbox(self,function,**kwargs):
        if self.inbox[function] == True:
            for idx, item in enumerate(self.reddit):
                self.results.extend(self.reddit.__getitem__(idx).inbox.__getattribute__(function).__call__(**kwargs))

    def compile(self,**kwargs):
        self.results = []
        for subreddit in self.subreddits:
            if self.submissions:
                submissions = subreddit.new(**kwargs)
            if self.comments:
                comments = subreddit.comments(**kwargs)
            self.results.extend(submissions)
            self.results.extend(comments)
        for key in self.inbox.keys():
            self.get_inbox(key)
        self.results.sort(key=lambda post: post.created_utc, reverse=True)
        return self.results

    def __iter__(self):
        stream = praw.models.util.stream_generator(lambda **kwargs: self.compile(**kwargs))
        for idx,post in enumerate(stream):
            yield post

    def __call__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        self.translate()

class Manager(object):

    def __init__(self,mode='local'):
        self.account = ''

        self.driver = Driver()
        self.driver.connect(mode=mode)

        self.streamer = Streamer()

        self.stream_table = 'stream'
        self.accounts_table = 'accounts'
        self.limit = self.driver.limit

    def auth(self):
        query = 'SELECT * FROM accounts'
        account = self.driver.pull(query)
        account = random.choice(account)
        self.account = {
                'id' : account[0],
                'CLIENT_ID' : account[1],
                'CLIENT_SECRET' : account[2],
                'PASSWORD' : account[3],
                'USER_AGENT' : account[4],
                'USERNAME' : account[5]
            }

    def connect(self,mode='local'):
        self.streamer.account = self.account
        self.streamer.connect(mode=mode)

    def run(self):
        self.driver.check(self.stream_table)
        columns_query = "select column_name from information_schema.columns where table_name = '{0}';".format(self.stream_table)
        columns_result = self.driver.pull(columns_query)
        columns_result = [ x for t in columns_result for x in t ]
        columns_result = [ x for x in columns_result if x != 'id_' ]
        select_query = "select * from {0} where id = '{1}'"
        insert_query = 'insert into {0} (reddit_id,class) values (%s,%s)'
        idx = 0
        for post in self.streamer:
            idx += 1
            post_type = post.__class__.__name__
            post_id = post.id
            copies = self.driver.pull(select_query.format(self.stream_table, post_id))
            copies = [ x for t in copies for x in t ]
            if not any(copies):
                self.driver.push(insert_query.format(self.stream_table))
            if idx >= self.limit:
                self.driver.check(self.stream_table)
                idx = 1
            yield post_type, post_id

    def __call__(self):
        return self.run()

if __name__ == '__main__':
    man = Manager(mode='heroku')
    man.auth()
    man.connect(mode='heroku')
    for post in man():
        print(post)
