# first step is to connect to the mongodb
from pymongo import MongoClient
import sys
from typing import Dict, Tuple, Pattern
from regex import *

def mongoPerekInfoGetter(masechta: str) -> Dict[str, Tuple[int, int]]:
    client = MongoClient()
    db = client.sefaria
    index = db.index
    book = {'title': masechta}
    nodes = list(index.find(book))[0]['alt_structs']['Chapters']['nodes']

    pattern = masechta + " (\d+)(a|b):(\d+)-(\d+)(a|b):(\d+)"

    positions = []
    for i, chapter in enumerate(nodes):
        #print(chapter['wholeRef'])
        m = findall(pattern, chapter['wholeRef'])
        m = m[0]
        daf_start = (int(m[0]) - 2) * 2
        offset_start = 0 if m[1] == 'a' else 1
        line_start = int(m[2]) - 1
        daf_end = (int(m[3]) - 2) * 2
        offset_end = 0 if m[4] == 'a' else 1
        line_end = int(m[5]) - 1

        positions.append((i+1, daf_start + offset_start, line_start, daf_end + offset_end, line_end))
    #print(positions)
    return positions

def mongoExtractStatements(title):
    masechta = title.replace(' ', '')
    underscore_masechta = title.replace(' ', '_')
    perek = 1
    engVersionTitle = 'William Davidson Edition - English'
    hebVersionTitle = 'William Davidson Edition - Aramaic'
    hebEdition = {'title': title, 'versionTitle': hebVersionTitle}
    engEdition = {'title': title, 'versionTitle': engVersionTitle}

    positions = mongoPerekInfoGetter(title)

    client = MongoClient()
    db = client.sefaria
    import pprint
    texts = db.texts
    d = dict()


    hebEdition = list(texts.find(hebEdition))[0]['chapter'][2:]
    engEdition = list(texts.find(engEdition))[0]['chapter'][2:]

#    hadran = 'הדרן עלך'
#    hadran2 = 'הדרן עליך'

    fout = open("../rawTextFiles/"+masechta+"_"+str(perek)+"_raw.txt", "w", encoding='utf-8')

    for perek, daf_start, line_start, daf_end, line_end in positions:
        fout = open("../rawTextFiles/" + masechta + "_" + str(perek) + "_raw.txt", "w", encoding='utf-8')

        for daf in range(daf_start, daf_end+1):
            ls = line_start if daf == daf_start else 0
            le = line_end+1 if daf == daf_end else len(hebEdition[daf])

            h = hebEdition[daf][ls:le]
            e = engEdition[daf][ls:le]
            for h_line, e_line, j in zip(h, e, range(len(h))):
                print(h_line, file=fout)
                print(e_line, file=fout)

        fout.close()

    print()


#mongoExtractStatements('Bava Kamma')



#print(engEdition)

# for i in texts.find():
#     print(i)
#     break
#
# pipeline = [ {"$unwind": "$title"},
#             {"$group": {"_id": "$title", "count": {"$sum": 1}}}]
# results = texts.aggregate(pipeline)
# pprint.pprint(list(results))
