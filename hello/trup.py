from pymongo import MongoClient
import sys
import re
# example ply here: https://www.dabeaz.com/ply/example.html

tokens = tuple('MAHPACH PASHTA MUNACH ZAKEF_KATON ZAKEF_GADOL MERCHA TIPCHA ETNACHTA ' \
                'DARGA TEVIR KADMA GERESH GERSHAYIM ZARQA SEGOLTA REVIA MUNACH_LEGARMEIH MUNACH_LEGARMEIH2 ' \
                'SILLUQ YETIV TELISHA_GEDOLA TELISHA_KETANA PAZER GERESH_MUKDAM ETNACH_HAFUCH ' \
                'SHALSHELET MERCHA_KEFULA GALGAL KARNEI_PARA DECHI OLEH ILUY TZINORIT SOF_PASUK'.split())
#print('tokens:', tokens)

SHEVA = 'ְ'
CHATAF_SEGOL = 'ֱ'
CHATAF_PATACH = 'ֲ'
CHATAF_KAMATZ = 'ֳ'
CHIRIK = 'ִ'
TZERE = 'ֵ'
SEGOL = 'ֶ'
PATACH = 'ַ'
KAMATZ = 'ָ'
CHOLAM = 'ֹ'
CHOLAM_CHASER_FOR_VAV = 'ֺ'
KUBUTZ = 'ֻ'
DAGESH = 'ּ'
SHIN_DOT = 'ׁ'
SIN_DOT = 'ׂ'
UPPER_DOT = 'ׄ'
LOWER_DOT = 'ׅ'
nekudot = SHEVA + CHATAF_SEGOL + CHATAF_PATACH + CHATAF_KAMATZ + CHIRIK + TZERE + \
            PATACH + KAMATZ + CHOLAM + CHOLAM_CHASER_FOR_VAV + KUBUTZ + DAGESH + \
            SHIN_DOT + SIN_DOT + UPPER_DOT + LOWER_DOT
nekudot2 = 'ְֱֲֳִֵֶַָֹּׁׂ'
OPTIONAL_PESIK = '׀' + '?'
# alephbet = '־אבגדהוזחטיכלמנסעפצקרשתץךףםן' + 'ְֱֲֳִֵֶַָֹּׁׂ' + 'ֽ'# last is meteg/silluq
alephbet = '־אבגדהוזחטיכלמנסעפצקרשתץךףםן' + nekudot + nekudot2 + 'ֽ'# last is meteg/silluq
RBEGIN = '[' + alephbet + ']*'
REND = RBEGIN

# hebrew trup characters
mahpach = '֤'
pashta = '֙'
munach = '֣'
zakef_katon = '֔'
zakef_gadol = '֕'
mercha = '֥'
tipcha = '֖'
etnachta = '֑'
darga = '֧'
tevir = '֛'
kadma = '֨'
geresh = '֜'
gershayim = '֞'
zarka = '֮'
segolta = '֒'
revia = '֗'
etnach_hafuch = '֢'
silluq = '׃'
yetiv = '֚'
telisha_gedola = '֠'
telisha_katana = '֩'
pazer = '֡'
geresh_mukdam = '֝'
shalshelet = '֓'
mercha_kefula = '֦'
galgal = '֪'
karnei_para = '֟'
melachim = pashta + zakef_katon + zakef_gadol + tipcha + etnachta + tevir + geresh + gershayim + silluq + revia + yetiv + telisha_gedola + pazer + geresh_mukdam + segolta
# Tokens
t_MAHPACH = RBEGIN + mahpach + REND + OPTIONAL_PESIK
t_PASHTA = RBEGIN + r'֙' + '(' + RBEGIN + r'֙' + ')?' + REND
t_MUNACH = RBEGIN + r'֣' + REND # but if trailer == '׀ ' should be munach_legarmeih...
t_ZAKEF_GADOL = RBEGIN + r'֕' + REND
t_ZAKEF_KATON = RBEGIN + '(' + r'֕' + '|' + r'֨' + ')?' + r'֔' + REND
t_MERCHA = RBEGIN + r'֥' + REND + OPTIONAL_PESIK
t_MUNACH_LEGARMEIH = RBEGIN +r'֣' + REND + '׀'
t_MUNACH_LEGARMEIH2 = RBEGIN +r'֣' + REND + '&'
t_TIPCHA = RBEGIN + r'֖' + REND
t_ETNACHTA = RBEGIN + '(' + r'֑' + '|' + '֑' + ')' + REND
t_DARGA = RBEGIN + r'֧' + REND + OPTIONAL_PESIK
t_TEVIR = RBEGIN + r'֛' + REND
t_KADMA = RBEGIN + r'֨' + REND + OPTIONAL_PESIK
t_GERESH = RBEGIN + r'֜' + REND
t_GERSHAYIM = RBEGIN + r'֞' + REND
# t_ZARQA = RBEGIN + r'֘' + REND
t_ZARQA = RBEGIN + '(' + r'֘' + '|' + '֮' + ')' + REND
t_SEGOLTA = RBEGIN + r'֒' + REND
t_REVIA = RBEGIN + r'֗' + REND
t_ETNACH_HAFUCH = RBEGIN + r'֢' + REND
#t_SILLUQ = RBEGIN + r'(75|25)' + REND

t_SILLUQ = RBEGIN + r'׃' + REND

t_YETIV = RBEGIN + r'֚' + REND
t_TELISHA_GEDOLA = RBEGIN + r'֠' + REND
t_TELISHA_KETANA = RBEGIN + r'֩' + REND
t_PAZER = RBEGIN + r'֡' + REND
t_GERESH_MUKDAM = RBEGIN + r'֝' + REND
t_SHALSHELET = RBEGIN + r'֓' + REND + OPTIONAL_PESIK
t_MERCHA_KEFULA = RBEGIN + r'֦' + REND
t_GALGAL = RBEGIN + r'֪' + REND
t_KARNEI_PARA = RBEGIN + r'֟' + REND
t_DECHI = RBEGIN + r'֭' + REND
t_OLEH = RBEGIN + r'֫' + REND
t_ILUY = RBEGIN + r'֬' + REND
t_TZINORIT = RBEGIN + r'֮' + REND
t_SOF_PASUK = RBEGIN + r'׃' + REND

