
def convert(s):
    heb = 'שנבגקכעיןחלךצמםפ/רדאוהסטז'

    result = []

    for letter in s:
        if 0 <= ord(letter) - ord('a') < len(heb):
            result.append(heb[ord(letter) - ord('a')])
        else:
            result.append(letter)

    return ''.join(reversed(result))

#print(convert('akuo jcr'))
