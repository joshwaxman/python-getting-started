#from django.contrib.gis.geoip2 import GeoIP2
from hello.Statement import Statement
from pymongo import MongoClient
import datetime
from neo4j.v1 import GraphDatabase, basic_auth
driver = GraphDatabase.driver("bolt://hobby-iamlocehkkokgbkekbgcgbal.dbs.graphenedb.com:24786",
                              auth=basic_auth("mivami", "b.jOGYTThIm49J.NCgtoqGY0qrXXajq"))

session = driver.session()

from typing import List
def findGlobalRelationships(people: List[str]):
    peopleTuple = tuple(sorted(people))
    if peopleTuple in findGlobalRelationships.cache:
        return findGlobalRelationships.cache[peopleTuple]

    edgesOriginal = []  # type: List[Dict[str, str]]
    relationDict = {}
    nodesById = dict()

    # get the nodes, and specifically the node ids, of all of the computed rabbis
    # we have passed in

    query = 'match (r1:ComputedRabbi) where r1.name in ' + str(people) + ' return r1'
    result = session.run(query)

    for record in result:
        nodeId = record['r1'].id
        englishName = record['r1']['name']
        nodesById[nodeId] = {'name': englishName, 'appears': "True"}

    if len(people) > 1: # it takes at least two to tango. else no relationships to find.
        # now include rabbis who have global paths from one to the other
        query = 'match (r1:ComputedRabbi) where r1.name in ' + str(people) + '\n' + \
                'match (r2:ComputedRabbi) where r2.name in ' + str(people) + '\n' + \
                "match path = (r1)-[relationship2 { daf: 'global'}]-(r2)" + '\n' + \
                'return path, relationship2, r1, r2'

        result = session.run(query)

        for record in result:
            # already added r1 and r2 to nodes, so need not add them
            # do however add the relationship
            source = record['relationship2'].start
            target = record['relationship2'].end
            relationDict = dict()
            relationDict['source'] = source
            relationDict['target'] = target
            relationDict['type'] = record['relationship2'].type
            edgesOriginal.append(relationDict)

        # now include rabbis who share an indirect connection
        query = 'match (r1:ComputedRabbi) where r1.name in ' + str(people) + '\n' + \
                'match (r2:ComputedRabbi) where id(r1) <> id(r2) and r2.name in ' + str(people) + '\n' + \
                'match (r3:ComputedRabbi) where not r3.name in ' + str(people) + '\n' + \
                'match path = (r1)-[relationship1:student]-(r3)-[relationship2: student]-(r2)' + '\n' + \
                'return distinct path, relationship1, relationship2, r1, r2, r3'

        result = session.run(query)

        for record in result:
            # add the additional rabbi
            nodeId = record['r3'].id
            englishName = record['r3']['name']

            nodesById[nodeId] = {'name': englishName, 'appears': "False"}

            source = record['relationship1'].start
            target = record['relationship1'].end
            relationDict = dict()
            relationDict['source'] = source
            relationDict['target'] = target
            relationDict['type'] = record['relationship1'].type
            edgesOriginal.append(relationDict)

            source = record['relationship2'].start
            target = record['relationship2'].end
            relationDict = dict()
            relationDict['source'] = source
            relationDict['target'] = target
            relationDict['type'] = record['relationship2'].type
            edgesOriginal.append(relationDict)

    # add list position to nodesById
    nodes = []
    for i, nodeId in enumerate(nodesById.keys()):
        nodesById[nodeId]['id'] = i
        nodes.append(nodesById[nodeId])

    # update edges to be by position
    edges = []  # type: List[Dict[str, str]]

    setSourceTargetType = set()

    for d in edgesOriginal:
        source = nodesById[d['source']]['id']
        target = nodesById[d['target']]['id']
        type = d['type']
        if (source, target, type) not in setSourceTargetType:
            element = {'source': source,
                       'target': target,
                       'label': type}
            edges.append(element)
            setSourceTargetType.add((source, target, type))

    findGlobalRelationships.cache[peopleTuple] = edges, nodes
    return edges, nodes
findGlobalRelationships.cache = dict() # type: Dict[Tuple, Tuple]


