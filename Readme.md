## Install

#### Create Environment with venv or conda:
Venv:
```
python3 -m venv .venv
source .venv/bin/activate
```
    
Conda:
```
conda create --name raas python=3.9
conda activate raas
```

#### Install packages:
```
pip install -r requirements.txt
``` 

#### Download required spaCy models
```
python -m spacy download en_core_web_lg
python -m spacy download de_core_news_lg
```


## Usage

#### 1.) Generate meaningful vocabularies
Run [get_vocabulary.py](preprocess/get_vocabulary.py) to generate vocabularies that only contain meaningful words.\
Default creates English, German and a combined checklist. \
Outputs:
- `preprocess/vocabularies/meaningful_words/en.txt`
- `preprocess/vocabularies/meaningful_words/de.txt`
- `preprocess/vocabularies/meaningful_words/check_vocab.txt`

To customize min/max length or language:
```
from preprocess.get_vocabulary import save_meaningful_words

# English nouns, length 4–12
en_words = save_meaningful_words(min_length=4, max_length=12, language_code='en')

# German nouns, length 5–15
de_words = save_meaningful_words(min_length=5, max_length=15, language_code='de')
```
Different languages require downloading the corresponding spaCy model and a word collection/corpus.

#### 2.) Run RAAS to generate matches
Run [run_raas.py](run_raas.py) to generate matches. \
\
Default german and english outputs:
- `matches/en.csv`
- `matches/de.csv`

What it does:
- Iterates over every word from the input_vocab for other strings of characters that can be read inside the input word.
- Checks if these strings are real words by looking up if they appear in check_vocab.
- Also takes every possible case variation of the input word into account.
- Saves results as a table in a CSV file. Every row contains the original_word, a new_word, possible case_variations 
off the part of the original_word that contains the new_word. And an offset and direction that indicates how and where 
the new_word is positioned in the original_word.

#### 3.) Sort matches by semantic similarity (optional)
It is possible to sort the outputs of run_raas.py by semantic similarity through [sort.py](matches/sort.py).
Which requires the CSVs from the previous step.\
\
Default outputs:
- `matches/en_sorted.csv`
- `matches/de_sorted.csv`

What it does:
- Loads a multilingual SentenceTransformer model
- Computes cosine similarity for original_word and new_word pairs
- Sorts the list of pairs by similarity score

