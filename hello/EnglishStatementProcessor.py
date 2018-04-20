# the focus here is as a catch all.
# We will look for specific regex patterned in the flat English text,
# not care about the Hebrew text, and try to get as much coverage as
# we can in as little time as possible.
# we will just have a list, in lexicographically descending order, of
# phrases indicating that X is citing Y is citing Z, or the X is refuting Y,
# and so on.

from typing import Match, Pattern

import regex
from hello.Statement import Statement
from hello.StatementProcessor import *
class EnglishStatementProcessor(AmoraicStatementProcessor):
    def recognize(self) -> bool:
        st: Statement = self.getStatement()
        eng: List[str] = st.getEnglishFlat()
        # 1)
        # example, Horayot 5a: Rabbi Meir says:
        # that is, a NAME pattern of Xxxx Yyyy followed by the word says
        # NAME might also follow pattern of X bar Y

        # note: nothing would be added to the dictionary for a bare
        # statement, unless we can establish a dispute among parties
        # But that requires context. A separate pass would be required
        # to analyze the discourse
        NAME = r'((?:[A-ZḤ][a-zḥ]*)(?: ?(?:[A-ZḤ][a-zḥ]*|, the son of|, son of|ben|bar|b\\.)*)*)'
        r = NAME + ' says:'
        if regex.match(r, eng):
            return True

        # 2)
        # example, Horayot 5a: Rabbi Shimon ben Elazar says in the name of Rabbi Meir:
        r = NAME + ' says in the name of ' + NAME + ":"
        if regex.match(r, eng):
            return True

        # 3)
        # example, Rav Ashi said:
        r = NAME + ' said:'
        if regex.match(r, eng):
            return True

        # 4)
        # example, Rav Shabba said to Rav Kahana:
        r = NAME + ' said to ' + NAME + ":"
        if regex.match(r, eng):
            return True

        #5)
        # example, # Rav Ḥisda said that Rabbi Zeira said that Rav Yirmeya said that Rav said: It is Rabbi Meir,
        # this example is also attribution of a separate statement, but too complex for now
        r = NAME + ' said that ' + NAME + " said that " + NAME + ' said that ' + NAME + ' said:'
        if regex.match(r, eng):
            return True

        return False

    def extractAll(self): # -> List[Dict[str]]:
        results: List[Dict[str]] = []

        st: Statement = self.getStatement()
        eng: List[str] = st.getEnglishFlat()
        # 1)
        # example, Horayot 5a: Rabbi Meir says:
        # that is, a NAME pattern of Xxxx Yyyy followed by the word says
        # NAME might also follow pattern of X bar Y

        # note: nothing would be added to the dictionary for a bare
        # statement, unless we can establish a dispute among parties
        # But that requires context. A separate pass would be required
        # to analyze the discourse
        NAME = r'((?:[A-ZḤ][a-zḥ]*)(?: (?:[A-ZḤ][a-zḥ]*|ben|bar|b\.)*)*)'
        #NAME = r'(([A-ZḤ][a-zḥ]*)( ([A-ZḤ][a-zḥ]*|ben|bar|b\.)*))'
        r = NAME + ' says:'

        nodes = set()
        edges = list()

        m: Match = None
        for m in regex.finditer(r, eng):
            nodes.add(m.groups(0)[0])

        # 2)
        # example, Horayot 5a: Rabbi Shimon ben Elazar says in the name of Rabbi Meir:
        r = NAME + ' says in the name of ' + NAME + " :"
        for m in regex.finditer(r, eng):
            source = m.groups(0)[0]
            target = m.groups(0)[1]
            nodes.add(source)
            nodes.add(target)
            edges.append({'source': source, 'target': target, 'label': 'cites'})

        # 3)
        # example, Rav Ashi said:
        r = NAME + ' said:'
        for m in regex.finditer(r, eng):
            nodes.add(m.groups(0)[0])

        # 4)
        # example, Rav Shabba said to Rav Kahana:
        r = NAME + ' said to ' + NAME + " :"
        for m in regex.finditer(r, eng):
            source = m.groups(0)[0]
            target = m.groups(0)[1]
            nodes.add(source)
            nodes.add(target)
            edges.append({'source': source, 'target': target, 'label': 'speaks_to'})

        #5a)
        # single citation, such as:
        # Horayot 10b:
        # Rabba bar bar Ḥana said that Rabbi Yoḥanan said
        r = NAME + ' said that ' + NAME + " said :"
        for m in regex.finditer(r, eng):
            source = m.groups(0)[0]
            target = m.groups(0)[1]
            nodes.add(source)
            nodes.add(target)
            edges.append({'source': source, 'target': target, 'label': 'cites'})



        #5b )
        # example, # Rav Ḥisda said that Rabbi Zeira said that Rav Yirmeya said that Rav said: It is Rabbi Meir,
        # this example is also attribution of a separate statement, but too complex for now
        r = NAME + ' said that ' + NAME + " said that " + NAME + ' said that ' + NAME + ' said :'
        for m in regex.finditer(r, eng):
            source = m.groups(0)[0]
            target1 = m.groups(0)[1]
            target2 = m.groups(0)[2]
            target3 = m.groups(0)[2]
            nodes.add(source)
            nodes.add(target1)
            nodes.add(target2)
            nodes.add(target3)
            edges.append({'source': source, 'target': target1, 'label': 'cites'})
            edges.append({'source': target1, 'target': target2, 'label': 'cites'})
            edges.append({'source': target2, 'target': target3, 'label': 'cites'})
            # indirect citation
            edges.append({'source': source, 'target': target2, 'label': 'indirectly_cites'})
            edges.append({'source': source, 'target': target3, 'label': 'indirectly_cites'})
            edges.append({'source': target1, 'target': target3, 'label': 'indirectly_cites'})

        #6)
        # simple attribution
        # example, # Rav said: It is Rabbi Meir,
        # this example is also attribution of a separate statement, but too complex for now
        r = NAME + ' said: It is ' + NAME
        for m in regex.finditer(r, eng):
            source = m.groups(0)[0]
            target = m.groups(0)[1]
            nodes.add(source)
            nodes.add(target)
            edges.append({'source': source, 'target': target, 'label': 'attributes'})

        #7)
        # inquiry
        # example, Horayot 9a,
        # Ravina raised a dilemma before Rav Naḥman bar Yitzḥak
        r = NAME + ' raised a dilemma before ' + NAME
        for m in regex.finditer(r, eng):
            source = m.groups(0)[0]
            target = m.groups(0)[1]
            nodes.add(source)
            nodes.add(target)
            edges.append({'source': source, 'target': target, 'label': 'inquires'})


        #8)
        # joint statement:
        # example, Horayot 9a: Abaye and Rava both say
        r = NAME + ' and ' + NAME + ' both say'
        for m in regex.finditer(r, eng):
            source = m.groups(0)[0]
            target = m.groups(0)[1]
            nodes.add(source)
            nodes.add(target)
            edges.append({'source': source, 'target': target, 'label': 'joint_statement'})
            edges.append({'source': target, 'target': source, 'label': 'joint_statement'})

        return nodes, edges


def main():
    englishText = '''
    Rabbi Shimon ben Elazar says in the name of Rabbi Meir: blah blah
    Rabbi Meir says: This is a statement;       
    Rav Ḥisda said that Rabbi Zeira said that Rav Yirmeya said that Rav said: It is Rabbi Meir,
    Ravina raised a dilemma before Rav Naḥman bar Yitzḥak
    '''

    st = Statement(englishText, '')
    p = EnglishStatementProcessor(st)
    nodes, edges = p.extractAll()
    print(nodes, edges)

#main()