def findStudentRelationships(people):
    peopleTuple = tuple(sorted(people))
    if peopleTuple in findStudentRelationships.cache:
        return findStudentRelationships.cache[peopleTuple]

    edgesOriginal = []  # type: List[Dict[str, str]]
    relationDict = {}
    nodesById = dict()

    # include solitary rabbis
    # so far, only have rabbis if there was a relationship between them
    # also include solitary rabbis

    query = 'match (r1:EncodedRabbi) where r1.englishName in ' + str(people) + "\n" \
                                                                               'return r1'

    result = session.run(query)

    for record in result:
        nodeId = record['r1'].id
        hebrewName = record['r1']['hebrewName']
        englishName = record['r1']['englishName']
        generation = record['r1']['generation']

        nodesById[nodeId] = {'name': englishName, 'hebrewName': hebrewName, 'generation': generation, 'appears': "True"}

    # now include rabbis who have paths
    query = 'match (r1:EncodedRabbi) where r1.englishName in ' + str(people) + '\n' + \
            'match (r2:EncodedRabbi) where r2.englishName in ' + str(people) + '\n' + \
            'match path = (r1)-[relationship2:student]-(r2)' + '\n' + \
            'return path, relationship2, r1, r2'

    result = session.run(query)

    for record in result:
        # already added r1 and r2 to nodes, so need not add them
        # do however add the relationship
        source = record['relationship2'].start
        target = record['relationship2'].end
        relationDict = dict()
        relationDict['source'] = source
        relationDict['target'] = target
        relationDict['type'] = record['relationship2'].type
        edgesOriginal.append(relationDict)

    # now include rabbis who share a teacher
    query = 'match (r1:EncodedRabbi) where r1.englishName in ' + str(people) + '\n' + \
            'match (r2:EncodedRabbi) where id(r1) <> id(r2) and r2.englishName in ' + str(people) + '\n' + \
            'match (r3:EncodedRabbi) where not r3.englishName in ' + str(people) + '\n' + \
            'match path = (r1)-[relationship1:student]->(r3)<-[relationship2: student]-(r2)' + '\n' + \
            'return distinct path, relationship1, relationship2, r1, r2, r3'

    result = session.run(query)

    for record in result:
        # add the additional rabbi
        nodeId = record['r3'].id
        hebrewName = record['r3']['hebrewName']
        englishName = record['r3']['englishName']
        generation = record['r3']['generation']

        nodesById[nodeId] = {'name': englishName, 'hebrewName': hebrewName, 'generation': generation, 'appears': "False"}

        r1English = record['r1']['englishName']
        r2English = record['r2']['englishName']

        source = record['relationship1'].start
        target = record['relationship1'].end
        relationDict = dict()
        relationDict['source'] = source
        relationDict['target'] = target
        relationDict['type'] = record['relationship1'].type
        edgesOriginal.append(relationDict)

        source = record['relationship2'].start
        target = record['relationship2'].end
        relationDict = dict()
        relationDict['source'] = source
        relationDict['target'] = target
        relationDict['type'] = record['relationship2'].type
        edgesOriginal.append(relationDict)

    # add list position to nodesById
    nodes = []
    for i, nodeId in enumerate(nodesById.keys()):
        nodesById[nodeId]['id'] = i
        nodes.append(nodesById[nodeId])

    # update edges to be by position
    edges = []  # type: List[Dict[str, str]]

    setSourceTargetType = set()

    for d in edgesOriginal:
        source = nodesById[d['source']]['id']
        target = nodesById[d['target']]['id']
        type = d['type']
        if (source, target, type) not in setSourceTargetType:
            element = {'source': source,
                       'target': target,
                       'label': type}
            edges.append(element)
            setSourceTargetType.add((source, target, type))

    findStudentRelationships.cache[peopleTuple] = edges, nodes
    return edges, nodes

findStudentRelationships.cache = dict() # type: Dict[Tuple, Tupe]

from typing import List, Set, Dict, Any
def graphTransformation(edges: List[Dict[str, Any]], nodes: Set[str]):
    # the transformation in question is that nodes are
    # strings such as 'Rabbi Meir', rather than numbers,
    # and these are also the source / target values of
    # the edges.

    nodes = list(nodes)
    nodesByName = {name : id for id, name in enumerate(nodes)}
    nodesById = {id: name for id, name in enumerate(nodes)}

    nodes = [{'name': name} for name in nodes]

    edges2 = []
    for edge in edges:
        if edge['target'] != '' and edge['source'] != 0:
            edges2.append({'source': nodesByName[edge['source']],
                            'target': nodesByName[edge['target']],
                            'label': edge['label']})
    edges = edges2

    return edges, nodes

