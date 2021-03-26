#from django.contrib.gis.geoip2 import GeoIP2
from pymongo import MongoClient
import datetime
from django.utils import timezone
from collections import defaultdict
from neo4j.v1 import GraphDatabase, basic_auth
import os

# paid connection string
driver = None
session = None

def makeNeoConnection():
    global driver
    global session

    if os.name == 'nt':
        driver = GraphDatabase.driver("bolt://localhost:11002", auth=basic_auth("neo4j", "qwerty"))
    else:
        driver = GraphDatabase.driver("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))

        #driver = GraphDatabase.driver("bolt://hobby-iamlocehkkokgbkekbgcgbal.dbs.graphenedb.com:24786",
        #                              auth=basic_auth("mivami", "b.hsh2OnrThi0v.aPpsVUFV5tjE7dzw"))

    session = driver.session()

    # driver = GraphDatabase.driver("bolt://hobby-iamlocehkkokgbkekbgcgbal.dbs.graphenedb.com:24786",
    #                              auth=basic_auth("mivami", "b.jOGYTThIm49J.NCgtoqGY0qrXXajq"))

    #driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "qwerty"))


from typing import List

def findLocalRelationships(people: List[str], daf: str):
    makeNeoConnection()
    edgesOriginal = []  # type: List[Dict[str, str]]
    relationDict = {}
    nodesById = dict()
    foundPeople = set()

    dPeople = {t[0]: (t[1], t[2]) for t in people}
    people = [t[0] for t in people]
    people = set(people)

    query = 'match (r1:ComputedRabbi)-[rel]-(r2:ComputedRabbi) where rel.daf = "' + daf + '" return r1, r2, rel'

    result = session.run(query)
    #h = query
    count = 0
    for record in result:
        nodeId = record['r1'].id
        englishName = record['r1']['name']
        generation = record['r1']['generation']
        foundPeople.add(englishName)
        if generation is None:
            generation = '?';
        nodesById[nodeId] = {'name': englishName, 'appears': "True", 'generation': generation}

        nodeId = record['r2'].id
        englishName = record['r2']['name']
        generation = record['r2']['generation']
        foundPeople.add(englishName)
        if generation is None:
            generation = '?';
        nodesById[nodeId] = {'name': englishName, 'appears': "True", 'generation': generation}

        count += 1
        source = record['rel'].start
        target = record['rel'].end
        relationDict = dict()
        relationDict['source'] = source
        relationDict['target'] = target
        relationDict['type'] = record['rel'].type
        edgesOriginal.append(relationDict)

    # add list position to nodesById
    nodes = []
    for i, nodeId in enumerate(nodesById.keys()):
        nodesById[nodeId]['id'] = i
        nodes.append(nodesById[nodeId])

    # add people from this page who don't have
    # relationships, passed in
    pos = len(nodes) # so no overlap in item number
    for person in people:
        #h += person + "|"
        if person not in foundPeople:
            generation = dPeople[person][0]
            if generation is None:
                generation = '?';
            nodes.append({'name': person, 'generation': generation, 'appears': 'True'})
    # update edges to be by position
    edges = []  # type: List[Dict[str, str]]

    setSourceTargetType = set()

    edgeDict = defaultdict(set)

    for d in edgesOriginal:
        source = nodesById[d['source']]['id']
        target = nodesById[d['target']]['id']
        type = d['type']
        edgeDict[(source, target)].add(type)

    for (source, target), type in edgeDict.items():
        element = {'source': source,
                   'target': target,
                   'label': ', '.join(type)}
        edges.append(element)

    #h += str(count)
    #h += str(foundPeople)
    return edges, nodes


def findGlobalRelationships(people: List[str]):
    people = [t[0] for t in people]
    people = list(set(people))
    peopleTuple = tuple(sorted(people))
    if peopleTuple in findGlobalRelationships.cache:
        return findGlobalRelationships.cache[peopleTuple]

    edgesOriginal = []  # type: List[Dict[str, str]]
    relationDict = {}
    nodesById = dict()

    makeNeoConnection()

    #f = open('logfile.log', 'a')

    # get the nodes, and specifically the node ids, of all of the computed rabbis
    # we have passed in

    query = 'match (r1:ComputedRabbi) where r1.name in ' + str(people) + ' return r1'
    #print(query, file=f)
    result = session.run(query)

    for record in result:
        nodeId = record['r1'].id
        englishName = record['r1']['name']
        generation = record['r1']['generation']

        if generation is None:
            generation = '?';

        nodesById[nodeId] = {'name': englishName, 'appears': "True", 'generation': generation}

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

    edgeDict = defaultdict(set)
    for d in edgesOriginal:
        source = nodesById[d['source']]['id']
        target = nodesById[d['target']]['id']
        type = d['type']
        edgeDict[(source, target)].add(type)

    for (source, target), type in edgeDict.items():
        element = {'source': source,
                   'target': target,
                   'label': ', '.join(type)}
        edges.append(element)


    # for d in edgesOriginal:
    #     source = nodesById[d['source']]['id']
    #     target = nodesById[d['target']]['id']
    #     type = d['type']
    #     if (source, target, type) not in setSourceTargetType:
    #         element = {'source': source,
    #                    'target': target,
    #                    'label': type}
    #         edges.append(element)
    #         setSourceTargetType.add((source, target, type))

    findGlobalRelationships.cache[peopleTuple] = edges, nodes

    return edges, nodes
findGlobalRelationships.cache = dict() # type: Dict[Tuple, Tuple]


def findStudentRelationships(people):
    people = [t[0] for t in people]
    peopleTuple = tuple(sorted(people))
    #if peopleTuple in findStudentRelationships.cache:
#        return findStudentRelationships.cache[peopleTuple]

    makeNeoConnection()

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

        if generation is None:
            generation = '?'

        nodesById[nodeId] = {'name': englishName, 'hebrewName': hebrewName, 'generation': generation, 'appears': "True"}

    # now include rabbis who have paths between each other
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

    # now include teachers shared by two rabbi
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

        if generation is None:
            generation = '?';

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
    edges = [{'source': nodesByName[edge['source']],
              'target': nodesByName[edge['target']],
              'label': edge['label']
              } for edge in edges]

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
    #now = datetime.datetime.now()
    now = timezone.now()
    theDate = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
    theDaf = {'date': theDate }
    x = dafyomi.find_one(theDaf)['daf'].split()
    masechet = x[0]
    if masechet == 'Hullin':
        masechet = 'Chullin'
    elif masechet == 'Bechorot':
        masechet = 'Bekhorot'
    elif masechet == 'Arachin':
        masechet = 'Arakhin'
    elif masechet == 'Eiruvin':
        masechet = 'Eruvin'
    elif masechet.startswith('Talmud Yerushalmi '):
        masechet = masechet.removeprefix('Talmud Yerushalmi ')

    if masechet == "Jerusalem":
        masechet =  "Shekalim"
        daf = x[3] + 'a'
    else:
        daf = x[1] + 'a'

    return masechet, daf

def getTalmudNavigation():
    masechtot = ['Berakhot', 'Shabbat', 'Eruvin', 'Pesachim', 'Rosh Hashanah', 'Yoma', 'Sukkah',
                 'Beitzah', 'Taanit', 'Megillah', 'Moed Katan', 'Chagigah', 'Yevamot', 'Ketubot',
                 'Nedarim', 'Nazir', 'Sotah', 'Gittin', 'Kiddushin', 'Bava Kamma', 'Bava Metzia',
                 'Bava Batra', 'Sanhedrin', 'Makkot', 'Shevuot', 'Avodah Zarah', 'Horayot',
                 'Zevachim', 'Menachot', 'Chullin', 'Bekhorot', 'Arakhin', 'Temurah', 'Keritot',
                 'Meilah', 'Tamid', 'Niddah']

    html = ''
    for masechet in masechtot:
        html += "<a href='" + masechet + "'>" + masechet + '</a><br/>'

    return html

def getTalmudPageNavigation(masechet: str):
    masechtot = ['Berakhot', 'Shabbat', 'Eruvin', 'Pesachim', 'Rosh Hashanah', 'Yoma', 'Sukkah',
                 'Beitzah', 'Taanit', 'Megillah', 'Moed Katan', 'Chagigah', 'Yevamot', 'Ketubot',
                 'Nedarim', 'Nazir', 'Sotah', 'Gittin', 'Kiddushin', 'Bava Kamma', 'Bava Metzia',
                 'Bava Batra', 'Sanhedrin', 'Makkot', 'Shevuot', 'Avodah Zarah', 'Horayot',
                 'Zevachim', 'Menachot', 'Chullin', 'Bekhorot', 'Arakhin', 'Temurah', 'Keritot',
                 'Meilah', 'Tamid', 'Niddah']

    chapter_structures = {'Berakhot': [(2, 'a', 13, 'a'), (13, 'a', 17, 'b'), (17, 'b', 26, 'a'), (26, 'a', 30, 'b'), (30, 'b', 34, 'b'), (35, 'a', 45, 'a'), (45, 'a', 51, 'b'), (51, 'b', 53, 'b'), (54, 'a', 64, 'a')], 'Shabbat': [(2, 'a', 20, 'b'), (20, 'b', 36, 'b'), (36, 'b', 47, 'b'), (47, 'b', 51, 'b'), (51, 'b', 56, 'b'), (57, 'a', 67, 'b'), (67, 'b', 76, 'b'), (76, 'b', 82, 'a'), (82, 'a', 90, 'b'), (90, 'b', 96, 'a'), (96, 'a', 102, 'a'), (102, 'b', 105, 'a'), (105, 'a', 107, 'a'), (107, 'a', 111, 'b'), (111, 'b', 115, 'a'), (115, 'a', 122, 'b'), (122, 'b', 126, 'b'), (126, 'b', 129, 'b'), (130, 'a', 137, 'b'), (137, 'b', 141, 'b'), (141, 'b', 143, 'a'), (143, 'b', 148, 'a'), (148, 'a', 153, 'a'), (153, 'a', 157, 'b')], 'Eruvin': [(2, 'a', 17, 'b'), (17, 'b', 26, 'b'), (26, 'b', 41, 'b'), (41, 'b', 52, 'b'), (52, 'b', 61, 'b'), (61, 'b', 76, 'a'), (76, 'a', 82, 'a'), (82, 'a', 89, 'a'), (89, 'a', 95, 'a'), (95, 'a', 105, 'a')], 'Pesachim': [(2, 'a', 21, 'a'), (21, 'a', 42, 'a'), (42, 'a', 50, 'a'), (50, 'a', 57, 'b'), (58, 'a', 65, 'b'), (65, 'b', 73, 'b'), (74, 'a', 86, 'b'), (87, 'a', 92, 'b'), (92, 'b', 99, 'a'), (99, 'b', 121, 'b')], 'Rosh Hashanah': [(2, 'a', 22, 'a'), (22, 'a', 25, 'b'), (25, 'b', 29, 'b'), (29, 'b', 35, 'a')], 'Yoma': [(2, 'a', 21, 'b'), (22, 'a', 28, 'a'), (28, 'a', 39, 'a'), (39, 'a', 46, 'b'), (47, 'a', 62, 'a'), (62, 'a', 68, 'b'), (68, 'b', 73, 'b'), (73, 'b', 88, 'a')], 'Sukkah': [(2, 'a', 20, 'b'), (20, 'b', 29, 'b'), (29, 'b', 42, 'b'), (42, 'b', 50, 'a'), (50, 'a', 56, 'b')], 'Beitzah': [(2, 'a', 15, 'a'), (15, 'b', 23, 'b'), (23, 'b', 29, 'b'), (29, 'b', 35, 'b'), (35, 'b', 40, 'b')], 'Taanit': [(2, 'a', 15, 'a'), (15, 'a', 18, 'b'), (18, 'b', 26, 'a'), (26, 'a', 31, 'a')], 'Megillah': [(2, 'a', 17, 'a'), (17, 'a', 21, 'a'), (21, 'a', 25, 'b'), (25, 'b', 32, 'a')], 'Moed Katan': [(2, 'a', 11, 'a'), (11, 'b', 13, 'b'), (13, 'b', 29, 'a')], 'Chagigah': [(2, 'a', 11, 'b'), (11, 'b', 20, 'b'), (20, 'b', 27, 'a')], 'Yevamot': [(2, 'a', 17, 'a'), (17, 'a', 26, 'a'), (26, 'a', 35, 'a'), (35, 'b', 50, 'a'), (50, 'a', 53, 'b'), (53, 'b', 66, 'a'), (66, 'a', 70, 'a'), (70, 'a', 84, 'a'), (84, 'a', 87, 'b'), (87, 'b', 97, 'a'), (97, 'a', 101, 'a'), (101, 'a', 106, 'b'), (107, 'a', 112, 'b'), (112, 'b', 114, 'b'), (114, 'b', 118, 'b'), (119, 'a', 122, 'b')], 'Ketubot': [(2, 'a', 15, 'b'), (15, 'b', 28, 'b'), (29, 'a', 41, 'b'), (41, 'b', 54, 'b'), (54, 'b', 65, 'b'), (65, 'b', 70, 'a'), (70, 'a', 77, 'b'), (78, 'a', 82, 'b'), (83, 'a', 90, 'a'), (90, 'a', 95, 'b'), (95, 'b', 101, 'b'), (101, 'b', 104, 'b'), (104, 'b', 112, 'b')], 'Nedarim': [(2, 'a', 13, 'b'), (13, 'b', 20, 'b'), (20, 'b', 32, 'b'), (32, 'b', 45, 'a'), (45, 'b', 48, 'b'), (49, 'a', 53, 'b'), (54, 'a', 60, 'a'), (60, 'a', 63, 'b'), (64, 'a', 66, 'b'), (66, 'b', 79, 'a'), (79, 'a', 91, 'b')], 'Nazir': [(2, 'a', 8, 'b'), (9, 'a', 16, 'a'), (16, 'a', 20, 'b'), (20, 'b', 30, 'b'), (30, 'b', 34, 'a'), (34, 'a', 47, 'a'), (47, 'a', 57, 'a'), (57, 'a', 61, 'a'), (61, 'a', 66, 'b')], 'Sotah': [(2, 'a', 14, 'a'), (14, 'a', 19, 'a'), (19, 'a', 23, 'b'), (23, 'b', 27, 'b'), (27, 'b', 31, 'a'), (31, 'a', 32, 'a'), (32, 'a', 42, 'a'), (42, 'a', 44, 'b'), (44, 'b', 49, 'b')], 'Gittin': [(2, 'a', 15, 'a'), (15, 'a', 24, 'a'), (24, 'a', 32, 'a'), (32, 'a', 48, 'b'), (48, 'b', 62, 'a'), (62, 'b', 67, 'b'), (67, 'b', 77, 'a'), (77, 'a', 82, 'a'), (82, 'a', 90, 'b')], 'Kiddushin': [(2, 'a', 41, 'a'), (41, 'a', 58, 'b'), (58, 'b', 69, 'a'), (69, 'a', 82, 'b')], 'Bava Kamma': [(2, 'a', 17, 'a'), (17, 'a', 27, 'a'), (27, 'a', 36, 'a'), (36, 'a', 46, 'a'), (46, 'a', 55, 'a'), (55, 'b', 62, 'b'), (62, 'b', 83, 'a'), (83, 'b', 93, 'a'), (93, 'b', 111, 'a'), (111, 'b', 119, 'b')], 'Bava Metzia': [(2, 'a', 21, 'a'), (21, 'a', 33, 'b'), (33, 'b', 44, 'a'), (44, 'a', 60, 'b'), (60, 'b', 75, 'b'), (75, 'b', 83, 'a'), (83, 'a', 94, 'a'), (94, 'a', 103, 'a'), (103, 'a', 116, 'a'), (116, 'b', 119, 'a')], 'Bava Batra': [(2, 'a', 17, 'a'), (17, 'a', 27, 'b'), (28, 'a', 60, 'b'), (61, 'a', 73, 'a'), (73, 'a', 91, 'b'), (92, 'a', 102, 'b'), (102, 'b', 108, 'a'), (108, 'a', 139, 'b'), (139, 'b', 159, 'b'), (160, 'a', 176, 'b')], 'Sanhedrin': [(2, 'a', 18, 'a'), (18, 'a', 22, 'b'), (23, 'a', 31, 'b'), (32, 'a', 39, 'b'), (40, 'a', 42, 'a'), (42, 'b', 49, 'a'), (49, 'b', 68, 'a'), (68, 'b', 75, 'a'), (75, 'a', 84, 'a'), (84, 'b', 90, 'a'), (90, 'a', 113, 'b')], 'Makkot': [(2, 'a', 7, 'a'), (7, 'a', 13, 'a'), (13, 'a', 24, 'b')], 'Shevuot': [(2, 'a', 14, 'a'), (14, 'a', 19, 'b'), (19, 'b', 29, 'b'), (30, 'a', 36, 'b'), (36, 'b', 38, 'b'), (38, 'b', 44, 'b'), (44, 'b', 49, 'a'), (49, 'a', 49, 'b')], 'Avodah Zarah': [(2, 'a', 22, 'a'), (22, 'a', 40, 'b'), (40, 'b', 49, 'b'), (49, 'b', 61, 'b'), (62, 'a', 76, 'b')], 'Horayot': [(2, 'a', 6, 'b'), (6, 'b', 9, 'b'), (9, 'b', 14, 'a')], 'Zevachim': [(2, 'a', 15, 'b'), (15, 'b', 31, 'b'), (31, 'b', 36, 'b'), (36, 'b', 47, 'a'), (47, 'a', 57, 'b'), (58, 'a', 66, 'a'), (66, 'a', 70, 'b'), (70, 'b', 83, 'a'), (83, 'a', 88, 'b'), (89, 'a', 92, 'a'), (92, 'a', 98, 'b'), (98, 'b', 106, 'a'), (106, 'a', 112, 'a'), (112, 'a', 120, 'b')], 'Menachot': [(2, 'a', 13, 'a'), (13, 'a', 17, 'a'), (17, 'a', 38, 'a'), (38, 'a', 52, 'b'), (52, 'b', 63, 'b'), (63, 'b', 72, 'b'), (72, 'b', 76, 'b'), (76, 'b', 83, 'b'), (83, 'b', 87, 'a'), (87, 'a', 94, 'a'), (94, 'a', 100, 'b'), (100, 'b', 104, 'b'), (104, 'b', 110, 'a')], 'Chullin': [(2, 'a', 26, 'b'), (27, 'a', 42, 'a'), (42, 'a', 67, 'b'), (68, 'a', 78, 'a'), (78, 'a', 83, 'b'), (83, 'b', 89, 'b'), (89, 'b', 103, 'b'), (103, 'b', 117, 'b'), (117, 'b', 129, 'b'), (130, 'a', 134, 'b'), (135, 'a', 138, 'b'), (138, 'b', 142, 'a')], 'Bekhorot': [(2, 'a', 13, 'a'), (13, 'a', 19, 'b'), (19, 'b', 26, 'b'), (26, 'b', 31, 'a'), (31, 'a', 37, 'a'), (37, 'a', 43, 'a'), (43, 'a', 46, 'a'), (46, 'a', 52, 'b'), (53, 'a', 61, 'a')], 'Meilah': [(2, 'a', 8, 'a'), (8, 'a', 10, 'b'), (10, 'b', 14, 'b'), (15, 'a', 18, 'a'), (18, 'a', 20, 'a'), (20, 'a', 22, 'a')], 'Tamid': [(25, 'b', 28, 'b'), (28, 'b', 30, 'a'), (30, 'a', 30, 'b'), (30, 'b', 32, 'b'), (32, 'b', 33, 'a'), (33, 'a', 33, 'a'), (33, 'b', 33, 'b')], 'Arakhin': [(2, 'a', 7, 'b'), (7, 'b', 13, 'b'), (13, 'b', 17, 'a'), (17, 'a', 19, 'a'), (19, 'a', 21, 'b'), (21, 'b', 24, 'a'), (24, 'a', 27, 'a'), (27, 'a', 29, 'a'), (29, 'b', 34, 'a')], 'Temurah': [(2, 'a', 13, 'b'), (14, 'a', 17, 'b'), (17, 'b', 21, 'b'), (21, 'b', 24, 'a'), (24, 'b', 27, 'b'), (28, 'a', 31, 'a'), (31, 'a', 34, 'a')], 'Keritot': [(2, 'a', 8, 'b'), (8, 'b', 11, 'b'), (11, 'b', 17, 'a'), (17, 'a', 20, 'b'), (20, 'b', 23, 'b'), (23, 'b', 28, 'b')], 'Niddah': [(2, 'a', 12, 'b'), (13, 'a', 21, 'a'), (21, 'a', 31, 'b'), (31, 'b', 39, 'b'), (40, 'a', 48, 'a'), (48, 'a', 54, 'b'), (54, 'b', 57, 'a'), (57, 'b', 59, 'a'), (59, 'b', 64, 'b'), (64, 'b', 73, 'a')]}

    html = ''

    chapter_structure = chapter_structures[masechet]

    html += masechet + '<br/>'

    def form_hyperlink(daf, amud):
        nonlocal html, num_elements, masechet
        page = str(daf) + amud
        html += '<td><a href="' + masechet + "." + page + '">' + page + '</a></td>'
        num_elements += 1
        if num_elements % 7 == 0: html += '</tr><tr>'

    for i, chapter in enumerate(chapter_structure, start=1):
        html += 'Chapter ' + str(i) + '<br/>'
        daf_start, amud_start, daf_end, amud_end = chapter

        html += '<table style="width:60%"><tr>'
        num_elements = 0

        if amud_start == 'b': #handle separately
            form_hyperlink(daf_start, amud_start)
            daf_start += 1

        for i in range(daf_start, daf_end):
            form_hyperlink(i, 'a')

        form_hyperlink(daf_end, 'a')
        if amud_end == 'b':
            form_hyperlink(daf_end, 'b')

        html += '</table><br/>'

    return html




def getTimeline(students):
    s = []
    genDict = {'T1': (-30, 20), 'T2': (40, 80), 'T3': (80, 110), 'T4': (110, 135), 'T5': (135, 170),
               'T6': (170, 200), 'TA': (200, 220),
                'A1': (220, 250), 'A2': (250, 290), 'A3': (290, 320), 'A4': (320, 350), 'A5': (350, 375), 'A6': (375, 425)}

    for student in students:
        d = dict()
        d['label'] = student['name']
        generation = student['generation']
        if generation in genDict.keys():
            t = genDict[generation]
            d['times'] = [{'starting_time': t[0], 'ending_time': t[1]}]
            d['generation'] = generation
            s.append(d)

    s.sort(key=lambda x : x['times'][0]['starting_time'])
    return s

def htmlOutputter(title: str, page: str):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    #client = MongoClient()
    db = client.sefaria
    mivami_html = db.mivami_stage_04_html
    mivami_persons = db.mivami_stage_03_persons
    mivami = db.mivami
    person = db.person
    time_period = db.time_period

    bCache = False
    if page.endswith('A') or page.endswith('B'):
        page = page.lower()
        bCache = False

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

    theText = {'title': title + ':' + str(daf)}
    item = mivami.find_one(theText)
    theHtml = mivami_html.find_one(theText)
    html = theHtml['html']
    html += ('<!––daf:' + str(daf) + '-->')
    h = '' # extra debugging output
    persons_collection = mivami_persons.find_one(theText)
    persons = [tuple(t) for t in persons_collection['person_in_daf']]
    persons_in_sugya = None
    try:
        persons_in_sugya = persons_collection['person_in_sugya']
    except:
        pass
#    html += str(persons)
    if False: #'EncodedEdges' in theHtml and 'EncodedNodes' in theHtml and bCache:
        # already generated and can pull it
        student_edges = theHtml['EncodedEdges']
        student_nodes = theHtml['EncodedNodes']
    else: # compute for the first time

        # must look up each person in the person table for full identity
        #people = list(person.find({'key': {'$in': persons}}))
        #people = [{'name': p['key'], 'generation': p['generation']} for p in people]

        student_nodes = persons
        student_edges, student_nodes = findStudentRelationships(student_nodes)
        # mivami_html.update_one({'title': title + ":" + str(daf)},
        #                   {'$set':
        #                        {'EncodedEdges': student_edges,
        #                         'EncodedNodes': student_nodes}
        #                    }, upsert=True)

        # write the edges out so that it does not need to be computed a second time

    #student_edges = item['EncodedEdges']

        local_interaction_edges, local_interaction_nodes = findLocalRelationships(persons, title + '.' + page)
#    local_interaction_nodes, local_interaction_edges = [], []

    # generate timeline
    # for now, for people, not statements
    timeline = getTimeline(student_nodes)

    if os.name == 'nt':
        html += 'Extra debugguing' + h  + '<br/>'
#     html += 'Local interaction Nodes: ' + str(local_interaction_nodes) + '</br>'
#     html += 'Local interaction Edges: ' + str(local_interaction_edges) + '</br>'
    #local_interaction_nodes = item['LocalInteractionNodes']
    #local_interaction_edges = item['LocalInteractionEdges']
    if 'GlobalInteractionNodes' in theText:
        global_interaction_nodes = item['GlobalInteractionNodes']
        global_interaction_edges = item['GlobalInteractionEdges']
    else:
        global_interaction_edges, global_interaction_nodes = findGlobalRelationships(persons)
        #mivami.update_one({'title': title+":"+str(daf)}, {'$set': {'GlobalInteractionNodes': global_interaction_nodes, 'GlobalInteractionEdges': global_interaction_edges}})

    wrapper += '<a href="https://www.sefaria.org/%s?lang=bi">%s</a></p>' % (title + '.' +str(page), title+" "+str(page))

    wrapper += html

    # fix up tags like < strong >
    wrapper = wrapper.replace('< ', '<')
    wrapper = wrapper.replace(' >', '>')

    leftside = wrapper

    # iterate through sugyot,
    # so that we have different graphs
    sugyaGraphs = dict()
    pplSet = set()
    if persons_in_sugya is not None:
        for i, sugya in enumerate(persons_in_sugya):
            line_start = sugya['line_start']
            sugya_number = sugya['sugya']
            people = sugya['people']
            e, n = findStudentRelationships(people)
            le, ln = findLocalRelationships(people, title + '.' + page)
            ge, gn = findGlobalRelationships(people)
            sugyaGraphs[i] = [e, n, le, ln, ge, gn]

    # why was this not precomputed?
    #local_interaction_edges, local_interaction_nodes = graphTransformation(local_interaction_edges, local_interaction_nodes)
    #student_edges, student_nodes = graphTransformation(student_edges, student_nodes)



    return leftside, student_edges, student_nodes, local_interaction_edges, local_interaction_nodes, \
           global_interaction_edges, global_interaction_nodes, sugyaGraphs, timeline


def generate_tzurat_hadaf(title: str, page: str):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    #client = MongoClient()
    db = client.sefaria
    mivami_html = db.mivami_stage_04_html
    mivami_persons = db.mivami_stage_03_persons
    mivami = db.mivami
    person = db.person
    time_period = db.time_period

    bCache = False
    if page.endswith('A') or page.endswith('B'):
        page = page.lower()
        bCache = False

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

    theText = {'title': title + ':' + str(daf)}
    item = mivami.find_one(theText)
    theHtml = mivami_html.find_one(theText)
    html = theHtml['html']
    html += ('<!––daf:' + str(daf) + '-->')
    h = '' # extra debugging output
    persons_collection = mivami_persons.find_one(theText)
    persons = [tuple(t) for t in persons_collection['person_in_daf']]
    persons_in_sugya = None
    try:
        persons_in_sugya = persons_collection['person_in_sugya']
    except:
        pass
#    html += str(persons)
    if False: #'EncodedEdges' in theHtml and 'EncodedNodes' in theHtml and bCache:
        # already generated and can pull it
        student_edges = theHtml['EncodedEdges']
        student_nodes = theHtml['EncodedNodes']
    else: # compute for the first time

        # must look up each person in the person table for full identity
        #people = list(person.find({'key': {'$in': persons}}))
        #people = [{'name': p['key'], 'generation': p['generation']} for p in people]

        student_nodes = persons
        student_edges, student_nodes = findStudentRelationships(student_nodes)
        # mivami_html.update_one({'title': title + ":" + str(daf)},
        #                   {'$set':
        #                        {'EncodedEdges': student_edges,
        #                         'EncodedNodes': student_nodes}
        #                    }, upsert=True)

        # write the edges out so that it does not need to be computed a second time

    #student_edges = item['EncodedEdges']

        local_interaction_edges, local_interaction_nodes = findLocalRelationships(persons, title + '.' + page)
#    local_interaction_nodes, local_interaction_edges = [], []

    # generate timeline
    # for now, for people, not statements
    timeline = getTimeline(student_nodes)

    if os.name == 'nt':
        html += 'Extra debugguing' + h  + '<br/>'
#     html += 'Local interaction Nodes: ' + str(local_interaction_nodes) + '</br>'
#     html += 'Local interaction Edges: ' + str(local_interaction_edges) + '</br>'
    #local_interaction_nodes = item['LocalInteractionNodes']
    #local_interaction_edges = item['LocalInteractionEdges']
    if 'GlobalInteractionNodes' in theText:
        global_interaction_nodes = item['GlobalInteractionNodes']
        global_interaction_edges = item['GlobalInteractionEdges']
    else:
        global_interaction_edges, global_interaction_nodes = findGlobalRelationships(persons)
        #mivami.update_one({'title': title+":"+str(daf)}, {'$set': {'GlobalInteractionNodes': global_interaction_nodes, 'GlobalInteractionEdges': global_interaction_edges}})

    wrapper += '<a href="https://www.sefaria.org/%s?lang=bi">%s</a></p>' % (title + '.' +str(page), title+" "+str(page))

    wrapper += html

    # fix up tags like < strong >
    wrapper = wrapper.replace('< ', '<')
    wrapper = wrapper.replace(' >', '>')

    leftside = wrapper

    # iterate through sugyot,
    # so that we have different graphs
    sugyaGraphs = dict()
    pplSet = set()
    if persons_in_sugya is not None:
        for i, sugya in enumerate(persons_in_sugya):
            line_start = sugya['line_start']
            sugya_number = sugya['sugya']
            people = sugya['people']
            e, n = findStudentRelationships(people)
            le, ln = findLocalRelationships(people, title + '.' + page)
            ge, gn = findGlobalRelationships(people)
            sugyaGraphs[i] = [e, n, le, ln, ge, gn]

    # why was this not precomputed?
    #local_interaction_edges, local_interaction_nodes = graphTransformation(local_interaction_edges, local_interaction_nodes)
    #student_edges, student_nodes = graphTransformation(student_edges, student_nodes)



    return leftside, student_edges, student_nodes, local_interaction_edges, local_interaction_nodes, \
           global_interaction_edges, global_interaction_nodes, sugyaGraphs, timeline
