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
    for node in data:
        root = node['n']['heName']
        html += '<a href="' + root + '"</a>' + root + '\n<br/>'

    return html, [], []

def getShoreshDist(shoresh: str):
    d = dict()
    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    #/ browser /:24780 / db / data /
    html = ''

    p = g.nodes.match('ShoreshDist', root=shoresh)
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

    edges = []
    if len(rels) > 0:
        html += '<br/><b>Similar words:</b><br/>'
        for i, rel in enumerate(rels, 1):
            other = rel.end_node
            label = rel.label

            html += other['root'] + '&nbsp;&nbsp;&nbsp;' + other['gloss'] + '<br/>'
            key = other['root']
            nodes.append({'root': other['root'], 'meaning': ''})
            nodeDict[key] = i
            edges.append(dict(source=0, target=i, label=label))
    else:
        i = 0

    # in nodes
    if len(rels2) > 0:
        for i, rel in enumerate(rels2, i+1):
            other = rel.start_node
            label = rel.label

            html += '<a href="' + other['root'] + '">' + other['root'] + '</a>&nbsp;&nbsp;&nbsp;' + other['gloss'] + '<br/>'
            key = other['root']
            gloss =  other['gloss']
            pos = gloss.find('.')
            gloss = gloss[:pos]
            nodes.append({'root': other['root'], 'meaning': gloss})
            nodeDict[key] = i
            edges.append(dict(source=0, target=i, label=label))

    return html, nodes, edges