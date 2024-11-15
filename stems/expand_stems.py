from itertools import combinations
import os
import sys

# You will need to install all these. Good luck.
# Also they take like 10 seconds to import
import nltk
import pymorphy2
from pattern.en import lexeme  # My IDE does not even believe that this exists...
from estnltk.vabamorf.morf import synthesize

ru_morph = pymorphy2.MorphAnalyzer()

def expand_en_stems():
    print('// English my boy (from the stem)')
    for line in open('stems/en.txt', 'r', encoding='utf-8').read().split('\n'):
        while True:
            try:  # Working around an *unfathomably* ridiculous bug in pattern.en
                superior_word, subpar_word = line.split(':')
                superior_lexemes = lexeme(superior_word)
                subpar_lexemes = lexeme(subpar_word)
                # Honestly, pattern is *bad*
                # But English is so forgiving it will suffice for our 80/20 purposes
                assert len(superior_lexemes) == len(subpar_lexemes)
                for i in range(len(superior_lexemes)):
                    print(f'{superior_lexemes[i]}:{subpar_lexemes[i]}')
                break
            except Exception as e:
                if e is AssertionError:
                    raise e


def expand_ru_stems():
    print('// Russian the troublemaker (from the stem)')

    # Я без понятия если честно что большинство из них делает, поэтому YOLO
    FUNNY_WORDS = ['animacy', 'aspect', 'case', 'gender', # <- род существительных это самая бесполезная фича языка
                   'involvement', 'mood', 'number', 'person', 'tense', 'transitivity', 'voice']
    for line in open('stems/ru.txt', 'r', encoding='utf-8').read().split('\n'):
        superior_word, subpar_word = line.split(':')
        parsed_superior = ru_morph.parse(superior_word)[0]
        parsed_subpar = ru_morph.parse(subpar_word)[0]
        forms_processed = []
        for subpar_form in parsed_subpar.lexeme:
            if subpar_form.word in forms_processed:
                continue
            gotchas = [getattr(subpar_form.tag, x) for x in FUNNY_WORDS]
            gotchas = [x for x in gotchas if x is not None]

            found = False
            for i in range(len(gotchas), 0, -1):
                if found:
                    break
                for subset in combinations(gotchas, i):
                    inflected = parsed_superior.inflect(set(subset))
                    if inflected:
                        print(f"{inflected.word.replace('ё', 'е')}:{subpar_form.word.replace('ё', 'е')}")
                        forms_processed.append(subpar_form.word)
                        found = True
                        break


def expand_et_stems():
    # There will be like 690 of them, but we don't care 'cause our substitution engine is aaaawesooome!
    print('// Estonian (from the stem)')
    nimisõnade_kääned = 'n g p ill in el all ad adt abl tr ter es ab kom'.split(' ')
    nimisõnade_mitmus = 'sg pl'.split(' ')
    # **OH MY GOD** neid on palju 😭
    tegusõnade_vormid = ('nuvat,neg gem,taks,sin,neg ge,maks,neg nud,o,gu,tud,nuksid,d,tuvat,vat,sime,takse,ksid,'
                         'neg gu,tagu,v,tuks,nud,neg vat,sid,neg ks,nuksin,neg o,b,da,nuksime,nuksite,tavat,mas,'
                         'ksite,neg nuks,neg me,tav,nuks,vad,ta,ksin,neg tud,site,ma,des,mast,tama,s,ge,ksime,'
                         'gem,me,n,neg,te,ti,mata,ks').split(',')
    forms_processed = []
    for line in open('stems/et.txt', 'r', encoding='utf-8').read().split('\n'):
        word_type, superior_word, subpar_word = line.split(':')
        if word_type == 'N':
            for m in nimisõnade_mitmus:
                for k in nimisõnade_kääned:
                    try:
                        # TODO: vaata, millist sõna loetelust tuleb parasjagu kasutada
                        parem = synthesize(superior_word, m + ' ' + k)[0]
                        halvem = synthesize(subpar_word, m + ' ' + k)[0]
                        if halvem not in forms_processed:
                            print(f"{parem}:{halvem}")
                            forms_processed.append(halvem)
                    except:
                        pass
        else:
            for v in tegusõnade_vormid:
                try:
                    parem = synthesize(superior_word, v)[0]
                    halvem = synthesize(subpar_word, v)[0]
                    if halvem not in forms_processed:
                        print(f"{parem}:{halvem}")
                        forms_processed.append(halvem)
                except:
                    pass  # Siin kuulus 80/20 reegel töötab ning ma kavatsen seda kasutada!


if __name__ == '__main__':
    expand_en_stems()
    expand_ru_stems()
    expand_et_stems()
    print(open('stems/base.txt', 'r').read())
