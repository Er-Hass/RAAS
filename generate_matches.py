from check_sequences import *
from preprocess.get_vocabulary import *


if __name__ == '__main__':
    save_path = "matches/"
    os.makedirs('matches', exist_ok=True)

    en_words = load_word_list('preprocess/vocabularies/meaningful_words/en.txt')
    print(f"Got {len(en_words)} English words\n")
    de_words = load_word_list('preprocess/vocabularies/meaningful_words/de.txt')
    print(f"Got {len(de_words)} German words\n")

    # en-en
    matches = find_matches(en_words, en_words, name='en-en', case_variations=True, simple=True)
    matches.to_csv(f'{save_path}/eng-eng.csv', index=False)

    # de-de
    # matches = find_matches(de_words, de_words, name='de-de', simple=True)
    # matches.to_csv(f'{save_path}/ger-ger.csv', index=False)

    # en-de
    # matches = find_matches(en_words, de_words, name='en-de', simple=True)
    # matches.to_csv(f'{save_path}/eng-ger.csv', index=False)

    # custom
    # custom_words = ['hass', 'erik', 'babysex']
    # matches = find_matches(custom_words, de_words, name='custom-ger')
    # matches.to_csv('matches/custom-ger.csv', index=False)


