from itertools import combinations
import pymorphy2

FUNNY_WORDS = ['animacy', 'aspect', 'case', 'gender', 'involvement', 'mood', 'number', 'person', 'tense', 'transitivity', 'voice']

if __name__ == '__main__':
    morph = pymorphy2.MorphAnalyzer()
    filename = 'substitutionlist_stem_ru.txt'
    for line in open(filename, 'r', encoding='utf-8').read().split('\n'):
        superior_word, subpar_word = line.split(':')
        parsed_superior = morph.parse(superior_word)[0]
        parsed_subpar = morph.parse(subpar_word)[0]
        for subpar_form in parsed_subpar.lexeme:
            gotchas = [getattr(subpar_form.tag, x) for x in FUNNY_WORDS]
            gotchas = [x for x in gotchas if x is not None]

            found = False
            for i in range(len(gotchas), 0, -1):
                if found:
                    break
                for subset in combinations(gotchas, i):
                    inflected = parsed_superior.inflect(set(subset))
                    if inflected:
                        print(f'{inflected.word}:{subpar_form.word}')
                        found = True
                        break
