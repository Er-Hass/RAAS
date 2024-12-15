To filter out the most common words:

```python
import pandas as pd

def filter_dataframe(word, file_name):
    df = pd.read_csv(file_name)
    filtered_df = df[~df['new_word'].str.contains(word, case=False)]
    filtered_df.to_csv(file_name, index=False)
```
```python
file_name = 'matches/de_sorted.csv'
df = pd.read_csv(file_name)
```

```python
most_common_word, max_count = df['new_word'].value_counts().idxmax(), df['new_word'].value_counts().max()
```

if the most common word is not desired, delete all rows that contain it
```python
filter_dataframe(most_common_word, file_name)
df = pd.read_csv(file_name)
```

Continue until really common, bad words are all gone

---
Or look through all new_words, sorted by occurences and delete all over a certain count
```python
def filter_by_occurrence(count, file_name):
    df = pd.read_csv(file_name)

    word_counts = df['new_word'].value_counts()
    filtered_df = df[~df['new_word'].isin(word_counts[word_counts > count].index)]
    filtered_df.to_csv(file_name, index=False)
```
