import os
#from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph
from py2neo.data import walk

driver = None
session = None

def getKleinFullList():
    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    html = '<h1>Full shoresh list</h1>'
    data = g.run('MATCH (n:KleinShoresh) RETURN n ORDER by n.root').data()
    for node in data:
        root = node['n']['root']
        html += '<a href="' + root + '"</a>' + root + '\n<br/>'

    return html, [], []

def getKleinShoresh(shoresh: str):
    d = dict()
    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    #/ browser /:24780 / db / data /
    html = ''

    p = g.nodes.match('KleinShoresh', root=shoresh)
    if len(p) == 0:
        return

    # for now, only process first one
    p = p.first()
    html += '<b>Shoresh</b>: ' + p['root'] + '<br/>'
    html += '<b>Meaning</b>: ' + p['gloss'] + '<br/>'

    nodes = []
    key = p['root'] + ';' + p['gloss']
    nodeDict = dict()
    nodeDict[key] = 0
    gloss = p['gloss']
    pos = gloss.find('.')
    gloss = gloss[:pos]
    nodes.append(dict(root=p['root'], meaning=gloss))

    rels = g.match(nodes=[p, None], r_type='IS_SIMILAR')
    rels2 = g.match(nodes=[None, p], r_type='IS_SIMILAR')
    edges = []

    # out nodes
    html += '<br/><b>Similar words:</b><br/>'
    if len(rels) > 0:
        for i, rel in enumerate(rels, 1):
            other = rel.end_node

            html += '<a href="' + other['root'] + '">' + other['root'] + '</a>&nbsp;&nbsp;&nbsp;' + other['gloss'] + '<br/>'
            key = other['root']
            gloss =  other['gloss']
            pos = gloss.find('.')
            gloss = gloss[:pos]
            nodes.append({'root': other['root'], 'meaning': gloss})
            nodeDict[key] = i
            edges.append(dict(source=0, target=i, label='IS_SIMILAR'))
    else:
        i = 0

    # in nodes
    if len(rels2) > 0:
        for i, rel in enumerate(rels2, i+1):
            other = rel.start_node

            html += '<a href="' + other['root'] + '">' + other['root'] + '</a>&nbsp;&nbsp;&nbsp;' + other['gloss'] + '<br/>'
            key = other['root']
            gloss =  other['gloss']
            pos = gloss.find('.')
            gloss = gloss[:pos]
            nodes.append({'root': other['root'], 'meaning': gloss})
            nodeDict[key] = i
            edges.append(dict(source=0, target=i, label='IS_SIMILAR'))

    return html, nodes, edges