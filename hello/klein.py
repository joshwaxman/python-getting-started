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
    html += 'Shoresh: ' + p['root'] + '<br/>'
    html += 'Meaning: ' + p['gloss'] + '<br/>'

    nodes = []
    key = p['root'] + ';' + p['gloss']
    nodeDict = dict()
    nodeDict[key] = 0
    nodes.append(dict(root=p['root'], meaning=p['gloss']))

    rels = g.match(nodes=[p, None], r_type='IS_SIMILAR')
    phonemic_classes = set()
    edges = []
    if len(rels) > 0:
        html += '<br/><b>Similar words:</b><br/>'
        for i, rel in enumerate(rels, 1):
            other = rel.end_node

            html += other['root'] + '&nbsp;&nbsp;&nbsp;' + other['gloss'] + '<br/>'
            key = other['root']
            nodes.append(other)
            nodeDict[key] = i
            edges.append(dict(source=0, target=i, label='IS_SIMILAR'))

    return html, nodes, edges