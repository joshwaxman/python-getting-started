import nltk
#from nltk.corpus import words as nltk_words

# EnglishDictionary is a Singleton class

class EnglishDictionary(object):
    from nltk.corpus import words as nltk_words
    __instance = None
    def __new__(cls):
        if EnglishDictionary.__instance is None:
            EnglishDictionary.__instance = object.__new__(cls)

            # also load the dictionary here
            cls.dictionary = dict.fromkeys(nltk_words.words(), None)
            print(cls.dictionary)
            cls.dictionary.pop('rabbi', None)
            cls.dictionary.pop('bar', None)

            #EnglishDictionary.__instance.val = val
        return EnglishDictionary.__instance

    def __contains__(self, item):
        try:
            if item == "Rabbi": # even though in dict, return fa;
                return False

            x = self.dictionary[item.lower()]
            return True
        except KeyError:
            return False

def main():
    a = EnglishDictionary()
    b = EnglishDictionary()
    print('Hello' in a)
    print('hellop' in a)
    print('rabbi' in a) # gives false because of pop! hooray!
    print('rav' in a)  # gives false! hooray!
    print('R' in a)  # gives false! hooray!

main()