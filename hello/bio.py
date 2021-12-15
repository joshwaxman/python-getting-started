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


def getBiography(person: str):
    d = dict()
    #g = Graph("https://hobby-jhedjehadkjfgbkeaajelfal.dbs.graphenedb.com:24780/db/data/", auth=("mivami", "b.jOGYTThIm49J.NCgtoqGY0qrXXajq"))
    # g = Graph("https://172.104.217.202:7473", auth=("neo4j", "qwerty"))
    g = Graph("neo4j+s://47351056.databases.neo4j.io", auth=("neo4j", "Yw05tVDOK7C0kKyczhkI20UyY_l2VBWTogn0JNNlP7Y"))

    html = ''

    p = g.nodes.match('EncodedRabbi', englishName=person)
    if len(p) == 0:
        return

    # for now, only process first one
    p = p.first()
    html += 'English Name: ' + p['englishName'] + '<br/>'
    html += 'Hebrew Name: ' + p['hebrewName'] + '<br/>'
    html += 'Generation: ' + p['generation'] + '<br/>'

    nodes = []
    no = set(p)
    nodes.append(dict(name=p['englishName'], hebrewName=p['hebrewName'], generation=p['generation']))

    rels = g.match(nodes=[p, None], r_type='student')
    if len(rels) > 0:
        html += '<br/><b>Teachers:</b><br/>'
        for rel in rels:
            teacher = rel.end_node
            #n.append(teacher)

            html += 'English Name: <a href="' + teacher['englishName'] + '">' + teacher['englishName'] + '</a><br/>'
            html += 'Hebrew Name: ' + teacher['hebrewName'] + '<br/>'
            html += 'Generation: ' + teacher['generation'] + '<br/><br/>'

            n = dict(name=teacher['englishName'], hebrewName=teacher['hebrewName'], generation=teacher['generation'])
            nodes.append(n)

    rels = g.match(nodes=[None, p], r_type='student')
    if len(rels) > 0:
        html += '<br/><b>Students:</b><br/>'
        for rel in rels:
            student = rel.start_node

            html += 'English Name: <a href="' + student['englishName'] + '">' + student['englishName'] + '</a><br/>'
            html += 'Hebrew Name: ' + student['hebrewName'] + '<br/>'
            html += 'Generation: ' + student['generation'] + '<br/><br/>'

            n = dict(name=student['englishName'], hebrewName=student['hebrewName'], generation=student['generation'])
            nodes.append(n)

    names = [x['name'] for x in nodes]
    cursor = g.run('MATCH (r1: EncodedRabbi) where r1.englishName in ' + str(names) + '\n' +
                   'MATCH (r2: EncodedRabbi) where r2.englishName in ' + str(names) + '\n' +
                   'MATCH (r1)-[rel]->(r2)\n' +
                   'return rel')

    edges = []
    while cursor.forward():
        rel = cursor.current['rel']
        start = names.index(rel.start_node['englishName'])
        end = names.index(rel.end_node['englishName'])
        title = type(rel).__name__
        edges.append(dict(source=start, target=end, label=title))

    #rels = g.match(nodes=[None, p], r_type='student')

    return html, nodes, edges