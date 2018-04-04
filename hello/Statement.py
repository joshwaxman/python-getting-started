from typing import List, Tuple, Union
import regex as re
import unittest
from hello.EnglishDictionary import *

class Statement(object):
    def __init__(self, english: Union[str, List[str]], hebrew: str, hebrew_gloss:str='', startsBold:bool = True):
        self.hebrew: str = hebrew
        self.hebrew_gloss = hebrew_gloss
        self.tokens: List[List[str]] = []
        self.verbList: List[str] = ['said']

        if isinstance(english, list):
            self.english: List[str] = english.copy() # lists are mutable so this is safer
            self.english_raw = english
        else:
            self.english = Statement.generateEnglishIterpolated(english)

        self.d = dict()

    def getEnglishHTML(self):
        # we need to recover the html, since the raw html was processed coming in
        # or the Statement might be the result of some prior manipulation
        if self.getStartsBold():
            bold = 0
        else:
            bold = 1

        return ' '.join(['<b>' + s + '</b>' if i % 2 == bold else s for i, s in enumerate(self.getEnglish())])

    def getEnglishFlat(self):
        ' This will rejoin the LITERAL and GLOSS sections of English for a plain text in which to search'
        return ' '.join(e[1] for e in self.english)

    def getDictionary(self):
        return self.d

    def getStartsBold(self):
        return self.startsBold

    def removeLeadingGloss(self):
        if not self.startsBold:
            self.startsBold = True
            del self.english[0]

    def setStatements(self, english: Union[str, List[str]], hebrew: str, startsBold:bool = True):
        self.__init__(english, hebrew, '', startsBold)

    def getHebrew(self) -> str:
        return self.hebrew

    def getEnglish(self) -> List[str]:
        return self.english

    def getEnglishLiteral(self) -> str:
            return [sentence for gloss, sentence in self.english if gloss == 'LITERAL']

    def setHebrew(self, heb):
        self.hebrew = heb

    def cutHebrew(self, pos: int):
        self.hebrew = self.hebrew[pos: ]

    @staticmethod
    def generateEnglishIterpolated(eng: str) -> Tuple[bool, List[Tuple[str, str]]]:
        # at this point, it is a good idea to strip attribution of explanations to various
        # Acharonim, Rishonim or Geonim from gloss text. It appears in the form of
        # parentheses around italics. E.g. (<i>Tosefot HaRosh</i>) We strip it because it
        # is not helpful for translation and it can hinder in terms of identifying the named
        # Tannaim or Amoraim in the gloss text.

        eng = re.sub(r' \(<i>(.*?)</i>\)', r'', eng)

        # replace contractions because we don't like
        # how our tokenizer / tagger deals with them
        eng = eng.replace("don't", "do not")
        eng = eng.replace("Don't", "Do not")
        eng = eng.replace("can't", "cannot")
        eng = eng.replace("Can't", "Cannot")
        eng = eng.replace("won't", "will not")
        eng = eng.replace("Won't", "Will not")
        eng = eng.replace("Shouldn't", "Should not")
        eng = eng.replace("it's", "it is")
        eng = eng.replace("It's", "It is")

        # replace special characters like ellipses
        eng = eng.replace("…", "...")
        eng = eng.replace('“', '"')
        eng = eng.replace('”', '"')
        eng = eng.replace('”', '"')
        eng = eng.replace('’’', '"')

        eng = eng.replace('``', '"')

        eng = eng.replace("''", '"')
        eng = eng.replace('’', '') # strip out quote from Ya’akov

        # now on to dividing bold from non-bold
        startsLiteral = eng.startswith('<b>')
        literal = startsLiteral

        boldStartingSentences: List = eng.split('<b>')

        paragraph: List = []
        if not startsLiteral:
            paragraph.append(('GLOSS', boldStartingSentences[0]))

        # regardless remove the first sentence, because if
        # started with <b> then the first sentence would
        # be the empty string.
        boldStartingSentences = boldStartingSentences[1:]

        for sentence in boldStartingSentences:
            s = sentence.split('</b>')
            paragraph.append(('LITERAL', s[0].strip()))
            if len(s) == 2 and s[1].strip() != '':
                paragraph.append(('GLOSS', s[1].strip()))

        return paragraph

    def __str__(self):
        return "hebrew: " + self.getHebrew() + "\nenglish: " + ' '.join(self.getEnglishLiteral()) + '\n' + str(self.getDictionary())

    def getTokens(self):
        if self.tokens == []:
            self.identifyRabbis()
        return self.tokens

    def identifyRabbis(self):
        # Strategy:
        # starting in the English interpolated text, look for capitalized names, and look specifically for sequences
        # of capitalized words. For now, we will spit them out. Eventually, we want to tag the statement with them

        # we tokenize using nltk's tokenize
        import nltk.tokenize
        eng: List[str] = self.getEnglish()



        self.tokens: List[List[Tuple[str], str]] = [[] for i in range(len(eng))]
        ed = EnglishDictionary()
        for i, (gloss, e) in enumerate(eng):
            words = nltk.tokenize.word_tokenize(e)
            prev_word = ''
            full_name = ''
            current_word = 0
            while current_word < len(words):
                w = words[current_word]
                # is it a name?
                if w not in ed and (w[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZḤ' or w == 'bar' or w == 'b.'):
                    n = words[current_word]
                    self.tokens[i].append((gloss, n, 'NAME'))
                    current_word += 1
                # is it a verb?
                elif w in self.verbList:
                    verb, num_tokens = self.capture_verb(words[current_word : ])
                    current_word += num_tokens
                    self.tokens[i].append((gloss, verb, "VERB"))
                elif self.contains_transliteration(words[current_word: ]):
                    n, t = self.capture_transliteration(words[current_word:])
                    current_word += t
                    self.tokens[i].append((gloss, n, 'TRANSLITERATION'))
                else:
                    n = words[current_word]
                    self.tokens[i].append((gloss, n, 'UNTAGGED'))
                    current_word += 1

            def consolidateSequence(sentence: List[Tuple[str]]):
                result: List[Tuple[str]] = []
                prev_tag = ''
                for i, (gloss, word, tag) in enumerate(sentence):
                    if tag == prev_tag:
                        if word in '''.,:\';)!?''' or result[-1][1].endswith('('):
                            newword = word
                        else:
                            newword = ' ' + word
                        result[-1] = (gloss, result[-1][1] + newword, tag)
                    else:
                        result.append((gloss, word, tag))
                    prev_tag = tag
                return result

            self.tokens[i] = consolidateSequence(self.tokens[i])
            rulesApplied = True
            #while not rulesApplied:


        #print()
        #print(self.tokens)

    def capture_name(self, words: List[str]) -> Tuple[str, int]:
        num_tokens = 0
        full_name = ''

        name_continuations: List[str] = [ ', son of', ', the son of']

        #print('got here to capture_name', words[start])
        # keep going forward, adding additional tokens to name until terminal condition
        i = 0

        # Sentences start with capitals, which we don't want to capture.
        # In Sefaria, many many sentences begin with Therefore, In, and so on for other functioning words. We advance on those.
        #common_sentence_beginnings: List[str] = [ 'Therefore', 'It', 'We', 'The', 'If', 'But', 'And', 'No', 'Consequently', 'In', 'With', 'By',  ]
        #if words[i] in common_sentence_beginnings:
#            i += 1

        ed = EnglishDictionary()

        while i < len(words):
            w = words[i]
            if w[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZḤ' and w not in ed:
                full_name = full_name + ' ' + w
                num_tokens += 1
                i += 1
            else:
                if self.contains_subname(words[i: ]):
                    n, t = self.capture_subname(words[i: ])
                    if n.startswith(','):
                        full_name = full_name + n
                    else:
                        full_name = full_name + ' ' + n
                    num_tokens += t
                    i += t
                else:
                    break

        return full_name.strip(), num_tokens

    def contains_subname(self, words: List[str]) -> bool:
        # maybe it is a lowercase continuation of the name?
        name_continuations: List[str] = [', son of', ', the son of', 'bar']

        for cont in name_continuations:
            c = cont.split()
            if c == words[ : len(c)]:
                return True

        return False

    def capture_subname(self, words: List[str]) -> Tuple[str, int]:
        # maybe it is a lowercase continuation of the name?
        name_continuations: List[str] = [', son of', ', the son of', 'bar']

        for i in range(len(words)):
            for cont in name_continuations:
                c = cont.split()
                if c == words[i: i + len(c)]:
                    return cont, len(c)

    def contains_transliteration(self, words: List[str]) -> bool:
        return words[0:3] == ['<', 'i', '>']

    def capture_transliteration(self, words: List[str]) -> Tuple[str, int]:
        # eat first three words, which are the open <i>
        words = words[3: ]

        # get position of end italics, that is </i>
        if '<' in words:
            pos = words.index('<')
        else:
            pos = len(words) - 1
        #print(words[: pos])

        transliteration = ' '.join(words[: pos])
        # pos is number of words, and also have open and close italics tags, each of three
        return transliteration, 3 + pos + 3

    def capture_verb(self, words: List[str]) -> str:
        num_tokens = 0
        full_verb = ''
        #print('got here to capture_name', words[start])
        # keep going forward, adding additional tokens to name until terminal condition

        verbs = ['said in the name of', 'said', 'strongly objected to', 'raises an objection', 'thought to say']

        for i in range(len(words)):
            for verb in verbs:
                v = verb.split()
                if v == words[i: i + len(v)]:
                    return verb, len(v)



class TestStatement(unittest.TestCase):
    def test_getters(self):
        eng = "<b>Rav Yitzḥak bar Shmuel said in the name of Rav: The night consists of three watches, and over each and every watch the Holy One, Blessed be He sits and roars like a lion,</b> because the Temple service was connected to the changing of these watches (<i>Tosefot HaRosh</i>), <b>and says: “Woe to Me, that due to their sins I destroyed My house, burned My Temple and exiled them among the nations of the world.”</b>"
        heb = "אמר רב יצחק בר שמואל משמיה דרב ג' משמרות הוי הלילה ועל כל משמר ומשמר יושב הקדוש ברוך הוא ושואג כארי ואומר אוי לבנים שבעונותיהם החרבתי את ביתי ושרפתי את היכלי והגליתים לבין אומות העולם:"

        proc = Statement(eng, heb)

        expected: List[str] = [('LITERAL','Rav Yitzḥak bar Shmuel said in the name of Rav: The night consists of three watches, and over each and every watch the Holy One, Blessed be He sits and roars like a lion,'), \
                               ('GLOSS', 'because the Temple service was connected to the changing of these watches,'), \
                               ('LITERAL', 'and says: "Woe to Me, that due to their sins I destroyed My house, burned My Temple and exiled them among the nations of the world."')]

        result: List[str] = proc.getEnglish()

        self.maxDiff = None
        self.assertEqual(result, expected)

        self.assertEqual(proc.getHebrew(), heb)
        result = proc.getEnglishLiteral()

        expected = ['Rav Yitzḥak bar Shmuel said in the name of Rav: The night consists of three watches, and over each and every watch the Holy One, Blessed be He sits and roars like a lion,', \
                    'and says: "Woe to Me, that due to their sins I destroyed My house, burned My Temple and exiled them among the nations of the world."']
        self.assertEqual(result, expected)

    def test_generateEnglishIterpolated(self):
        eng = "<strong>GEMARA:</strong> The Mishna opens with the laws concerning the appropriate time to recite <i>Shema</i> with the question: From when does one recite <i>Shema</i> in the evening? With regard to this question, the Gemara asks: <b>On the basis of what</b> prior knowledge <b>does</b> the <b><i>tanna</i></b> of our mishna ask: <b>From when?</b> It would seem from his question that the obligation to recite <i>Shema</i> in the evening was already established, and that the <i>tanna</i> seeks only to clarify details that relate to it. But our mishna is the very first mishna in the Talmud."
        english = Statement.generateEnglishIterpolated(eng)

    def test_identifyRabbis(self):
        eng = "<b>Rav Yitzḥak bar Shmuel said in the name of Rav: The night consists of three watches, and over each and every watch the Holy One, Blessed be He sits and roars like a lion,</b> because the Temple service was connected to the changing of these watches (<i>Tosefot HaRosh</i>), <b>and says: “Woe to Me, that due to their sins I destroyed My house, burned My Temple and exiled them among the nations of the world.”</b>"
        heb = "אמר רב יצחק בר שמואל משמיה דרב ג' משמרות הוי הלילה ועל כל משמר ומשמר יושב הקדוש ברוך הוא ושואג כארי ואומר אוי לבנים שבעונותיהם החרבתי את ביתי ושרפתי את היכלי והגליתים לבין אומות העולם:"

        proc = Statement(eng, heb)
        proc.identifyRabbis()

    def test_bar(self):
        heb = "כדר' יעקב בר אידי דר' יעקב בר אידי רמי כתיב (בראשית כח, טו) והנה אנכי עמך ושמרתיך בכל אשר תלך וכתיב (בראשית לב, ח) ויירא יעקב מאד אמר שמא יגרום החטא"
        eng = "The Gemara cites a proof that there is room for one to fear lest he commit a transgression in the future <b>in accordance with</b> the opinion of <b>Rabbi Yaakov b. Idi, as Rabbi Ya’akov bar Idi raised a contradiction</b> between two verses. <b>It is written</b> that God told Jacob in his vision of the ladder: <b>“Behold, I am with you and I guard you wherever you go”</b> (Genesis 28:15), yet when Jacob returned to Canaan and realized that Esau was coming to greet him, <b>it is written: “And Jacob became very afraid,</b> and he was pained” (Genesis 32:8). Why did Jacob not rely on God’s promise? Jacob had concerns and <b>said</b> to himself: <b>Lest a transgression</b> that I might have committed after God made His promise to me <b>will cause</b> God to revoke His promise of protection."
        proc = Statement(eng, heb)
        tokens = proc.getTokens()
        print(tokens)



def main():
    eng = "<b>Rav Yitzḥak bar Shmuel said in the name of Rav: The night consists of three watches, and over each and every watch the Holy One, Blessed be He sits and roars like a lion,</b> because the Temple service was connected to the changing of these watches (<i>Tosefot HaRosh</i>), <b>and says: “Woe to Me, that due to their sins I destroyed My house, burned My Temple and exiled them among the nations of the world.”</b>"
    engLiteral = "Rav Yitzḥak bar Shmuel said in the name of Rav: The night consists of three watches, and over each and every watch the Holy One, Blessed be He sits and roars like a lion, and says: “Woe to Me, that due to their sins I destroyed My house, burned My Temple and exiled them among the nations of the world.”"
    heb = "אמר רב יצחק בר שמואל משמיה דרב ג' משמרות הוי הלילה ועל כל משמר ומשמר יושב הקדוש ברוך הוא ושואג כארי ואומר אוי לבנים שבעונותיהם החרבתי את ביתי ושרפתי את היכלי והגליתים לבין אומות העולם:"

    proc = Statement(eng, heb)

    print(proc.getEnglishLiteral())

#    heb = "אמר רב אחא בריה דרב איקא לפי שאין דרכן של בני אדם להתחכך בכתלים"
#    eng = "<b>Rav Aḥa, son of Rav Ika, says:</b> It is <b>because it is not the<b> typical <b>manner of people to rub against walls,</b> but to keep a certain distance from them. Therefore, if a pedestrian is wounded by the thorns, it is considered an unusual accident, for which the owner of the fence is not liable."
#    proc = Statement(eng, heb)
#    print(proc.getTokens())

#main()

if __name__ == '__main__':
    unittest.main()



