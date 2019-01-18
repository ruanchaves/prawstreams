import psycopg2
import praw
import select
import json
import re
import os

class Listener(object):

    def __init__(self):
        self.channel = 'events'
        self.conn = ''
        self.cur = ''

    def connect(self,mode='local',dbname='reddit',user='postgres'):
        if mode == 'local':
            self.conn = psycopg2.connect("dbname={0} user={1}".format(dbname,user))
        if mode == 'heroku':
            self.conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.conn.cursor()

    def fetch(self):
        self.cur.execute("LISTEN {0};".format(self.channel))
        while 1:
            if select.select([self.conn], [], [], 5) == ([], [], []):
                yield None #timeout
            else:
                self.conn.poll()
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    yield { 'payload' : notify.payload,
                            'pid' : notify.pid,
                            'channel' : notify.channel }

    def __iter__(self):
        for item in self.fetch():
            if item == None:
                continue
            payload = json.loads(item['payload'])
            if payload['action'] == 'INSERT':
                yield { 'id' : payload['data']['reddit_id'],
                       'class' : payload['data']['class'] }

class Driver(object):
    def __init__(self):
        self.conn = ''
        self.cur = ''
        self.limit = 9000
        self.init_file = 'initialize.sql'
        self.conn_args = []
        self.conn_kwargs = {}

    def connect(self,mode='local',dbname='reddit',user='postgres'):
        if mode == 'local':
            self.conn = psycopg2.connect("dbname={0} user={1}".format(dbname,user))
        if mode == 'heroku':
            self.conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        self.conn.set_session(autocommit=True)
        self.cur = self.conn.cursor()
        self.cur.execute(open(self.init_file,'r').read())

    def heroku_connect(self):
        args = [os.environ['DATABASE_URL']]
        kwargs = { 'sslmode' : 'require' }
        self.connect(args,kwargs)

    def pull(self,query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def pull_var(self,query,var):
        self.cur = self.conn.cursor()
        self.cur.execute(query,var)
        rows = self.cur.fetchall()
        return rows

    def push(self, query):
        self.cur.execute(query)
        self.conn.commit()

    def push_var(self, query, var):
        self.cur.execute(query, var)
        self.conn.commit()

    def serialize(self,table=None):
        if not table:
            self.cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE tablename NOT LIKE '%\_%';")
            result = [ y for x in self.cur.fetchall() for y in x ]
        else:
            result = [ table ]
        for t in result:
            query = "ALTER SEQUENCE {0}_id_seq RESTART WITH 1;".format(t)
            self.cur.execute(query)
            self.conn.commit()

    def check(self,table):
        query = 'select count(*) from {0}'.format(table)
        count = self.pull(query)
        count = count[0][0]
        if count >= self.limit:
            query = "DELETE FROM {0};"
            query = query.format(table,self.limit)
            self.push(query)
            self.serialize(table)
