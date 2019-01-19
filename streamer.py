import praw
import os
import psycopg2
import random
import re
from utils import Driver


class ArchiveBot(Bot):

    def __init__(self,username):
        super().__init__(username)

    def archive(self,body):
        urls = get_urls(body)
        for url in urls:
            page, is_not_cache = savepagenow.capture_or_cache(url)
        return page

    def compile(self,md_urls):

        if not md_urls:
            return None
        if any([ self.regexp(v) for v in md_urls.values() ]):
            return None

        template = self.template
        body = ''

        for key in md_urls.keys():
            body += '* [{0}]({1})    \n'.format(key,self.archive(md_urls[key]) )
        return body

    def regexp(self,text):
        query = "SELECT expression FROM regexp;"
        result = [ y for x in self.driver.pull(query) for y in x ]
        for pattern in result:
            if pattern in text:
                return True
        else:
            return False

    def process(self,body):
        INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        md_urls = dict(INLINE_LINK_RE.findall(body))
        return md_urls

    def get_message(self,obj):
        body = self.get_body(obj)
        message = self.compile(self.process(body))
        if not message:
            return None
        message = self.template.format(message)
        return message

    def get_body(self,obj):
        if self.is_class(obj, 'comment'):
            body = obj.body
        elif self.is_class(obj,'submission'):
            body = "[{0}]({1}) {2}".format(obj.title,obj.url,obj.selftext)
        return body

    def __call__(self,item):

        myself = self.reddit.redditor(self.username)
        if not self.check(myself.id):
            self.block(myself.id,'redditor')

        obj = self.read(item)
        obj_id = obj.id
        body = self.get_body(obj)
        redditor = obj.author
        redditor_id = redditor.id


        if self.unblock_command in body:
            if self.check(redditor_id):
                self.unblock(redditor_id)
                return None
        elif self.block_command in body:
            if not self.check(redditor_id):
                self.block(redditor_id,'redditor')
                return None

        if self.check(obj_id):
            return None
        if self.check(redditor_id):
            return None

        try:
            obj.reply( self.get_message(obj) )
        except Exception as e:
            pass
        self.block(obj.id, self.get_type(obj))

class Streamer(object):
    def __init__(self,*args,**kwargs):
        self.reddit = ''
        self.driver = Driver()
        self.bot = ArchiveBot()

    def auth(self):
        return  praw.Reddit(client_id=self.account['CLIENT_ID'],
                           client_secret=self.account['CLIENT_SECRET'],
                           password=self.account['PASSWORD'],
                           user_agent=self.account['USER_AGENT'],
                           username=self.account['USERNAME'])

    def connect(self,mode='local'):
        self.driver.connect(mode='local')
        query = 'SELECT * FROM accounts'
        account = self.driver.pull(query)
        account = account[0]
        self.account = {
                'id' : account[0],
                'CLIENT_ID' : account[1],
                'CLIENT_SECRET' : account[2],
                'PASSWORD' : account[3],
                'USER_AGENT' : account[4],
                'USERNAME' : account[5]
            }
        self.reddit = self.auth()

    def compile(self,**kwargs):
        self.results = []
        mentions = self.reddit.inbox.unread(**kwargs)
        self.results.extend(mentions)
        self.results.sort(key=lambda post: post.created_utc, reverse=True)
        return self.results

    def __iter__(self):
        stream = praw.models.util.stream_generator(lambda **kwargs: self.compile(**kwargs))
        for idx,post in enumerate(stream):
            self.reddit.inbox.mark_read([post])
            body = ''
            try:
                post_type = post.parent().__class__.__name__.lower()
            except:
                continue
            if post_type == 'submission':
                url = post.parent().url
                title = post.parent().title
                if 'reddit.com' in url:
                    try:
                        selftext = post.parent().selftext
                        body =  " ".join([title, selftext])
                    except:
                        continue
                else:
                    body = " ".join([title, url])
            elif post_type == 'comment' or post_type == 'message':
                body = post.parent().body
            else:
                continue
            post.reply(self.bot.archive(body))

if __name__ == '__main__':
    stream = Streamer()
    stream.connect()
    for post in stream:
        print(post)
