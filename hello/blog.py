import mistune
from pymongo import *

def getBlogPost():
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    posts = db.posts

    try:
        html = ''
        for post in db.posts.find().sort('theDate', ASCENDING).limit(10):
            html += mistune.markdown(post['text'])
            author = post['author']
            theDate = post['theDate']
            tags = post['tags']
            html += ('<p/>posted by ' + author + ' at ' + str(theDate))
            html += ('<p/>tags ' + str(tags))
    except Exception as e:
        html = str(e)

    return html
