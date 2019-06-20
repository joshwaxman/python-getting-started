import os
#from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph
from py2neo.data import walk
driver = None
session = None

# def makeNeoConnection():
#     global driver
#     global session
#
#     if os.name == 'nt':
#         driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "qwerty"))
#     else:
#         driver = GraphDatabase.driver("bolt://hobby-jhedjehadkjfgbkeaajelfal.dbs.graphenedb.com:24786", auth=basic_auth("mivami", "b.hsh2OnrThi0v.aPpsVUFV5tjE7dzw"))
#     session = driver.session()
#
#     # driver = GraphDatabase.driver("bolt://hobby-iamlocehkkokgbkekbgcgbal.dbs.graphenedb.com:24786",
#     #                              auth=basic_auth("mivami", "b.jOGYTThIm49J.NCgtoqGY0qrXXajq"))
#
#     #driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "qwerty"))


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
    no = set(p)
    nodes.append(dict(root=p['root'], meaning=p['meaning']))

    rels = g.match(nodes=[p, None], r_type='MEMBER_OF')
    phonemic_classes = set()
    edges = []
    if len(rels) > 0:
        html += '<br/><b>Phonemic Classes:</b><br/>'
        for i, rel in enumerate(1, rels):
            pc = rel.end_node
            #n.append(teacher)

            #html += 'Phonemic class: <a href="' + pc['name'] + '">' + pc['group'] + '</a><br/>'
            html += 'Phonemic class: <a href="' + pc['name'] + '">' + pc['name'] + '</a><br/>'
            phonemic_classes.add(pc['name'])
            n = dict(name=pc['name'], group=pc['group'])
            nodes.append(n)
            edges.append(dict(source=0, target=i, label='MEMBER_OF'))

    for pc in phonemic_classes:
        p = g.nodes.match('ClarkPhonemicClass', name=pc)
        rels = g.match(nodes=[p, None], r_type='MEMBER_OF')
        for i, rel in enumerate(1, rels):
            s = rel.end_node
            #n.append(teacher)

            n = dict(root=pc['root'], meaning=pc['meaning'])
            nodes.append(n)

    return html, nodes, edges