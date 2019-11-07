import os
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph
from py2neo.data import walk

driver = None
session = None

def getClarkFullList():
    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    html = '<h1>Full shoresh list</h1>'
    data = g.run('MATCH (n:ClarkShoresh) RETURN n ORDER by n.root').data()

    alephbet = 'אבגדהוזחטחיכלמנסעפצקרשת'
    words = []
    for node in data:
        root = node['n']['root']
        words.append(root)

    prevword = ''
    for word in words:
        html += '<a href="' + word + '"</a>' + word + '\n&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        if word[0] != prevword[0]:
            html += '\n<br>'
        prevword = word

    return html, [], []

def append_graph(nodes, relationships, query):
    driver = GraphDatabase.driver("bolt://172.104.217.202:7687", auth=basic_auth("neo4j", "qwerty"))
    session = driver.session()
    result = session.run(query)
    for record in result:
        for item in record:
            if type(item).__name__ == 'Node':
                id = item.id
                label = item._labels.copy().pop()
                properties = item._properties.copy()
                node = dict(label=label)
                for k, v in properties.items():
                    node[k] = v
                nodes[id] = node
            elif type(item).__name__ == 'list': # if multistep relationships
                item = item[0]
                id = item.id
                start = item._start_node.id
                end = item._end_node.id
                rel = dict(label=type(item).__name__, source=start, target=end)
                relationships[id] = rel
            else: # assume it is a relationship with the __name__ being the rel type
                id = item.id
                start = item._start_node.id
                end = item._end_node.id
                rel = dict(label=type(item).__name__, source=start, target=end)
                relationships[id] = rel
    session.close()

def neoToD3(nodes, relationships):
    nToI = {key: pos for pos, key in enumerate(nodes)}
    nds = [value for value in nodes.values()]
    edges = [dict(source=nToI[v['source']], target=nToI[v['target']], label=v['label']) for v in relationships.values()]
    return nds, edges

def getClarkShoresh(shoresh: str):
    d = dict()
    g = Graph("bolt://172.104.217.202:7687", auth=("neo4j", "qwerty"))
    #/ browser /:24780 / db / data /
    html = ''

    nodes, relationships = {}, {}
    query = "match (r:ClarkShoresh)-[rel]-(c:ClarkPhonemicClass) where r.root='" +  shoresh + "'\n" + \
            "match (c)-[rel2]-(p)\n" + \
            " return r, c, p, rel, rel2"
    append_graph(nodes, relationships, query)

    html += '<b>Shoresh</b>: ' + shoresh + '<br/>'
    for n in nodes.values():
        if 'root' in n and n['root'] == shoresh:
            html += '<b>Meaning</b>: ' + n['meaning'] + '<br/>'

    query = "match (r:ClarkShoresh)-[rel]-(r2:ClarkShoresh) where r.root='" + shoresh + "'\n" + \
            "match (r2)-[rel2]-(c:ClarkPhonemicClass)\n" + \
            " return r, r2, c, rel, rel2"
    append_graph(nodes, relationships, query)

    nodes, edges = neoToD3(nodes, relationships)
    # i = 0
    # phonemic_classes = set()
    # edges = []
    # for p in cs:
    #     html += 'Shoresh: ' + p['root'] + '<br/>'
    #     html += 'Meaning: ' + p['meaning'] + '<br/>'
    #
    #     nodes = []
    #     key = p['root'] + ';' + p['meaning']
    #     nodeDict = dict()
    #     nodeDict[key] = i
    #     i += 1
    #     nodes.append(dict(root=p['root'], meaning=p['meaning']))
    #
    # for j, p in enumerate(cs):
    #     rels = g.match(nodes=[p, None], r_type='MEMBER_OF')
    #
    #     if len(rels) > 0:
    #         html += '<br/><b>Phonemic Classes:</b><br/>'
    #         for rel in rels:
    #             pc = rel.end_node
    #
    #             html += 'Phonemic class: <a href="' + pc['name'] + '">' + pc['name'] + '</a><br/>'
    #             phonemic_classes.add(pc)
    #             n = dict(name=pc['name'], group=pc['group'])
    #             nodes.append(n)
    #             key = n['name'] + ';' + n['group']
    #             nodeDict[key] = i
    #             edges.append(dict(source=j, target=i, label='MEMBER_OF'))
    #             i += 1
    #
    # for pc in phonemic_classes:
    #     key = pc['name'] + ';' + pc['group']
    #     toIndex = nodeDict[key]
    #     rels = g.match([None, pc], r_type='MEMBER_OF')
    #     for i, rel in enumerate(rels, 1):
    #         s = rel.start_node
    #         key = s['root'] + ';' + s['meaning']
    #         if key in nodeDict.keys():
    #             fromIndex = nodeDict[key]
    #         else:
    #             n = dict(root=s['root'], meaning=s['meaning'])
    #             nodes.append(n)
    #             fromIndex = len(nodes) - 1
    #             nodeDict[key] = fromIndex
    #
    #         edges.append(dict(source=fromIndex, target=toIndex, label='MEMBER_OF'))

    return html, nodes, edges