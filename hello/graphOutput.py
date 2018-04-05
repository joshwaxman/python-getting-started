from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://hobby-iamlocehkkokgbkekbgcgbal.dbs.graphenedb.com:24786",
                              auth=basic_auth("mivami", "b.jOGYTThIm49J.NCgtoqGY0qrXXajq"))

session = driver.session()


# def createNode(name):  # create node of 'name' by returning a dictionary to be added to the list 'nodes'
#     try:
#         result = session.run('MATCH (r1:EncodedRabbi) WHERE r1.englishName = "' + name + '"\n' + 'return r1')
#
#         personDict = {}
#         for record in result:
#             # print(record)
#             # print(record['r1'].properties['englishName']) #hebrewName, generation, englishName, sex
#             personDict['name'] = record['r1'].properties['englishName']
#             personDict['label'] = 'Person'
#             personDict['id'] = record['r1'].id
#             # print(personDict)
#         return personDict
#     except:
#         print('ERROR: ' + str(name) + ' not found')  # ///////////// str not dict?

#
# print(createNode('Abaye'))
# print(createNode('Rabbi Shimon b. Rabbi'))


def findRelationship(from_key, to_key):
    relationDict = {}
    result = session.run('MATCH (r1:EncodedRabbi) WHERE r1.englishName = "' + from_key + '"\n' +
                         'MATCH (r2:EncodedRabbi) WHERE r2.englishName = "' + to_key + '"\n' +
                         'MATCH (r1)-[relationship]-(r2)' + "\n" +
                         'return r1, r2, relationship')

    for record in result:
        # print(record['r1'])
        r = record['relationship']
        relationDict['source'] = record['relationship'].start
        relationDict['target'] = record['relationship'].end
        relationDict['type'] = record['relationship'].type
    return relationDict

#
# print(findRelationship('Rav Pappa', 'Abaye'))
# print(findRelationship('Rashi', 'Radak'))

'''
result = session.run('MATCH (r1:EncodedRabbi) WHERE r1.englishName = "' + from_key + '"\n' +
                'MATCH (r2:EncodedRabbi) WHERE r2.englishName = "' + to_key + '"\n' +
                'MATCH (r1)-[relationship]-(r2)' + "\n" +
                'return r1, r2, relationship')

result = session.run('MATCH (r1:EncodedRabbi) WHERE r1.englishName = "' + from_key + '"\n' +
            'MATCH (r2:EncodedRabbi) WHERE r2.englishName = "' + to_key + '"\n' +
            'MATCH path = (r1)-[relationship]->(r2)' + "\n" +
            'return path')

for record in result:
    print(record)
    print(record['path'])
    print(record['path'].start) #returns the node of the id at the start of the path

'''

'''GOAL is to look something like this:

{"nodes":[{name:"Peter",label:"Person",id:1},{name:"Michael",label:"Person",id:2},
          {name:"Neo4j",label:"Database",id:3}],
 "links":[{source:0, target:1, type:"KNOWS", since:2010},{source:0, target:2, type:"FOUNDED"},
          {source:1, target:2, type:"WORKS_ON"}]}'''


def findRelationship2(people):
    edgesOriginal = []  # type: List[Dict[str, str]]
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

        nodesById[nodeId] = {'name': englishName, 'hebrewName': hebrewName, 'generation': generation}

    # now include rabbis who have paths
    query = 'match (r1:EncodedRabbi) where r1.englishName in ' + str(people) + '\n' + \
            'match (r2:EncodedRabbi) where r2.englishName in ' + str(people) + '\n' + \
            'match path = (r1)-[relationship2:student]-(r2)' + '\n' + \
            'return path, relationship2, r1, r2'

    result = session.run(query)

    for record in result:
        nodeId = record['r1'].id
        hebrewName = record['r1']['hebrewName']
        englishName = record['r1']['englishName']
        generation = record['r1']['generation']

        nodesById[nodeId] = {'name': englishName, 'hebrewName': hebrewName, 'generation': generation}

        nodeId = record['r2'].id
        hebrewName = record['r2']['hebrewName']
        englishName = record['r2']['englishName']
        generation = record['r2']['generation']

        nodesById[nodeId] = {'name': englishName, 'hebrewName': hebrewName, 'generation': generation}

        source = record['relationship2'].start
        target = record['relationship2'].end
        relationDict = dict()
        relationDict['source'] = source
        relationDict['target'] = target
        relationDict['type'] = record['relationship2'].type
        edgesOriginal.append(relationDict)

    # now include rabbis who have indirect paths
    query = 'match (r1:EncodedRabbi) where r1.englishName in ' + str(people) + '\n' + \
            'match (r2:EncodedRabbi) where id(r1) <> id(r2) and r2.englishName in ' + str(people) + '\n' + \
            'match (r3:EncodedRabbi) where not r3.englishName in ' + str(people) + '\n' + \
            'match path = (r1)-[relationship1:student]-(r3)-[relationship2: student]-(r2)' + '\n' + \
            'return distinct path, relationship1, relationship2, r1, r2, r3'

    result = session.run(query)

    for record in result:
        # add the additional rabbi
        nodeId = record['r3'].id
        hebrewName = record['r3']['hebrewName']
        englishName = record['r3']['englishName']
        generation = record['r3']['generation']

        nodesById[nodeId] = {'name': englishName, 'hebrewName': hebrewName, 'generation': generation}

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
            setSourceTargetType.add((source, target, type))\

    return edges, nodes



# print(findRelationship2(["Rav Hisda", "Rava", "Rav Hama"]))

# session.close()