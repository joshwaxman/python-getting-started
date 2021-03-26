import os
#from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph
from py2neo.data import walk

driver = None
session = None

def getDistFullList():
    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    html = '<h1>Full shoresh list</h1>'
    data = g.run('MATCH (n:ShoreshDist) RETURN n ORDER by n.heName').data()

    words = []
    for node in data:
        root = node['n']['heName']
        words.append(root)

    prevword = ' '
    for word in words:
        if word[0] != prevword[0]:
            html += '<h2>' + word[0] + '</h2>\n'

        html += '<a href="' + word + '">' + word + '</a>\n&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        prevword = word

    return html, [], []

    return html, [], []

def getShoreshDist(shoresh: str):
    d = dict()
    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    #/ browser /:24780 / db / data /
    html = ''

    p = g.nodes.match('ShoreshDist', heName=shoresh)
    if len(p) == 0:
        return

    # for now, only process first one
    p = p.first()
    html += '<b>Shoresh</b>: ' + p['heName'] + '<br/>'
    # right now, no meaning. we *could* look it up in klein
    #html += '<b>Meaning</b>: ' + p['gloss'] + '<br/>'

    nodes = []
    key = p['heName']
    nodeDict = dict()
    nodeDict[key] = 0
    nodes.append(dict(root=p['heName'], meaning=''))

    rels = g.match(nodes=[p, None])
    rels2 = g.match(nodes=[None, p])
    #rels2 = g.match(nodes=[None, p], r_type='')

    html += '<br/><b>Similar words:</b><br/>'
    edges = []
    i = 0
    if len(rels) > 0:
        for rel in rels:
            other = rel.end_node
            label = type(rel).__name__

            html += other['heName'] + '&nbsp;&nbsp;&nbsp;' + '<br/>'
            key = other['heName']
            if key not in nodeDict:
                i += 1
                nodes.append({'root': other['heName'], 'meaning': ''})
                nodeDict[key] = i
                j = i
            else:
                j = nodeDict[key]
            edges.append(dict(source=0, target=j, label=label))

    # in nodes
    if len(rels2) > 0:
        for rel in rels2:
            other = rel.start_node
            label = type(rel).__name__

            key = other['heName']
            if key not in nodeDict:
                i = i + 1
                html += '<a href="' + other['heName'] + '">' + other['heName'] + '</a>&nbsp;&nbsp;&nbsp;' + '<br/>'

                nodes.append({'root': key, 'meaning': ''})
                nodeDict[key] = i
                j = i
            else:
                j = nodeDict[key]
            edges.append(dict(source=0, target=j, label=label))

    return html, nodes, edges