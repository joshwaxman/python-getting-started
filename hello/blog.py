import mistune
from pymongo import *

def getBlogPost():
    client = MongoClient(
        "mongodb://mivami")
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