# t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'
#
# def t_NUMBER(t):
#     r'\d+'
#     try:
#         t.value = int(t.value)
#     except ValueError:
#         print("Integer value too large %d", t.value)
#         t.value = 0
#     return t

# Ignored characters
t_ignore = " \t\n"

def t_error(t):
    #print(book, chapter, pasuk, end=' ')
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
import ply.lex as lex
from ply.lex import LexToken
lexer =  lex.lex(reflags=re.UNICODE | re.VERBOSE)

# can download zip of text from here: http://ota.ox.ac.uk/desc/0525
# in Hebrew here: https://www.mechon-mamre.org/c/ct/cu0101.htm
# Genesis 1:1
# text = 'בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃'
# lexer.input(text)
# marked = ' '.join(['(' + i.value + ', ' + i.type + ')' for i in lexer])
# print(marked)





#
# # Genesis 1:29
# text = '''
# WA/Y.O74)MER ):ELOHI81YM HIN."H04 NFTA63T.IY L/FKE61M
# )ET-K.FL-("74&EB05 ZOR"74(A ZE81RA( ):A$ER03 (AL-?P.:N"74Y
# KFL-HF/)F80REC W:/)ET-K.FL-HF/("91C ):A$ER-B.O71W
# P:RIY-("73C ZOR"74(A ZF92RA( L/FKE71M YI75H:YE73H?
# L:/)FK:LF75H00
# '''
# lexer.input(text)
# marked = ' '.join(['(' + i.value + ', ' + i.type + ')' for i in lexer])
# #print(marked)
#
#
# Parsing rules

# def p_pasuk(p):
#     '''pasuk : silluq_clause'''
#     p[0] = ('PASUK', p[1])

def p_pasuk_clause(p):
    '''pasuk_clause : etnachta_clause silluq_clause
                    | silluq_clause'''
    p[0] = tuple(['PASUK'] + p[1:])

def p_silluq_clause(p):
    '''silluq_clause : tipcha_clause silluq_clause
            | zakef_katon_clause silluq_clause
            | zakef_gadol_clause silluq_clause
            | segolta_clause silluq_clause
            | mesharet silluq
            | silluq
            '''
    p[0] = tuple(['SILLUQ'] + p[1:])


def p_silluq(p):
    '''silluq : SILLUQ'''
    p[0] = p.slice[1]


def p_etnachta_clause(p):
    '''etnachta_clause : etnachta
            | mesharet etnachta
            | mesharet mesharet etnachta
            | zakef_katon_clause etnachta_clause
            | zakef_gadol_clause etnachta_clause
            | segolta_clause etnachta_clause
            | shalshelet_clause etnachta_clause
            | tipcha_clause etnachta_clause'''

    p[0] = tuple(['ETNACHTA'] + p[1:])

def p_etnachta(p):
    '''etnachta : ETNACHTA'''
    p[0] = p.slice[1]

def p_mesharet(p):
    '''mesharet : MERCHA
                | MUNACH
                | MAHPACH
                | DARGA
                | KADMA
                | TELISHA_KETANA
                | GALGAL'''

    # print(len(p.slice))
    p[0] = p.slice[1]



def p_tipcha_clause(p):
    '''tipcha_clause : mesharet tipcha
                       | mesharet mesharet tipcha
                       | tipcha
                       | tevir_clause tipcha_clause
                       | mercha_kefula_clause tipcha_clause
                       | revia_clause tipcha_clause
                       | pashta_clause tipcha_clause'''
    p[0] = tuple(['TIPCHA'] + p[1:])


def p_tipcha(p):
    '''tipcha : TIPCHA'''
    p[0] = p.slice[1]



def p_revia_clause(p):
    '''revia_clause : mesharet revia
                    | mesharet mesharet revia
                    | mesharet mesharet mesharet revia
                    | revia
                    | geresh_clause revia_clause
                    | gershayim_clause revia_clause
                    | telisha_gedola_clause revia_clause
                    | pazer_clause revia_clause
                    | karnei_para_clause revia_clause
                    | munach_legarmeih_clause revia_clause'''

    p[0] = tuple(['REVIA'] + p[1:])



def p_revia(p):
    '''revia : REVIA'''
    p[0] = p.slice[1]


def p_zakef_katon_clause(p):
    '''zakef_katon_clause : mesharet zakef_katon
                          | mesharet mesharet zakef_katon
                          | revia_clause zakef_katon_clause
                          | pashta_clause zakef_katon_clause
                          | yetiv_clause zakef_katon_clause
                          | zakef_katon'''
    if len(p.slice) == 2:
        p[0] = ('ZAKEF_KATON', p[1])
    else:
        p[0] = ('ZAKEF_KATON', p[1], p[2])


    # note: allowing rule of "mesharet mesharet zakef_katon"
    # means that certain times, where the first mesharet is a
    # kadma, would be allowed, even though it really would be
    # an error for identical pashta, IMHO.
    # could make several classes of mesharets in different
    # contexts in order to tighten this rule and others.


def p_zakef_katon(p):
    '''zakef_katon : ZAKEF_KATON'''
    p[0] = p.slice[1]


def p_pashta_clause(p):
    '''pashta_clause : gershayim_clause pashta_clause
                       | pazer_clause pashta_clause
                       | karnei_para_clause pashta_clause
                       | geresh_clause pashta_clause
                       | telisha_gedola_clause pashta_clause
                       | mesharet pashta
                       | mesharet mesharet pashta
                       | mesharet mesharet mesharet pashta
                       | mesharet mesharet mesharet mesharet pashta
                       | mesharet mesharet mesharet mesharet mesharet pashta
                       | mesharet mesharet mesharet mesharet mesharet mesharet pashta
                       | pashta'''
    p[0] = tuple(['PASHTA'] + p[1:])


