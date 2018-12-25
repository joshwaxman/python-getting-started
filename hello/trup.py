from pymongo import MongoClient
def getTree(verse):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    trup = db.trup
    search = dict(key=verse)
    x = trup.find_one(search)
    tree = x['tree']
    text = x['text']
    tagged = x['tagged']
    return tree, text, tagged