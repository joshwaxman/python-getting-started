
from hello.Statement import Statement
from pymongo import MongoClient
import sys
import hello.mongo_statement_extractor as m1
import hello.graphOutput as graphOutput
from typing import List

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


def lookupName(name: str, person):
    # some rules to apply before searching.
    # right now, searching in mongodb person table
    # which had its own transliteration rules. Such as:
    # ḥ -> h as in Rav Yitzḥak bar Avdimi
    # final ei -> e as in Yosei -> Yose
    name = name.replace('ḥ', 'h')
    name = name.replace('Ḥ', 'H')

    import re
    name = re.sub(r'ei\b', 'e', name)
    name = name.replace(' ben ', ' b. ')
    name = name.replace(' bar ', ' b. ')

    # handle Yehuda HaNasi as a special case
    # really need to handle names spanning accross
    # gloss vs. literal text
    if name == "Yehuda HaNasi" or name == "Rabbi" or name == "Rabbi Yehuda HaNasi":
        name = "Rabbi Yehudah haNasi"

    p = person.find_one({'key': name})  # find this person in Mongo sefaria

    if p is None:
        # attempt variations of name to find the best match
        # variation #1. replace 'ben' with b.
        p = person.find_one({'key': name})  # find this person in Mongo sefaria

    if p is None:
        # Attempt 2: Look in alternate names. There is a names
        # array and within each element, a text array. We can
        # find Rabbi Eliezer as:
        # { names.text: ['Rabbi', 'Eliezer']}
        search = {'names.text': str(name.split())}
        import re
        search['generation'] = re.compile('^[TA].*')
        p = person.find_one(search)

    if p is None:
        # Attempt 3: Same as above, but perhaps the final
        # letter ending in 'a' should be ending in 'ah'.
        # For instance, Rabbi Yehuda is stored as Rabbi Yehudah
        altNames = name.split()
        for i in range(len(altNames)):
            if altNames[i].endswith('a'):
                altNames[i] += 'h'
        search = {'names.text': altNames}
        import re
        search['generation'] = re.compile('^[TA].*')
        p = person.find_one(search)

    if p is None:
        # Attempt 3b: Same as above, but with
        # *ei -> e
        # impetus: Rabbi Yosei in english text
        # is Rabbi Yose in the persons table
        altNames = name.split()
        for i in range(len(altNames)):
            if altNames[i].endswith('ei'):
                # chop off last letter
                altNames[i] = altNames[i][:-1]
        search = {'names.text': altNames}
        import re
        search['generation'] = re.compile('^[TA].*')
        p = person.find_one(search)

        # try it also as a key
    if p is None:
        search = {'key': ' '.join(altNames)}
        import re
        search['generation'] = re.compile('^[TA].*')
        p = person.find_one(search)

    def ruleLowerCaseHa(names: List[str]) -> str:
        # motivating examples are 'Rabbi Yose HaGelili'
        # but there are others. In any word, if it begins
        # with Ha and has an internal capital, lowercase
        # the ha
        result = []
        for name in names:
            wordEnd = name[2:]
            if name.startswith('Ha') and wordEnd.lower() != wordEnd:
                result.append('ha' + wordEnd)
            else:
                result.append(name)
        return result

    if p is None:
        search = {'key': ' '.join(ruleLowerCaseHa(altNames))}
        import re
        search['generation'] = re.compile('^[TA].*')
        p = person.find_one(search)

    if p is None:
        # Attempt 4: assume it is a prefix.
        # Case of Rabbi Eliezer as Rabbi Eliezer ben Hyrcanus
        # We could make a list of such shorthands, or we
        # can do our best, and not worry about noise
        # Do NOT do this for something simple like Rabbi,
        # or you will have a big problem. Gives Rabbi Abbahu, for instance
        # and this is spurious

        if ' ' in name:  # then name has mult words
            import re
            regName = re.compile('^' + name + '.*')
            regTannaOrAmora = re.compile('^[TA].*')
            p = person.find_one({'key': regName, 'generation': regTannaOrAmora})

    return p

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

    nodes = set()
    edges = []

    for i in range(len(h)):
        #print()
        #print(i)
        eng, heb = e[i], h[i]
        proc = Statement(e[i], h[i])


        from hello.EnglishStatementProcessor import EnglishStatementProcessor
        ep: EnglishStatementProcessor = EnglishStatementProcessor(proc)
        no, ed = ep.extractAll()
        nodes = nodes | no
        edges = edges + ed


        tokens = proc.getTokens()
        # print(tokens)

        wrapper += '<p dir="rtl">' + h[i] + '</p>\n<p>'

        for j in tokens: #for every list in the list tokens
            if len(j) >= 1:
                for tup in j: #for every tuple in each list j
                    if tup[0] == "LITERAL":
                        wrapper += '<b>'

                    if tup[2] == 'NAME':
                        name = tup[1]
                        p = lookupName(tup[1], person)
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

    e, n = graphOutput.findRelationship2(allRabbis)

    edges, nodes = graphOutput.graphTransformation(edges, nodes)

    return leftside, e, n, edges, nodes