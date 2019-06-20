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
    if len(rels) > 0:
        html += '<br/><b>Phonemic Classes:</b><br/>'
        for rel in rels:
            pc = rel.end_node
            #n.append(teacher)

            #html += 'Phonemic class: <a href="' + pc['name'] + '">' + pc['group'] + '</a><br/>'
            html += 'Phonemic class: <a href="' + pc['name'] + '">' + pc['name'] + '</a><br/>'

            n = dict(name=pc['name'], group=pc['group'])
            nodes.append(n)

    edges = []

    return html, nodes, edges