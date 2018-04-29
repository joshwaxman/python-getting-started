
from hello.Statement import Statement
from pymongo import MongoClient
import datetime
import hello.graphOutput as graphOutput

def getDafYomi():
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    dafyomi = db.dafyomi
    now = datetime.datetime.now()
    theDate = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
    theDaf = {'date': theDate }
    x = dafyomi.find_one(theDaf)['daf'].split()
    masechet = x[0]
    daf = x[1] + 'a'
    return masechet, daf


def htmlOutputter(title, page):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    mivami = db.mivami

    wrapper = ''

    amud = page[-1]
    daf_start = (int(page[:-1]) - 2) * 2
    if amud == 'b':
        daf_start += 1

    daf = daf_start

    theText = {'title': title + ":" + str(daf)}
    theText = list(mivami.find(theText))
    contents = theText[0]['contents']
    n = theText[0]['EncodedNodes']
    e = theText[0]['EncodedEdges']
    nodes = theText[0]['LocalInteractionNodes']
    edges = theText[0]['LocalInteractionEdges']


    wrapper += '<a href="https://www.sefaria.org/%s?lang=bi">%s</a></p>' % (title + '.' +str(page), title+" "+str(page)) #Pesachim.7b, Pesachim 7b

    # iterate through sugyot,
    # so that we have different graphs
    sugya = 0
    sugyaGraphs = []
    pplSet = set()

    for line in contents: # type: Dict[str, Any]
        #eng, heb = line['eng'], line['heb'] # type: str, str
        html = line['html']

        wrapper += html

    # fix up tags like < strong >
    wrapper = wrapper.replace('< ', '<')
    wrapper = wrapper.replace(' >', '>')

    leftside = wrapper

    edges, nodes = graphOutput.graphTransformation(edges, nodes)

    return leftside, e, n, edges, nodes
