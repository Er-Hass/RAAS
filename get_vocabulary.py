import spacy
from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP_WORDS
from spacy.lang.es.stop_words import STOP_WORDS as DE_STOP_WORDS


def load_stop_words(language_code):
    if language_code == 'en':
        return EN_STOP_WORDS
    elif language_code == 'de':
        return DE_STOP_WORDS
    else:
        raise ValueError("Unsupported language code: Stopwords")


def load_word_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = set(line.strip().lower() for line in file)
    return words


def get_meaningful_words(language_code='en'):
    if language_code == 'en':
        nlp = spacy.load('en_core_web_lg')
        word_list = load_word_list('vocabularies/en/EOWL.txt')
    elif language_code == 'de':
        nlp = spacy.load('de_core_news_lg')
        word_list = load_word_list('vocabularies/de/wordlist-german.txt')
    else:
        raise ValueError("Unsupported language code: Vocabulary")

    stop_words = load_stop_words(language_code)
    vocab = nlp.vocab

    # Extract meaningful words from the vocabulary
    meaningful_words = [
        word for word in vocab.strings
        if word.isalpha() and word.lower() not in stop_words
        and vocab[word].has_vector
        and word.lower() in word_list
        and len(word) > 3
    ]

    return meaningful_words


if __name__ == '__main__':
    words = get_meaningful_words('en')
    print(f"English: {len(words)}")
    print(words[:500])

    words = get_meaningful_words('de')
    print(f"German: {len(words)}")
    print(words[:500])
