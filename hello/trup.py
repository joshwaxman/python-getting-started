from pymongo import MongoClient

import re
# example ply here: https://www.dabeaz.com/ply/example.html

tokens = tuple('MAHPACH PASHTA MUNACH ZAKEF_KATON ZAKEF_GADOL MERCHA TIPCHA ETNACHTA ' \
                'DARGA TEVIR KADMA GERESH GERSHAYIM ZARQA SEGOLTA REVIA MUNACH_LEGARMEIH ' \
                'SILLUQ YETIV TELISHA_GEDOLA TELISHA_KETANA PAZER GERESH_MUKDAM ETNACH_HAFUCH ' \
                'SHALSHELET MERCHA_KEFULA GALGAL KARNEI_PARA DECHI OLEH ILUY TZINORIT SOF_PASUK'.split())
#print('tokens:', tokens)

alephbet = '־אבגדהוזחטיכלמנסעפצקרשתץךףםן' + 'ְֱֲֳִֵֶַָֹּׁׂ' + 'ֽ'# last is meteg/silluq

RBEGIN = '[' + alephbet + ']*'
REND = RBEGIN

# Tokens
t_MAHPACH = RBEGIN + '֤' + REND
t_PASHTA = RBEGIN + r'֙' + '(' + RBEGIN + r'֙' + ')?' + REND
t_MUNACH_LEGARMEIH = RBEGIN +r'֣' + REND + r'׀'
t_MUNACH = RBEGIN +r'֣' + REND # but if trailer == '׀ ' should be munach_legarmeih...
t_ZAKEF_GADOL = RBEGIN +r'֕' + REND
t_ZAKEF_KATON = RBEGIN +r'֔' + REND
t_MERCHA = RBEGIN + r'֥' + REND
t_TIPCHA = RBEGIN + r'֖' + REND
t_ETNACHTA = RBEGIN + r'֑' + REND
t_DARGA = RBEGIN + r'֧' + REND
t_TEVIR = RBEGIN + r'֛' + REND
t_KADMA = RBEGIN + r'֨' + REND
t_GERESH = RBEGIN + r'֜' + REND
t_GERSHAYIM = RBEGIN + r'֞' + REND
t_ZARQA = RBEGIN + r'֘' + REND
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
t_SHALSHELET = RBEGIN + r'֓' + REND
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
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
from ply.lex import LexToken
lexer =  lex.lex(reflags=re.UNICODE | re.VERBOSE)

# can download zip of text from here: http://ota.ox.ac.uk/desc/0525
# in Hebrew here: https://www.mechon-mamre.org/c/ct/cu0101.htm
# Genesis 1:1
text = 'בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃'
lexer.input(text)
marked = ' '.join(['(' + i.value + ', ' + i.type + ')' for i in lexer])
print(marked)





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
            | zakef_katon_clause etnachta_clause
            | zakef_gadol_clause etnachta_clause
            | segolta_clause etnachta_clause
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
                | TELISHA_KETANA'''
    # print(len(p.slice))
    p[0] = p.slice[1]

def p_tipcha_clause(p):
    '''tipcha_clause : mesharet tipcha
                       | mesharet mesharet tipcha
                       | tipcha
                       | tevir_clause tipcha_clause
                       | revia_clause tipcha_clause
                       | pashta_clause tipcha_clause'''
    p[0] = tuple(['TIPCHA'] + p[1:])


def p_tipcha(p):
    '''tipcha : TIPCHA'''
    p[0] = p.slice[1]


def p_revia_clause(p):
    '''revia_clause : mesharet revia
                    | mesharet mesharet revia
                    | revia
                    | geresh_clause revia_clause
                    | gershayim_clause revia_clause
                    | telisha_gedola_clause revia_clause
                    | pazer_clause revia_clause
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


def p_zakef_katon(p):
    '''zakef_katon : ZAKEF_KATON'''
    p[0] = p.slice[1]


def p_pashta_clause(p):
    '''pashta_clause : gershayim_clause pashta_clause
                       | geresh_clause pashta_clause
                       | telisha_gedola_clause pashta_clause
                       | pazer_clause pashta_clause
                       | mesharet pashta
                       | mesharet mesharet pashta
                       | mesharet mesharet mesharet pashta
                       | pashta'''
    p[0] = tuple(['PASHTA'] + p[1:])


def p_pashta(p):
    '''pashta : PASHTA'''
    p[0] = p.slice[1]


