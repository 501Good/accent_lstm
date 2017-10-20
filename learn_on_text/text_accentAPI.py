from keras.models import model_from_json
import numpy as np
import re
from tokenizer import tokenize

VOWELS = 'аеиоуэюяыё'
REG = '[{}].*[{}]'.format(VOWELS, VOWELS)
MAXLEN = 40
CHARS = ["'", '-', '_', 'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к',
        'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', 'ё']
CHAR_INDICES = dict((c, i) for i, c in enumerate(CHARS))
with open("text_model.json", 'r') as content_file:
    json_string = content_file.read()
    model = model_from_json(json_string)
    model.load_weights('on-texts-weights-improvement-09-0.96.hdf5')

def parse_the_phrase(text):
    text = text.replace("c", "с")  # latinic to cyrillic
    regex1 = "[…:,.?!\n]"
    text = re.sub(regex1, " _ ", text).lower()  # mark beginning of clause
    regex2 = "[^а-яё'_ -]"  # get rid of "#%&""()*-[0-9][a-z];=>@[\\]^_{|}\xa0'
    text = re.sub(regex2, "", text)
    words = text.split(' ')
    return words

def add_endings(wordlist):
    pluswords = []
    for i,word in enumerate(wordlist):
        if not bool(re.search(REG, word)):
            pluswords.append(word) # won't predict, just return (less then two syllables )
        elif i == 0 or wordlist[i-1] == '_':
            pluswords.append('_' + word)
        else:
            context = wordlist[i-1].replace("'", "")
            if len(context)<3:
                ending = context
            else:
                ending = context[-3:]
            plusword = ending + '_' + word
            pluswords.append(plusword)
    return pluswords

def predict(model, word):
    x = np.zeros((1, MAXLEN, len(CHAR_INDICES)), dtype=np.bool)
    #print(word)
    for index, letter in enumerate(word):
        pos = MAXLEN - len(word.replace("'", "")) + index
        x[0, pos, CHAR_INDICES[letter]] = 1
    #print(x)
    preds = model.predict(x, verbose=0)[0]
    preds = preds.tolist()
    max_value = max(preds)
    index = preds.index(max_value)
    #cut left context "ные_мечты" -> "мечты"
    word = word[word.index('_')+1:]
    index = len(word) - MAXLEN + index
    #print(preds)
    #print('max_value in preds is %s with index %s' % (max_value, index))
    if index > len(word)-1:
        print('no %s-th letter in %s' % (index+1,word))
    else:
        acc_word = word[:index+1]+'\''+ word[index+1:]
        return(acc_word)


def put_stress(text, stress_symbol="'"):
    """This function gets any string as an input and returns the same string
    but only with the predicted stress marks.
    
    All the formating is preserved using this function. 
    """
    
    words = parse_the_phrase(text)
    tokens = tokenize(text)
    accented_phrase = []
    pluswords = add_endings(words)

    for w in pluswords:
        if not bool(re.search(REG, w)):
            pass
        else:
            accented_phrase.append(predict(model, w))
    final = []
    
    for token in tokens:
        try:
            temp = accented_phrase[0].replace("'", '')
        except IndexError:
            temp = ''
        if temp == token.lower():
            final.append(accented_phrase[0].replace("'", stress_symbol))
            accented_phrase = accented_phrase[1:]
        else:
            final.append(token)
    final = ''.join(final)
    return final


def main():
    with open("text_model.json", 'r') as content_file:
        json_string = content_file.read()
    model = model_from_json(json_string)
    model.load_weights('on-texts-weights-improvement-09-0.96.hdf5')

    while True:
        phrase = input("Russian phrase to accentuate: ")
        accented_phrase = put_stress(phrase)
        print(accented_phrase)

def for_bot(phrase):
    # with open("text_model.json", 'r') as content_file:
    #     json_string = content_file.read()
    # model = model_from_json(json_string)
    # model.load_weights('on-texts-weights-improvement-09-0.96.hdf5')
    words = parse_the_phrase(phrase)
    accented_phrase = []
    pluswords = add_endings(words)

    for w in pluswords:
        if w == "_":
            continue
        elif not bool(re.search(REG, w)):
            accented_phrase.append(w)
        else:
            accented_phrase.append(predict(model, w))
    accented_phrase = ' '.join(accented_phrase)
    return accented_phrase


if __name__ == "__main__":
    main()