def p_pashta(p):
    '''pashta : PASHTA'''
    p[0] = p.slice[1]


def p_geresh_clause(p):
    '''geresh_clause : mesharet geresh
                     | mesharet mesharet geresh
                     | mesharet mesharet mesharet geresh
                     | mesharet mesharet mesharet mesharet geresh
                     | mesharet mesharet mesharet mesharet mesharet geresh
                     | geresh'''


    # see Wickes pg 117, that even though pazer, geresh and telisha gedola
    # stand on the same level, pazer ( / karnei para) can also stand as
    # subordinate to the geresh. and the geresh can even be transformed into
    # a mesharet, but Wickes would still consider the pazer and karnei para
    # to be subordinated to that transformed geresh. for now, we cannot
    # handle such transformations. That would require semantic + syntactic
    # knowledge, namely where precisely the major dichotomy was to have fallen.

    p[0] = tuple(['GERESH'] + p[1:])


def p_geresh(p):
    '''geresh : GERESH'''
    p[0] = p.slice[1]

def p_gershayim_clause(p):
    '''gershayim_clause : mesharet gershayim
                        | gershayim'''
    p[0] = tuple(['GERSHAYIM'] + p[1:])


def p_gershayim(p):
    '''gershayim : GERSHAYIM'''
    p[0] = p.slice[1]


def p_yetiv_clause(p):
    '''yetiv_clause : yetiv
                    | mesharet yetiv'''
    p[0] = tuple(['YETIV'] + p[1:])


def p_yetiv(p):
    '''yetiv : YETIV'''
    p[0] = p.slice[1]


def p_tevir_clause(p):
    '''tevir_clause : mesharet tevir
                    | mesharet mesharet tevir
                    | mesharet mesharet mesharet tevir
                    | mesharet mesharet mesharet mesharet tevir
                    | tevir
                    | geresh_clause tevir_clause
                    | gershayim_clause tevir_clause
                    | telisha_gedola_clause tevir_clause
                    | pazer_clause tevir_clause
                    | karnei_para_clause tevir_clause'''
    p[0] = tuple(['TEVIR'] + p[1:])


def p_tevir(p):
    '''tevir : TEVIR'''
    p[0] = p.slice[1]


def p_mercha_kefula_clause(p):
    '''mercha_kefula_clause : mesharet mercha_kefula'''

    # note that the mesharet here is specifically darga
    p[0] = tuple(['MERCHA_KEFULA'] + p[1:])


def p_mercha_kefula(p):
    '''mercha_kefula : MERCHA_KEFULA'''
    p[0] = p.slice[1]



def p_telisha_gedola_clause(p):
    '''telisha_gedola_clause : telisha_gedola
                             | mesharet telisha_gedola
                             | mesharet mesharet telisha_gedola
                             | mesharet mesharet mesharet telisha_gedola
                             | mesharet mesharet mesharet mesharet telisha_gedola
                             | mesharet mesharet mesharet mesharet mesharet telisha_gedola'''
    p[0] = tuple(['TELISHA_GEDOLA'] + p[1:])


def p_telisha_gedola(p):
    '''telisha_gedola : TELISHA_GEDOLA'''
    p[0] = p.slice[1]


def p_pazer_clause(p):
    '''pazer_clause : mesharet pazer
                    | mesharet mesharet pazer
                    | mesharet mesharet mesharet pazer
                    | mesharet mesharet mesharet mesharet pazer
                    | mesharet mesharet mesharet mesharet mesharet pazer
                    | pazer
                    | munach_legarmeih2_clause pazer_clause'''
    p[0] = tuple(['PAZER'] + p[1:])


def p_pazer(p):
    '''pazer : PAZER'''
    p[0] = p.slice[1]


# karnei para stands in place of a regular ("little" pazer)
# and is sometimes called the great pazer

# also, the mesharetim should be munach* munach galgal
# but that would mean introducing different classes of mesharet
# perhaps implement later. for now, just call mesharet
def p_karnei_para_clause(p):
    '''karnei_para_clause : mesharet mesharet karnei_para
                    | mesharet mesharet mesharet karnei_para
                    | mesharet mesharet mesharet mesharet karnei_para
                    | mesharet mesharet mesharet mesharet mesharet karnei_para
                    | mesharet mesharet mesharet mesharet mesharet mesharet karnei_para
                    | mesharet mesharet mesharet mesharet mesharet mesharet mesharet karnei_para'''

    p[0] = tuple(['KARNEI_PARA'] + p[1:])

def p_karnei_para(p):
    '''karnei_para : KARNEI_PARA'''
    p[0] = p.slice[1]

def p_munach_legarmeih_clause(p):
    '''munach_legarmeih_clause : mesharet munach_legarmeih
                               | mesharet mesharet munach_legarmeih
                               | munach_legarmeih'''
    p[0] = tuple(['MUNACH_LEGARMEIH'] + p[1:])


def p_munach_legarmeih(p):
    '''munach_legarmeih : MUNACH_LEGARMEIH'''
    p[0] = p.slice[1]


def p_munach_legarmeih2_clause(p):
    '''munach_legarmeih2_clause : mesharet munach_legarmeih2
                               | mesharet mesharet munach_legarmeih2
                               | mesharet mesharet mesharet munach_legarmeih2
                               | munach_legarmeih2'''
    p[0] = tuple(['MUNACH_LEGARMEIH2'] + p[1:])


def p_munach_legarmeih2(p):
    '''munach_legarmeih2 : MUNACH_LEGARMEIH2'''
    p[0] = p.slice[1]


