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






# print(findRelationship2(["Rav Hisda", "Rava", "Rav Hama"]))

# session.close()