import os
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph
driver = None
session = None

def makeNeoConnection():
    global driver
    global session

    if os.name == 'nt':
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "qwerty"))
    else:
        driver = GraphDatabase.driver("bolt://hobby-jhedjehadkjfgbkeaajelfal.dbs.graphenedb.com:24786", auth=basic_auth("mivami", "b.hsh2OnrThi0v.aPpsVUFV5tjE7dzw"))
    session = driver.session()

    # driver = GraphDatabase.driver("bolt://hobby-iamlocehkkokgbkekbgcgbal.dbs.graphenedb.com:24786",
    #                              auth=basic_auth("mivami", "b.jOGYTThIm49J.NCgtoqGY0qrXXajq"))

    #driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "qwerty"))


def getBiography(person: str):
    d = dict()
    g = Graph("https://hobby-jhedjehadkjfgbkeaajelfal.dbs.graphenedb.com:24780/db/data/", auth=("mivami", "b.jOGYTThIm49J.NCgtoqGY0qrXXajq"))

    p = g.nodes.match('EncodedRabbi', englishName=person)
    if len(p) > 0:
        # for now, only process first one
        p = p.first()
        d['englishName'] = p['englishName']
        d['hebrewName'] = p['hebrewName']
        d['generation'] = p['generation']
        d['sex'] = p['sex']

    else:
        return

    html = ''
    html += 'English Name: ' + d['englishName'] + '<br/>'
    html += 'Hebrew Name: ' + d['hebrewName'] + '<br/>'
    html += 'Generation: ' + d['generation'] + '<br/>'

    rels = g.match(nodes=[p], r_type='student')

    if len(rels) > 0:
        html += 'Teachers: <br/>'
        for rel in rels:
            teacher = rel.start_node

            html += 'English Name: ' + teacher['englishName'] + '<br/>'
            html += 'Hebrew Name: ' + teacher['hebrewName'] + '<br/>'
            html += 'Generation: ' + teacher['generation'] + '<br/><br/>'

    return html