def p_segolta_clause(p):
    '''segolta_clause : zarqa_clause segolta_clause
                      | revia_clause segolta_clause
                      | pashta_clause segolta_clause
                      | mesharet segolta
                      | mesharet mesharet segolta
                      | segolta'''
    p[0] = tuple(['SEGOLTA'] + p[1:])


def p_segolta(p):
    '''segolta : SEGOLTA'''
    p[0] = p.slice[1]


def p_shalshelet_clause(p):
    '''shalshelet_clause : shalshelet'''
    p[0] = tuple(['SHALSHELET'] + p[1:])


def p_shalshelet(p):
    '''shalshelet : SHALSHELET'''
    p[0] = p.slice[1]

def p_zarqa_clause(p):
    '''zarqa_clause : mesharet zarqa
                    | mesharet mesharet zarqa
                    | mesharet mesharet mesharet zarqa
                    | mesharet mesharet mesharet mesharet zarqa
                    | zarqa
                    | geresh_clause zarqa_clause
                    | gershayim_clause zarqa_clause
                    | telisha_gedola_clause zarqa_clause
                    | pazer_clause zarqa_clause
                    | karnei_para_clause zarqa_clause'''
    p[0] = tuple(['ZARQA'] + p[1:])


def p_zarqa(p):
    '''zarqa : ZARQA'''
    p[0] = p.slice[1]


def p_zakef_gadol_clause(p):
    '''zakef_gadol_clause : zakef_gadol
                        | pashta_clause zakef_gadol_clause'''

    p[0] = tuple(['ZAKEF_GADOL'] + p[1:])


def p_zakef_gadol(p):
    '''zakef_gadol : ZAKEF_GADOL'''
    p[0] = p.slice[1]


book, chapter = None, None

def p_error(p):
    global i, pasuk, marked

    if p:
        # print(book, chapter, pasuk, end=' ')
        print("Syntax error at '%s'" % p.value)
#        print(chapter, verse_num, pasuk, marked)
#        print()
    else:
        # print(book, chapter, pasuk, end=' ')
        print("Syntax error at EOF")

import ply.yacc as yacc
yacc.yacc()

#
# text = 'B.:/R")$I73YT B.FRF74) ):ELOHI92YM )"71T HA/$.FMA73YIM W:/)"71T HF/)F75REC00'
# # #text = 'W:/)"71T HF/)F75REC00'
# text = '''W:/HF/)F81REC? HFY:TF71H TO33HW.03 WF/BO80HW. W:/XO73$EK:
# (AL-P.:N"74Y T:HO92WM W:/R74W.XA ):ELOHI80YM M:RAXE73PET
# (AL-P.:N"71Y? HA/M.F75YIM00'''
#
# # text = '''T:HO92WM W:/R74W.XA ):ELOHI80YM M:RAXE73PET (AL-P.:N"71Y? HA/M.F75YIM00'''
# text = '''
# WA/Y.O74)MER ):ELOHI80YM Y:HI71Y RFQI73Y(A B.:/TO74WK:
# HA/M.F92YIM WI/YHI74Y MAB:D.I80YL? B."71YN MA73YIM
# LF/MF75YIM00'''
#
# f = open(r'.\Trup\michigan.txt')
# lines = f.readlines()
# f.close()
#
# book = 'Genesis'
# chapter = 1
# verse_num = 1
# pasuk = ''
# pesukim = []
# for line in lines[3:]:
#     if line.startswith('~x'):
#         chapter += 1
#         verse_num = 1
#     if line.startswith('~y'):
#         if pasuk != '':
#             pesukim.append((chapter, verse_num, pasuk))
#             verse_num += 1
#         pasuk = ''
#     else:
#         pasuk += line
#
#
# print(len(pesukim))
# from pprint import pprint
#
# from pymongo import MongoClient
# client = MongoClient()
# sefaria = client.sefaria
# trup = sefaria.trup
#
def encode(tree):
    treeData = []
    if type(tree) is LexToken:
    # if len(tree) == 0: # leaf
        return {'name': tree.value}
    elif tree is None: # TODO find out when this is the case and fix!
        pass
    else: #internal node
        children = []

        for child in tree[1:]:
            children.append(encode(child))

        return {'name': str(tree[0]), 'children': children}


def bit_encode(tree, encoding, consider_leaves=False):
    # a preorder traversal of the binary trie
    if tree is None: # TODO: get to the bottom of when this happen
        return encoding

    if type(tree[1]) is LexToken: # all children are leaves
        if consider_leaves:
            encoding.append(str(len(tree)-1))
        else:
            encoding.append('1') # could also append the leaves?
        return encoding

    encoding.append('0')
    for child in tree[1:]:
        bit_encode(child, encoding, consider_leaves)

    return encoding

def preprocess(text):
    # strip setuma and petucha breaks
    if text.endswith(' (פ)'):
        text = text[:-4]
    if text.endswith(' (ס)'):
        text = text[:-4]

    text = text.replace(']', '').replace('[', '')

    # some verses are input missing their final sof pasuk
    # if so, add it
    if '׃' not in text:
        text = text + '׃'

    text = text.replace(' ׀', '׀')

    # preprocess text to form munach_legarmeih where exists
    # and to scan ahead in input to make sure that the next
    # melech will be a revia or pazer or geresh.
    # (possibly pashta due to transformation?)

    s = text.split()
    for i in range(len(s)):
        if s[i].endswith('׀'):
            # find next melech
            for j in range(i + 1, len(s)):
                if any(melech in s[j] for melech in melachim):
                    break
            # j has the position of the next melech
            if revia in s[j]:  # munach legarmeih
                pass  # leave alone
            elif pazer in s[j]:  # munach legarmeih before pazer
                s[i] = s[i][:-1] + '&'  # special munach legarmeih
            else:  # remove the ׀
                s[i] = s[i][:-1]

    return ' '.join(s)




