
def convert(s):
    heb = 'שנבגקכעיןחלךצמםפ/רדאוהסטז'

#    for letter in s:


    return ''.join(reversed(([heb[ord(letter) - ord('a')] for letter in s if ord(letter) - ord('a') < len(heb)])))

