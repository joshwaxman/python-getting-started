
from hello.Statement import Statement
from pymongo import MongoClient
import hello.graphOutput as graphOutput

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

    wrapper += '<a href="https://www.sefaria.org/%s?lang=bi">%s</a></p>' % (title + '.' +str(page), title+" "+str(page)) #Pesachim.7b, Pesachim 7b

    nodes = set()
    edges = []

    # iterate through sugyot,
    # so that we have different graphs
    sugya = 0
    sugyaGraphs = []
    pplSet = set()

    for line in contents: # type: Dict[str, Any]
        eng, heb = line['eng'], line['heb'] # type: str, str
        html = line['html']
        names = line['names'] # type: List[Dict[str, str]]

        for item in names:
            pplSet.add(item['key'])

        proc = Statement(eng, heb)

        # if eng.startswith('§') or eng.startswith('MISHNA'):
        #     sugya += 0
        #     if len(nodes) > 0 or len(edges) > 0:
        #         sugyaGraphs.append((nodes, edges))
        #         #nodes = set()
        #         #edges = []

        from .EnglishStatementProcessor import EnglishStatementProcessor
        ep: EnglishStatementProcessor = EnglishStatementProcessor(proc)
        no, ed = ep.extractAll()
        nodes = nodes | no
        edges = edges + ed

        wrapper += html

    # fix up tags like < strong >
    wrapper = wrapper.replace('< ', '<')
    wrapper = wrapper.replace(' >', '>')

    leftside = wrapper

    allRabbis = [key for key in pplSet]

    e, n = graphOutput.findRelationship2(allRabbis)

    edges, nodes = graphOutput.graphTransformation(edges, nodes)

    return leftside, e, n, edges, nodes
