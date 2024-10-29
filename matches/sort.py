import spacy
import pandas as pd
from tqdm import tqdm


def check_same_word(word1, word2):
    word1_rotational = word1 + word1
    if word2 in word1_rotational or word2[::-1] in word1_rotational:
        return True
    else:
        return False

def sort_words_by_similarity(file_name):
    en = spacy.load('en_core_web_lg')
    de = spacy.load('de_core_news_lg')

    # Read CSV and calculate similarity scores
    df = pd.read_csv(f'{file_name}')

    # Clean data: remove rows with non-string values and strip whitespace
    df = df.dropna(subset=['original_word', 'new_word'])
    df['original_word'] = df['original_word'].astype(str).str.strip()
    df['new_word'] = df['new_word'].astype(str).str.strip()

    # Calculate similarity scores with progress bar
    def calculate_similarity(row):
        try:
            original_word = row['original_word'].lower()
            new_word = row['new_word'].lower()

            # Skip if one word contains the other
            if original_word in new_word or new_word in original_word:
                return None

            original = en(original_word)
            new = en(new_word)

            # Check if words are english, otherwise use german
            if not original.has_vector:
                original = de(original_word)
            if not new.has_vector:
                new = de(new_word)
            
            if original.has_vector and new.has_vector:
                return original.similarity(new)
            else:
                raise Exception("No vector")
        except Exception as e:
            print(f"Error processing row: {row}. Error: {e}")
        return None

    tqdm.pandas(desc=f"Calculating similarities of {file_name}", bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m")
    df['similarity_score'] = df.progress_apply(calculate_similarity, axis=1)

    # Remove rows with None similarity score
    df = df.dropna(subset=['similarity_score'])

    # Sort by absolute value of similarity score and select columns
    df_sorted = df.sort_values('similarity_score', key=abs, ascending=False)[['original_word', 'new_word', 'similarity_score']]

    # Save sorted DataFrame
    output_path = f'{file_name.split(".")[0]}_sorted.csv'
    df_sorted.to_csv(output_path, index=False)
    print(f"Sorted results saved to {output_path}")

def filter_words_by_length(file_name, min_length):
    # Read CSV
    df = pd.read_csv(f'{file_name}')

    # Clean data: remove rows with non-string values and strip whitespace
    df = df.dropna(subset=['original_word', 'new_word'])
    df['original_word'] = df['original_word'].astype(str).str.strip()
    df['new_word'] = df['new_word'].astype(str).str.strip()

    # Filter words based on minimum length
    df_filtered = df[df['new_word'].str.len() >= min_length]

    # Sort alphabetically by new_word
    df_filtered = df_filtered.sort_values('new_word')

    # Select columns
    df_filtered = df_filtered[['original_word', 'new_word']]

    # Save filtered DataFrame
    output_path = f'{file_name.split(".")[0]}_min{min_length}.csv'
    df_filtered.to_csv(output_path, index=False)
    print(f"Filtered results (minimum length {min_length}) saved to {output_path}")


if __name__ == '__main__':
    # sort_words_by_similarity('en.csv')
    sort_words_by_similarity('de.csv')

    # filter_words_by_length('en_sorted.csv', 5)
    # filter_words_by_length('de_sorted.csv', 5)