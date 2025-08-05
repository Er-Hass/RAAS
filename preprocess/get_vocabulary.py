import spacy
from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP_WORDS
from spacy.lang.es.stop_words import STOP_WORDS as DE_STOP_WORDS
import os
from tqdm import tqdm


def load_stop_words(language_code):
    if language_code == 'en':
        return EN_STOP_WORDS
    elif language_code == 'de':
        return DE_STOP_WORDS
    else:
        raise ValueError("Unsupported language code: Stopwords")


def load_word_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = list(line.strip().lower() for line in file)
    return words


def get_meaningful_words(language_code='en', min=4, max=9):
    if language_code == 'en':
        nlp = spacy.load('en_core_web_lg')
        word_list = set(load_word_list('vocabularies/en/EOWL.txt'))
    elif language_code == 'de':
        nlp = spacy.load('de_core_news_lg')
        word_list = set(load_word_list('vocabularies/de/wordlist-german.txt'))
    else:
        raise ValueError("Unsupported language code: Vocabulary")

    stop_words = load_stop_words(language_code)
    vocab = nlp.vocab

    # Extract meaningful words from the vocabulary
    meaningful_words = [
        word.lower() for word in vocab.strings
        if word.isalpha() and word.lower() not in stop_words
        and vocab[word].has_vector
        and word.lower() in word_list
        and max >= len(word) >= min
    ]

    # Filter out non-noun words separately, because .pos_ is slow
    meaningful_nouns = []
    for word in tqdm(
            meaningful_words,
            desc=f"Filtering words, {language_code}",
            bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m"):

        if nlp(word)[0].pos_ == 'NOUN':
            meaningful_nouns.append(word)

    return meaningful_nouns


def save_meaningful_words(language_code='en', min=4, max=20):
    words = set(get_meaningful_words(language_code, min, max))

    directory = 'vocabularies/meaningful_words'
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(f'{directory}/{language_code}.txt', 'w', encoding='utf-8') as file:
        for word in words:
            file.write(f"{word}\n")

    return words


if __name__ == '__main__':
    # Save all meaningful words to files
    en = save_meaningful_words('en')
    print(f"English words: {len(en)}")

    de = save_meaningful_words('de')
    print(f"German words:  {len(de)}")

    # Save all meaningful words to a single file
    with open('vocabularies/meaningful_words/check_vocab.txt', 'w', encoding='utf-8') as file:
        for word in en:
            file.write(f"{word}\n")
        for word in de:
            file.write(f"{word}\n")
