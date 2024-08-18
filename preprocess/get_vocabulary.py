import spacy
from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP_WORDS
from spacy.lang.es.stop_words import STOP_WORDS as DE_STOP_WORDS
import os


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


def get_meaningful_words(language_code='en'):
    if language_code == 'en':
        nlp = spacy.load('en_core_web_lg')
        word_list = set(load_word_list('preprocess/vocabularies/en/EOWL.txt'))
    elif language_code == 'de':
        nlp = spacy.load('de_core_news_lg')
        word_list = set(load_word_list('preprocess/vocabularies/de/wordlist-german.txt'))
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
        and 10 >= len(word) > 3
    ]

    return meaningful_words


def save_meaningful_words(language_code='en'):
    words = set(get_meaningful_words(language_code))

    directory = 'preprocess/vocabularies/meaningful_words'
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(f'{directory}/{language_code}.txt', 'w', encoding='utf-8') as file:
        for word in words:
            file.write(f"{word}\n")

    return words


if __name__ == '__main__':
    # Save all meaningful words to files
    print(f"English words: {len(save_meaningful_words('en'))}")
    print(f"German words: {len(save_meaningful_words('de'))}")