def graphTransformation2(edges: List[Dict[str, Any]], nodes: Dict[str, str]):
    # the transformation in question is that nodes are
    # strings such as 'Rabbi Meir', rather than numbers,
    # and these are also the source / target values of
    # the edges.

    nodes = list(nodes)
    nodesByName = {name : id for id, name in enumerate(nodes)}
    nodesById = {id: name for id, name in enumerate(nodes)}

    nodes = [{'name': name} for name in nodes]
    edges = [{'source': nodesByName[edge['source']],
              'target': nodesByName[edge['target']],
              'label': edge['label']
              } for edge in edges]

    return edges, nodes




def getDafYomi():
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    dafyomi = db.dafyomi
    now = datetime.datetime.now()
    theDate = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
    theDaf = {'date': theDate }
    x = dafyomi.find_one(theDaf)['daf'].split()
    masechet = x[0]
    daf = x[1] + 'a'
    return masechet, daf


def htmlOutputter(title: str, page: str):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    mivami = db.mivami

    if page.endswith('b'):
        prevPage = page[:-1] + 'a'
        nextPage = str((int(page[:-1]))+1) + 'a'
    else:
        prevPage = str((int(page[:-1]))-1) + 'b'
        nextPage = page[:-1] + 'b'
    wrapper = '<a href="/talmud/' + title + '.' + prevPage + '">Previous</a> | ' + \
              '<a href="/talmud/' + title + '.' + nextPage + '">Next</a> | '

    amud = page[-1]
    daf_start = (int(page[:-1]) - 2) * 2
    if amud == 'b':
        daf_start += 1

    daf = daf_start

    theText = {'title': title + ":" + str(daf)}
    theText = list(mivami.find(theText))

    item = theText[0]
    contents = item['contents']
    student_nodes = item['EncodedNodes']

    if 'EncodedEdges' in item: # already computed for this daf
        student_edges = item['EncodedEdges']
    else: # compute for the first time
        allRabbis = [item['name'] for item in student_nodes]
        student_edges, student_nodes = findStudentRelationships(allRabbis)
        mivami.update_one({'title': title + ":" + str(daf)},
                          {'$set':
                               {'EncodedNodes': student_nodes,
                                'EncodedEdges': student_edges}
                           }, upsert=True)

        # write the edges out so that it does not need to be computed a second time

    #student_edges = item['EncodedEdges']
    local_interaction_nodes = item['LocalInteractionNodes']
    local_interaction_edges = item['LocalInteractionEdges']
    if 'GlobalInteractionNodes' in theText[0]:
        global_interaction_nodes = item['GlobalInteractionNodes']
        global_interaction_edges = item['GlobalInteractionEdges']
    else:
        global_interaction_nodes = local_interaction_nodes
        global_interaction_edges, global_interaction_nodes = findGlobalRelationships(global_interaction_nodes)
        mivami.update_one({'title': title+":"+str(daf)}, {'$set': {'GlobalInteractionNodes': global_interaction_nodes, 'GlobalInteractionEdges': global_interaction_edges}})

    wrapper += '<a href="https://www.sefaria.org/%s?lang=bi">%s</a></p>' % (title + '.' +str(page), title+" "+str(page)) #Pesachim.7b, Pesachim 7b

    # iterate through sugyot,
    # so that we have different graphs
    sugya = 0
    sugyaGraphs = []
    pplSet = set()

    for line in contents: # type: Dict[str, Any]
        #eng, heb = line['eng'], line['heb'] # type: str, str
        html = line['html']

        wrapper += html

    # fix up tags like < strong >
    wrapper = wrapper.replace('< ', '<')
    wrapper = wrapper.replace(' >', '>')

    leftside = wrapper

    # why was this not precomputed?
    local_interaction_edges, local_interaction_nodes = graphTransformation(local_interaction_edges, local_interaction_nodes)
    #student_edges, student_nodes = graphTransformation(student_edges, student_nodes)

    return leftside, student_edges, student_nodes, local_interaction_edges, local_interaction_nodes, \
           global_interaction_edges, global_interaction_nodes
