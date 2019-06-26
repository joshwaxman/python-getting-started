import os
#from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph
from py2neo.data import walk

driver = None
session = None

def getClarkFullList():
    g = Graph("bolt://172.104.219.113:7687", auth=("neo4j", "qwerty"))
    html = '<h1>Full shoresh list</h1>'
    data = g.run('MATCH (n:ClarkShoresh) RETURN n ORDER by n.root').data()
    for node in data:
        root = node['n']['root']
        html += '<a href="' + root + '"</a>' + root + '\n<br/>'

    return html, [], []

def getClarkShoresh(shoresh: str):
    d = dict()
    g = Graph("bolt://172.104.219.113:7687", auth=("neo4j", "qwerty"))
    #/ browser /:24780 / db / data /
    html = ''

    p = g.nodes.match('ClarkShoresh', root=shoresh)
    if len(p) == 0:
        return

    # for now, only process first one
    p = p.first()
    html += 'Shoresh: ' + p['root'] + '<br/>'
    html += 'Meaning: ' + p['meaning'] + '<br/>'

    nodes = []
    key = p['root'] + ';' + p['meaning']
    nodeDict = dict()
    nodeDict[key] = 0
    nodes.append(dict(root=p['root'], meaning=p['meaning']))

    rels = g.match(nodes=[p, None], r_type='MEMBER_OF')
    phonemic_classes = set()
    edges = []
    if len(rels) > 0:
        html += '<br/><b>Phonemic Classes:</b><br/>'
        for i, rel in enumerate(rels, 1):
            pc = rel.end_node
            #n.append(teacher)

            #html += 'Phonemic class: <a href="' + pc['name'] + '">' + pc['group'] + '</a><br/>'
            html += 'Phonemic class: <a href="' + pc['name'] + '">' + pc['name'] + '</a><br/>'
            phonemic_classes.add(pc)
            n = dict(name=pc['name'], group=pc['group'])
            nodes.append(n)
            key = n['name'] + ';' + n['group']
            nodeDict[key] = i
            edges.append(dict(source=0, target=i, label='MEMBER_OF'))


    for pc in phonemic_classes:
        key = pc['name'] + ';' + pc['group']
        toIndex = nodeDict[key]
        rels = g.match([None, pc], r_type='MEMBER_OF')
        for i, rel in enumerate(rels, 1):
            s = rel.start_node
            #n.append(teacher)
            key = s['root'] + ';' + s['meaning']
            if key in nodeDict.keys():
                fromIndex = nodeDict[key]
            else:
                n = dict(root=s['root'], meaning=s['meaning'])
                nodes.append(n)
                fromIndex = len(nodes) - 1
                nodeDict[key] = fromIndex

            edges.append(dict(source=fromIndex, target=toIndex, label='MEMBER_OF'))

    return html, nodes, edges