from hello.Statement import Statement
from pymongo import MongoClient
import sys
import hello.mongo_statement_extractor as m1
import hello.graphOutput as graphOutput

#T6 A8  one T4/T5 and no other slashes


def genSplit(s: str):
    if s[0] == 'A':
        clss = 'Amora'
    elif s[0] == 'T':
        clss = 'Tanna'
    elif s[0] == 'Z': #don't know what this is, but it's in there and checked using regexes that are are no slashed to deal with for Zs
        clss = 'Z'
    else:
        raise Exception ('The first letter of generation in the p list from Mongo was not A, T, or Z.', "generation: " + s)

    if '/' not in s and str.isdigit(s[1]): #such as A1
        return clss, s[1:]
    elif '/' not in s: #which means that s[1] is str, such as TA
        if clss == 'Amora' and s[1] == 'T' or clss == 'Tanna' and s[1] == 'A':
            clss = 'Tanna/Amora'
            gen = 0
    #I checked Mongodb using cypher quieries and no generations exist that are A_/T_ or t_/A_.
    elif '/' in s: #such as A2/A3
        gen = s[1] + '/' + s[4]
    else: raise Exception ("Don't know how to read generation " + s)
    return clss, gen

def htmlOutputter(title, page):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    person = db.person
    texts = db.texts
    pplDict = {}

    wrapper = ''

    engVersionTitle = 'William Davidson Edition - English'
    hebVersionTitle = 'William Davidson Edition - Aramaic'
    hebEdition = {'title': title, 'versionTitle': hebVersionTitle}
    engEdition = {'title': title, 'versionTitle': engVersionTitle}

    hebEdition = list(texts.find(hebEdition))[0]['chapter'][2:]
    engEdition = list(texts.find(engEdition))[0]['chapter'][2:]

    amud = page[-1]
    daf_start = (int(page[:-1]) - 2) * 2
    if amud == 'b':
        daf_start += 1

    daf = daf_start

    names = set()
    wrapper += '<a href="https://www.sefaria.org/%s?lang=bi">%s</a></p>' % (title + '.' +str(page), title+" "+str(page)) #Pesachim.7b, Pesachim 7b

    h = hebEdition[daf]
    e = engEdition[daf]

    for i in range(len(h)):
        #print()
        #print(i)

        proc = Statement(e[i], h[i])
        tokens = proc.getTokens()
        #print(tokens)

        wrapper += h[i] + '\n<p>'
        
        wrapper += '\n<p>'
        for j in tokens: #for every list in the list tokens
            if len(j) >= 1:
                for tup in j: #for every tuple in each list j
                    if tup[0] == "LITERAL":
                        wrapper += '<b>'

                    if tup[2] == 'NAME':
                        name = tup[1] #if it's tagged as name, get the name
                        p = person.find_one({'key': name}) #find this person in Mongo sefaria
                        if p is None:
                            # attempt variations of name to find the best match
                            # Attempt 1: Look in alternate names. There is a names
                            # array and within each element, a text array. We can
                            # find Rabbi Eliezer as:
                            # { 'names.text.0': 'Rabbi', 'names.text.1': 'Eliezer'}
                            search = {'names.text.' + str(i): n for i, n in enumerate(name.split())}
                            import re
                            search['generation'] = re.compile('^[TA].*')
                            p = person.find_one(search)

                        if p is None:
                            # Attempt 2: assume it is a prefix.
                            # Case of Rabbi Eliezer as Rabbi Eliezer ben Hyrcanus
                            # We could make a list of such shorthands, or we
                            # can do our best, and not worry about noise
                            import re
                            regName = re.compile('^' + name + '.*')
                            regTannaOrAmora = re.compile('^[TA].*')
                            p = person.find_one({'key': regName, 'generation': regTannaOrAmora})

                        if p is not None:
                            names.add(p['key'])
                            #/////////do we want the whole node like {'name': 'Abaye', 'label': 'Person', 'id': 25}? In the example, just had the name.
                        try: #if 'generation' in p:
                            if p is not None:
                                clss, gen = genSplit(p['generation']) #returns a tuple of the class and generation
                                # store in dictionary just for fun
                                pplDict[p['key']] = (p['names'][0]['text'], p['names'][1]['text'], clss, gen)  # key = eng name, data = eng name, heb name, class (Amora or Tanna), generation
                                #make the necessary adjustments in the html and output it
                                wrapper += '<span class="%s" generation="%s">%s</span> ' % (clss, gen, name)
                            else:
                                w = tup[1]
                                wrapper += w + ' '

                                print('name: ' + name + ' is not found')
                        except Exception as e:
                            print(e)
                            print("ERROR.  P is:", p)
                    else:
                        w = tup[1]
                        wrapper += w + ' '

                    if tup[0] == "LITERAL":
                        wrapper += '</b> '

        wrapper += '</p>'

    # fix up tags like < strong >
    wrapper = wrapper.replace('< ', '<')
    wrapper = wrapper.replace(' >', '>')

    leftside = wrapper

    allRabbis = [key for key in pplDict]
    edges, nodes = graphOutput.findRelationship2(allRabbis)

    return leftside, edges, nodes