books = 'Genesis Exodus Leviticus Numbers Deuteronomy ' \
    'Joshua Judges Isaiah Jeremiah Ezekiel ' \
        'Hosea Joel Amos Obadiah Jonah Micah Nahum ' \
        'Habakkuk Zephaniah Haggai Zechariah Malachi ' \
        'Psalms Job Proverbs Ruth Ecclesiastes ' \
        'Lamentations Esther Daniel Ezra Nehemiah'.split() + ['Song of Songs', 'I Samuel', 'II Samuel',
                                                              'I Kings', 'II Kings',
                                                              'I Chronicles', 'II Chronicles']

def getTree(verse):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    iso_trees = db.iso_trees
    iso_trees2 = db.iso_trees2
    texts = db.texts
    space_pos = verse.rfind(' ')
    s = verse[0: space_pos], verse[space_pos+1:]
    if len(s) > 0:
        book = s[0]
        chapter, verse_num = s[1].split(':')
        chapter = int(chapter) - 1
        verse_num = int(verse_num) - 1
        search = dict(versionTitle="Tanach with Ta'amei Hamikra", title=book)

        x = texts.find_one(search)
        text = x['chapter'][chapter][verse_num]
        ch = x['chapter'][chapter]
        # calculate next
        # if not the last verse in chapter
        if verse_num < len(ch) - 1:
            next = book + ' ' + str(chapter + 1) + ':' + str(verse_num + 2)
        else:
            next = book + ' ' + str(chapter + 2) + ':1'

        # calculate prev
        if verse_num == 0:
            ch = x['chapter'][chapter-1]
            # what is last verse in prev chapter
            prev = book + ' ' + str(chapter) + ':' + str(len(ch))
        else:
            prev = book + ' ' + str(chapter + 1) + ':' + str(verse_num)

        chapter = chapter + 1
        pasuk = verse_num
        if book == 'Genesis' and chapter == 35 and pasuk == 22:
            text = 'וַיְהִ֗י בִּשְׁכֹּ֤ן יִשְׂרָאֵל֙ בָּאָ֣רֶץ הַהִ֔וא וַיֵּ֣לֶךְ רְאוּבֵ֗ן וַיִּשְׁכַּב֙ אֶת־בִּלְהָה֙ פִּילֶ֣גֶשׁ אָבִ֔יו וַיִּשְׁמַ֖ע יִשְׂרָאֵ֑ל וַיִּֽהְי֥וּ בְנֵֽי־יַעֲקֹ֖ב שְׁנֵ֥ים עָשָֽׂר׃'
        elif book == 'Exodus' and chapter == 4 and pasuk == 10:
            text = 'וַיֹּ֨אמֶר מֹשֶׁ֣ה אֶל־יְהוָה֮ בִּ֣י אֲדֹנָי֒ לֹא֩ אִ֨ישׁ דְּבָרִ֜ים אָנֹ֗כִי גַּ֤ם מִתְּמוֹל֙ גַּ֣ם מִשִּׁלְשֹׁ֔ם גַּ֛ם מֵאָ֥ז דַּבֶּרְךָ֖ אֶל־עַבְדֶּ֑ךָ כִּ֧י כְבַד־פֶּ֛ה וּכְבַ֥ד לָשׁ֖וֹן אָנֹֽכִי׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 2:
            text = 'אָֽנֹכִי֙ יְהוָ֣ה אֱלֹהֶ֔יךָ אֲשֶׁ֧ר הֽוֹצֵאתִ֛יךָ מֵאֶ֥רֶץ מִצְרַ֖יִם מִבֵּ֣ית עֲבָדִ֑ים לֹֽא־יִהְיֶ֥ה לְךָ֛ אֱלֹהִ֥ים אֲחֵרִ֖ים עַל־פָּנָֽי׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 3:
            # duplicate on purpose because of alignment issues of etnachta or full verse
            text = 'אָֽנֹכִי֙ יְהוָ֣ה אֱלֹהֶ֔יךָ אֲשֶׁ֧ר הֽוֹצֵאתִ֛יךָ מֵאֶ֥רֶץ מִצְרַ֖יִם מִבֵּ֣ית עֲבָדִ֑ים לֹֽא־יִהְיֶ֥ה לְךָ֛ אֱלֹהִ֥ים אֲחֵרִ֖ים עַל־פָּנָֽי׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 4:
            text = 'לֹֽא־תַעֲשֶׂ֨ה לְךָ֥ פֶ֨סֶל֙ וְכָל־תְּמוּנָ֔ה אֲשֶׁ֤ר בַּשָּׁמַ֨יִם֙ מִמַּ֔עַל וַֽאֲשֶׁ֥ר בָּאָ֖רֶץ מִתָּ֑חַת וַֽאֲשֶׁ֥ר בַּמַּ֖יִם מִתַּ֥חַת לָאָֽרֶץ׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 5:
            text = 'לֹֽא־תִשְׁתַּחֲוֶ֥ה לָהֶ֖ם וְלֹ֣א תָֽעָבְדֵ֑ם כִּ֣י אָֽנֹכִ֞י יְהוָ֤ה אֱלֹהֶ֨יךָ֙ אֵ֣ל קַנָּ֔א פֹּ֠קֵד עֲוֺ֨ן אָבֹ֧ת עַל־בָּנִ֛ים עַל־שִׁלֵּשִׁ֥ים וְעַל־רִבֵּעִ֖ים לְשֹֽׂנְאָֽי׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 6:
            text = 'וְעֹ֥שֶׂה חֶ֖סֶד לַֽאֲלָפִ֑ים לְאֹֽהֲבַ֖י וּלְשֹֽׁמְרֵ֥י מִצְוֺתָֽי׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 7:
            text = 'לֹ֥א תִשָּׂ֛א אֶת־שֵֽׁם־יְהוָ֥ה אֱלֹהֶ֖יךָ לַשָּׁ֑וְא כִּ֣י לֹ֤א יְנַקֶּה֙ יְהוָ֔ה אֵ֛ת אֲשֶׁר־יִשָּׂ֥א אֶת־שְׁמ֖וֹ לַשָּֽׁוְא׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 8:
            text = 'זָכ֛וֹר אֶת־י֥וֹם הַשַּׁבָּ֖ת לְקַדְּשֽׁוֹ׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 9:
            text = 'שֵׁ֤שֶׁת יָמִים֙ תַּֽעֲבֹ֔ד וְעָשִׂ֖יתָ כָּל־מְלַאכְתֶּֽךָ׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 10:
            # should really get the other taam for this so that it will be separate verses
            text = 'וְיוֹם֙ הַשְּׁבִיעִ֔י שַׁבָּ֖ת לַֽיהוָ֣ה אֱלֹהֶ֑יךָ לֹֽא־תַעֲשֶׂ֨ה כָל־מְלָאכָ֜ה אַתָּ֣ה ׀ וּבִנְךָ֣ וּבִתֶּ֗ךָ עַבְדְּךָ֤ וַאֲמָֽתְךָ֙ וּבְהֶמְתֶּ֔ךָ וְגֵֽרְךָ֖ אֲשֶׁ֥ר בִּשְׁעָרֶֽיךָ׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 11:
            text = 'כִּ֣י שֵֽׁשֶׁת־יָמִים֩ עָשָׂ֨ה יְהוָ֜ה אֶת־הַשָּׁמַ֣יִם וְאֶת־הָאָ֗רֶץ אֶת־הַיָּם֙ וְאֶת־כָּל־אֲשֶׁר־בָּ֔ם וַיָּ֖נַח בַּיּ֣וֹם הַשְּׁבִיעִ֑י עַל־כֵּ֗ן בֵּרַ֧ךְ יְהוָ֛ה אֶת־י֥וֹם הַשַּׁבָּ֖ת וַֽיְקַדְּשֵֽׁהוּ׃'
        elif book == 'Exodus' and chapter == 20 and pasuk == 12:
            pass # this one was fine
        elif book == 'Exodus' and chapter == 20 and pasuk == 13:
            text = 'לֹ֥א תִרְצָ֖ח לֹ֣א תִנְאָ֑ף לֹ֣א תִגְנֹ֔ב לֹֽא־תַעֲנֶ֥ה בְרֵֽעֲךָ֖ עֵ֥ד שָֽׁקֶר׃'
        elif book == 'Exodus' and chapter == 28 and pasuk == 1: # revii turned to zakef katon
            text = 'וְאַתָּ֡ה הַקְרֵ֣ב אֵלֶיךָ֩ אֶת־אַֽהֲרֹ֨ן אָחִ֜יךָ וְאֶת־בָּנָ֣יו אִתּ֗וֹ מִתּ֛וֹךְ בְּנֵ֥י יִשְׂרָאֵ֖ל לְכַֽהֲנוֹ־לִ֑י אַֽהֲרֹ֕ן נָדָ֧ב וַֽאֲבִיה֛וּא אֶלְעָזָ֥ר וְאִֽיתָמָ֖ר בְּנֵ֥י אַֽהֲרֹֽן׃'
        elif book == 'Leviticus' and chapter == 1 and pasuk == 3:  # used geresh mukdam, even though that is of emet
            text = 'אִם־עֹלָ֤ה קָרְבָּנוֹ֙ מִן־הַבָּקָ֔ר זָכָ֥ר תָּמִ֖ים יַקְרִיבֶ֑נּוּ אֶל־פֶּ֜תַח אֹ֤הֶל מוֹעֵד֙ יַקְרִ֣יב אֹת֔וֹ לִרְצֹנ֖וֹ לִפְנֵ֥י יְהוָֽה׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 7:
            text = 'אָֽנֹכִי֙ יְהוָ֣ה אֱלֹהֶ֔יךָ אֲשֶׁ֧ר הֽוֹצֵאתִ֛יךָ מֵאֶ֥רֶץ מִצְרַ֖יִם מִבֵּ֣ית עֲבָדִ֑ים לֹֽא־יִהְיֶ֥ה לְךָ֛ אֱלֹהִ֥ים אֲחֵרִ֖ים עַל־פָּנָֽי׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 8:
            text = 'לֹֽא־תַעֲשֶׂ֨ה לְךָ֥ פֶ֨סֶל֙ כָּל־תְּמוּנָ֔ה אֲשֶׁ֤ר בַּשָּׁמַ֨יִם֙ מִמַּ֔עַל וַֽאֲשֶׁ֥ר בָּאָ֖רֶץ מִתָּ֑חַת וַֽאֲשֶׁ֥ר בַּמַּ֖יִם מִתַּ֥חַת לָאָֽרֶץ׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 9:
            text = 'לֹֽא־תִשְׁתַּחֲוֶ֥ה לָהֶ֖ם וְלֹ֣א תָֽעָבְדֵ֑ם כִּ֣י אָֽנֹכִ֞י יְהוָ֤ה אֱלֹהֶ֨יךָ֙ אֵ֣ל קַנָּ֔א פֹּ֠קֵד עֲוֺ֨ן אָב֧וֹת עַל־בָּנִ֛ים וְעַל־שִׁלֵּשִׁ֥ים וְעַל־רִבֵּעִ֖ים לְשֹֽׂנְאָֽי׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 10:
            text = 'וְעֹ֥שֶׂה חֶ֖סֶד לַֽאֲלָפִ֑ים לְאֹֽהֲבַ֖י וּלְשֹֽׁמְרֵ֥י מִצְוֺתָֽי׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 12:
            text = 'שָׁמ֛וֹר אֶת־י֥וֹם הַשַּׁבָּ֖ת לְקַדְּשׁ֑וֹ כַּֽאֲשֶׁ֥ר צִוְּךָ֖ יְהוָ֥ה אֱלֹהֶֽיךָ׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 13:
            text = 'שֵׁ֤שֶׁת יָמִים֙ תַּֽעֲבֹ֔ד וְעָשִׂ֖יתָ כָּל־מְלַאכְתֶּֽךָ׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 14:
            text = 'וְיוֹם֙ הַשְּׁבִיעִ֔י שַׁבָּ֖ת לַֽיהוָ֣ה אֱלֹהֶ֑יךָ לֹ֣א תַֽעֲשֶׂ֣ה כָל־מְלָאכָ֡ה אַתָּ֣ה וּבִנְךָֽ־וּבִתֶּ֣ךָ וְעַבְדְּךָֽ־וַ֠אֲמָתֶךָ וְשֽׁוֹרְךָ֨ וַחֲמֹֽרְךָ֜ וְכָל־בְּהֶמְתֶּ֗ךָ וְגֵֽרְךָ֙ אֲשֶׁ֣ר בִּשְׁעָרֶ֔יךָ לְמַ֗עַן יָנ֛וּחַ עַבְדְּךָ֥ וַאֲמָֽתְךָ֖ כָּמֽוֹךָ׃'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 15:
            text = 'וְזָֽכַרְתָּ֗ כִּ֣י עֶ֤בֶד הָיִ֨יתָ֙ בְּאֶ֣רֶץ מִצְרַ֔יִם וַיֹּצִ֨אֲךָ֜ יְהוָ֤ה אֱלֹהֶ֨יךָ֙ מִשָּׁ֔ם בְּיָ֥ד חֲזָקָ֖ה וּבִזְרֹ֣עַ נְטוּיָ֑ה עַל־כֵּ֗ן צִוְּךָ֙ יְהוָ֣ה אֱלֹהֶ֔יךָ לַֽעֲשׂ֖וֹת אֶת־י֥וֹם הַשַּׁבָּֽת׃ {ס}'
        elif book == 'Deuteronomy' and chapter == 5 and pasuk == 17:
            text = 'לֹ֥א תִרְצָ֖ח וְלֹ֣א תִנְאָ֑ף וְלֹ֣א תִגְנֹ֔ב וְלֹֽא־תַעֲנֶ֥ה בְרֵֽעֲךָ֖ עֵ֥ד שָֽׁוְא׃ {ס}'
        elif book == 'Judges' and chapter == 13 and pasuk == 18: # tevir instead of silluq
            text = 'וַיֹּ֤אמֶר לוֹ֙ מַלְאַ֣ךְ יְהוָ֔ה לָ֥מָּה זֶּ֖ה תִּשְׁאַ֣ל לִשְׁמִ֑י וְהוּא־פֶֽלִאי׃'
        elif book == 'Isaiah' and chapter == 45 and pasuk == 1: # change munach on "lechoresh" to segolta and first zarqa to revia. see Wickes pg 136, correction
            text = 'כֹּה־אָמַ֣ר יְהוָ֗ה לִמְשִׁיחוֹ֮ לְכ֒וֹרֶשׁ֒ אֲשֶׁר־הֶחֱזַ֣קְתִּי בִֽימִינ֗וֹ לְרַד־לְפָנָיו֙ גּוֹיִ֔ם וּמָתְנֵ֥י מְלָכִ֖ים אֲפַתֵּ֑חַ לִפְתֹּ֤חַ לְפָנָיו֙ דְּלָתַ֔יִם וּשְׁעָרִ֖ים לֹ֥א יִסָּגֵֽרוּ׃'
        elif book == 'Jeremiah' and chapter == 28 and pasuk == 2:  # change second gershayim to zakef gadol
            text = 'כֹּֽה־אָמַ֞ר יְהוָ֧ה צְבָא֛וֹת אֱלֹהֵ֥י יִשְׂרָאֵ֖ל לֵאמֹ֑ר שָׁבַ֕רְתִּי אֶת־עֹ֖ל מֶ֥לֶךְ בָּבֶֽל׃'
        elif book == 'Jeremiah' and chapter == 48 and pasuk == 12:  # change foretone tipcha on hineh-yamim to a meteg
            text = 'לָכֵ֞ן הִנֵּֽה־יָמִ֤ים בָּאִים֙ נְאֻם־יְהוָ֔ה וְשִׁלַּחְתִּי־ל֥וֹ צֹעִ֖ים וְצֵעֻ֑הוּ וְכֵלָ֣יו יָרִ֔יקוּ וְנִבְלֵיהֶ֖ם יְנַפֵּֽצוּ׃'
        elif book == 'Jeremiah' and chapter == 48 and pasuk == 20:  # suppress syntax error due to strange bracketing
            text = 'הֹבִ֥ישׁ מוֹאָ֛ב כִּֽי־חַ֖תָּה הֵילִ֣ילוּ ׀ וּֽזְעָ֑קוּ הַגִּ֣ידוּ בְאַרְנ֔וֹן כִּ֥י שֻׁדַּ֖ד מוֹאָֽב׃'
        elif book == 'Obadiah' and chapter == 1 and pasuk == 1:  # fix missing tipcha in penultimate word
            text = 'חֲז֖וֹן עֹֽבַדְיָ֑ה כֹּֽה־אָמַר֩ אֲדֹנָ֨י יְהוִ֜ה לֶאֱד֗וֹם שְׁמוּעָ֨ה שָׁמַ֜עְנוּ מֵאֵ֤ת יְהוָה֙ וְצִיר֙ בַּגּוֹיִ֣ם שֻׁלָּ֔ח ק֛וּמוּ וְנָק֥וּמָה עָלֶ֖יהָ לַמִּלְחָמָֽה׃'
        elif book == 'Ecclesiastes' and chapter == 9 and pasuk == 18:  # change a mercha to tipcha at end
            text = 'טוֹבָ֥ה חָכְמָ֖ה מִכְּלֵ֣י קְרָ֑ב וְחוֹטֶ֣א אֶחָ֔ד יְאַבֵּ֖ד טוֹבָ֥ה הַרְבֵּֽה׃'
        elif book == 'Nehemiah' and chapter == 2 and pasuk == 13:  # change krei ketiv bracketing
            text = 'וָאֵצְאָ֨ה בְשַֽׁעַר־הַגַּ֜יא לַ֗יְלָה וְאֶל־פְּנֵי֙ עֵ֣ין הַתַּנִּ֔ין וְאֶל־שַׁ֖עַר הָאַשְׁפֹּ֑ת וָאֱהִ֨י שֹׂבֵ֜ר בְּחוֹמֹ֤ת יְרוּשָׁלִַ֙ם֙ אֲשֶׁר־המפרוצים הֵ֣ם ׀ פְּרוּצִ֔ים וּשְׁעָרֶ֖יהָ אֻכְּל֥וּ בָאֵֽשׁ׃'
        # special trup, change geresh (which was erroneously mukdam) paired with telisha gedola
        # into just a geresh. don't make special rules to parse a dual trup
        elif book == 'II Kings' and chapter == 17 and pasuk == 13:
            text = 'יָּ֣עַד יְהוָ֡ה בְּיִשְׂרָאֵ֣ל וּבִֽיהוּדָ֡ה בְּיַד֩ כָּל־נְבִיאֵ֨י כָל־חֹזֶ֜ה לֵאמֹ֗ר שֻׁ֜בוּ מִדַּרְכֵיכֶ֤ם הָֽרָעִים֙ וְשִׁמְרוּ֙ מִצְוֺתַ֣י חֻקּוֹתַ֔י כְּכָ֨ל־הַתּוֹרָ֔ה אֲשֶׁ֥ר צִוִּ֖יתִי אֶת־אֲבֹֽתֵיכֶ֑ם וַֽאֲשֶׁר֙ שָׁלַ֣חְתִּי אֲלֵיכֶ֔ם בְּיַ֖ד עֲבָדַ֥י הַנְּבִיאִֽים׃'
        elif book == 'II Kings' and chapter == 23 and pasuk == 36: # change kadma to pashta
            text = 'בֶּן־עֶשְׂרִ֨ים וְחָמֵ֤שׁ שָׁנָה֙ יְהֽוֹיָקִ֣ים בְּמָלְכ֔וֹ וְאַחַ֤ת עֶשְׂרֵה֙ שָׁנָ֔ה מָלַ֖ךְ בִּירֽוּשָׁלִָ֑ם וְשֵׁ֣ם אִמּ֔וֹ זבידה (זְבוּדָּ֥ה) בַת־פְּדָיָ֖ה מִן־רוּמָֽה׃'
        elif book == 'I Chronicles' and chapter == 10 and pasuk == 1:  # change second etnachta to mahpach
            text = 'וּפְלִשְׁתִּ֖ים נִלְחֲמ֣וּ בְיִשְׂרָאֵ֑ל וַיָּ֤נָס אִֽישׁ־יִשְׂרָאֵל֙ מִפְּנֵ֣י פְלִשְׁתִּ֔ים וַיִּפְּל֥וּ חֲלָלִ֖ים בְּהַ֥ר גִּלְבֹּֽעַ׃'
        elif book == 'II Chronicles' and chapter == 7 and pasuk == 5:  # change revia to segolta
            text = 'וַיִּזְבַּ֞ח הַמֶּ֣לֶךְ שְׁלֹמֹה֮ אֶת־זֶ֣בַח הַבָּקָר֒ עֶשְׂרִ֤ים וּשְׁנַ֨יִם֙ אֶ֔לֶף וְצֹ֕אן מֵאָ֥ה וְעֶשְׂרִ֖ים אָ֑לֶף וַֽיַּחְנְכוּ֙ אֶת־בֵּ֣ית הָֽאֱלֹהִ֔ים הַמֶּ֖לֶךְ וְכָל־הָעָֽם׃'
        elif book == 'II Chronicles' and chapter == 17 and pasuk == 11:  # own emendation misevara. and fixed syntax error
                # changed tzon eilim from zakef gadol katon to zakef katon revia
            text = 'וּמִן־פְּלִשְׁתִּ֗ים מְבִיאִ֧ים לִיהֽוֹשָׁפָ֛ט מִנְחָ֖ה וְכֶ֣סֶף מַשָּׂ֑א גַּ֣ם הָֽעַרְבִיאִ֗ים מְבִיאִ֥ים לוֹ֙ צֹ֔אן אֵילִ֗ים שִׁבְעַ֤ת אֲלָפִים֙ וּשְׁבַ֣ע מֵא֔וֹת וּתְיָשִׁ֕ים שִׁבְעַ֥ת אֲלָפִ֖ים וּשְׁבַ֥ע מֵאֽוֹת׃'
        text = preprocess(text)

        lexer.input(text)
        marked = ' '.join(['(' + i.value + ', ' + i.type + ')' for i in lexer])
        # print(i, marked)

        result = yacc.parse(text)
        d = dict()
        tree = encode(result)
        bitcode = bit_encode(result, [])
        bitcode = ''.join(bitcode)

        x = iso_trees.find_one({'key': bitcode})
        x2 = iso_trees2.find_one({'key': bitcode})
        iso_verses = x['verses']
        iso_verses2 = x2['verses']
        iso_html = '<table><tr><td>'
        iso_html += 'Isomorphic Trees\n'.join(['<a href="' + verse + '">' + verse + '</a><br/>' for verse in iso_verses])
        iso_html += '</td>Isomorphic Trees\n'.join(['<a href="' + verse + '">' + verse + '</a><br/>' for verse in iso_verses2])
        iso_html += '</tr></table>'
        tagged = marked

        return tree, text, tagged, next, prev, iso_html