import spacy
import pandas as pd
from tqdm import tqdm


def check_same_word(word1, word2):
    word1_rotational = word1 + word1
    if word2 in word1_rotational or word2[::-1] in word1_rotational:
        return True
    else:
        return False

def sort_words_by_similarity(file_name, language_code='en'):
    # Load the appropriate language model
    if language_code == 'en':
        nlp = spacy.load('en_core_web_lg')
    elif language_code == 'de':
        nlp = spacy.load('de_core_news_lg')
    else:
        raise ValueError("Unsupported language code")

    # Read CSV and calculate similarity scores
    df = pd.read_csv(f'{file_name}')

    # Clean data: remove rows with non-string values and strip whitespace
    df = df.dropna(subset=['original_word', 'new_word'])
    df['original_word'] = df['original_word'].astype(str).str.strip()
    df['new_word'] = df['new_word'].astype(str).str.strip()

    # Calculate similarity scores with progress bar
    def calculate_similarity(row):
        try:
            original = nlp(row['original_word'])
            new = nlp(row['new_word'])
            
            # Skip if one word contains the other
            if row['original_word'] in row['new_word'] or row['new_word'] in row['original_word']:
                return None
            
            if original.has_vector and new.has_vector:
                return original.similarity(new)
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
    # sort_words_by_similarity('en.csv', 'en')
    # sort_words_by_similarity('de.csv', 'de')

    filter_words_by_length('en_sorted.csv', 5)
    filter_words_by_length('de_sorted.csv', 5)