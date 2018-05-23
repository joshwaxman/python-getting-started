import markdown
from pymongo import *

def getBlogPost():
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    posts = db.posts

    try:
        html = ''
        for post in db.posts.find().sort('theDate', ASCENDING).limit(10):
            html +=  markdown.markdown(post['text'])
    except:
        html = 'default text'

    return html
