#from django.contrib.gis.geoip2 import GeoIP2
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


def htmlOutputter(title: str, page: str):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    mivami = db.mivami

    if page.endswith('b'):
        prevPage = page[:-1] + 'a'
        nextPage = str((int(page[:-1]))+1) + 'a'
    else:
        prevPage = str((int(page[:-1]))-1) + 'b'
        nextPage = page[:-1] + 'b'
    wrapper = '<a href="/talmud/' + title + '.' + prevPage + '">Previous</a> | ' + \
              '<a href="/talmud/' + title + '.' + nextPage + '">Next</a> | '

    amud = page[-1]
    daf_start = (int(page[:-1]) - 2) * 2
    if amud == 'b':
        daf_start += 1

    daf = daf_start

    theText = {'title': title + ":" + str(daf)}
    theText = list(mivami.find(theText))

    item = theText[0]
    contents = item['contents']
    student_nodes = item['EncodedNodes']
    student_edges = item['EncodedEdges']
    local_interaction_nodes = item['LocalInteractionNodes']
    local_interaction_edges = item['LocalInteractionEdges']
    if 'GlobalInteractionNodes' in theText[0]:
        global_interaction_nodes = item['GlobalInteractionNodes']
        global_interaction_edges = item['GlobalInteractionEdges']
    else:
        global_interaction_nodes = local_interaction_nodes
        global_interaction_edges = local_interaction_edges


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

    # why was this not precomputed?
    local_interaction_edges, local_interaction_nodes = graphOutput.graphTransformation(local_interaction_edges, local_interaction_nodes)


    return leftside, student_edges, student_nodes, local_interaction_edges, local_interaction_nodes, \
           global_interaction_edges, global_interaction_nodes