def p_geresh_clause(p):
    '''geresh_clause : mesharet geresh
                     | mesharet mesharet geresh
                     | mesharet mesharet mesharet geresh
                     | geresh'''
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
                    | tevir
                    | geresh_clause tevir_clause
                    | gershayim_clause tevir_clause
                    | telisha_gedola_clause tevir_clause
                    | pazer_clause tevir_clause'''
    p[0] = tuple(['TEVIR'] + p[1:])


def p_tevir(p):
    '''tevir : TEVIR'''
    p[0] = p.slice[1]


def p_telisha_gedola_clause(p):
    '''telisha_gedola_clause : telisha_gedola'''
    p[0] = tuple(['TELISHA_GEDOLA'] + p[1:])


def p_telisha_gedola(p):
    '''telisha_gedola : TELISHA_GEDOLA'''
    p[0] = p.slice[1]


def p_pazer_clause(p):
    '''pazer_clause : pazer
                    | mesharet pazer'''
    p[0] = tuple(['PAZER'] + p[1:])


def p_pazer(p):
    '''pazer : PAZER'''
    p[0] = p.slice[1]


def p_munach_legarmeih_clause(p):
    '''munach_legarmeih_clause : mesharet munach_legarmeih
                               | mesharet mesharet munach_legarmeih
                               | munach_legarmeih'''
    p[0] = tuple(['MUNACH_LEGARMEIH'] + p[1:])


def p_munach_legarmeih(p):
    '''munach_legarmeih : MUNACH_LEGARMEIH'''
    p[0] = p.slice[1]


def p_segolta_clause(p):
    '''segolta_clause : zarqa_clause segolta_clause
                      | revia_clause segolta_clause
                      | mesharet segolta
                      | mesharet mesharet segolta
                      | segolta'''
    p[0] = tuple(['SEGOLTA'] + p[1:])


def p_segolta(p):
    '''segolta : SEGOLTA'''
    p[0] = p.slice[1]


def p_zarqa_clause(p):
    '''zarqa_clause : mesharet zarqa
                    | mesharet mesharet zarqa
                    | mesharet mesharet mesharet zarqa
                    | zarqa
                    | geresh_clause zarqa_clause
                    | gershayim_clause zarqa_clause
                    | telisha_gedola_clause zarqa_clause
                    | pazer_clause zarqa_clause'''
    p[0] = tuple(['ZARQA'] + p[1:])


def p_zarqa(p):
    '''zarqa : ZARQA'''
    p[0] = p.slice[1]


def p_zakef_gadol_clause(p):
    '''zakef_gadol_clause : zakef_gadol
                          | mesharet zakef_gadol
                          | pashta_clause zakef_gadol_clause'''

# many additions on the basis of a strange pattern of pashta munach zakef gadol
    p[0] = tuple(['ZAKEF_GADOL'] + p[1:])


def p_zakef_gadol(p):
    '''zakef_gadol : ZAKEF_GADOL'''
    p[0] = p.slice[1]



def p_error(p):
    global i, pasuk, marked

    if p:
        print("Syntax error at '%s'" % p.value)
#        print(chapter, verse_num, pasuk, marked)
#        print()
    else:
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




books = 'Genesis Exodus Leviticus Numbers Deuteronomy ' \
    'Joshua Judges Isaiah Jeremiah Ezekiel ' \
        'Hosea Joel Amos Obadiah Jonah Micah Nahum ' \
        'Habakkuk Zephaniah Haggai Zechariah Malachi ' \
        'Psalms Job Proverbs Ruth Ecclesiastes ' \
        'Lamentations Esther Daniel Ezra Nehemiah'.split() + ['Song of Songs', 'I Samuel',
                                                              'I Kings',
                                                              'I Chronicles'
]


def getTree(verse):
    client = MongoClient(
        "mongodb://mivami:Talmud1%@talmud-shard-00-00-ol0w9.mongodb.net:27017,talmud-shard-00-01-ol0w9.mongodb.net:27017,talmud-shard-00-02-ol0w9.mongodb.net:27017/admin?replicaSet=Talmud-shard-0&ssl=true")
    db = client.sefaria
    texts = db.texts
    s = verse.split()
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
            next = book + ' ' + str(chapter) + ':' + str(verse_num + 1)
        else:
            next = ''
        prev = ''
        lexer.input(text)
        marked = ' '.join(['(' + i.value + ', ' + i.type + ')' for i in lexer])
        # print(i, marked)

        result = yacc.parse(text)
        d = dict()
        tree = encode(result)
        tagged = marked

        return tree, text, tagged, next, prev