from check_sequences import *
from get_vocabulary import *


if __name__ == '__main__':
    en_words = get_meaningful_words('en')
    print(f"Got {len(en_words)} English words\n")
    de_words = get_meaningful_words('de')
    print(f"Got {len(de_words)} German words\n")

    # en-en
    matches = find_matches(en_words, en_words, name='en-en')
    matches.to_csv('matches/eng-eng.csv', index=False)

    # de-de
    # matches = find_matches(de_words, de_words, name='de-de')
    # matches.to_csv('matches/ger-ger.csv', index=False)
    #
    # # en-de
    # matches = find_matches(en_words, de_words, name='en-de')
    # matches.to_csv('matches/eng-ger.csv', index=False)
    #
    # # custom
    # custom_words = ['hass', 'erik', 'babysex']
    # matches = find_matches(custom_words, de_words, name='custom-ger')
    # matches.to_csv('matches/custom-ger.csv', index=False)