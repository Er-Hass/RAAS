from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity


def check_same_word(word1, word2):
    word1_rotational = word1 + word1
    if word2 in word1_rotational or word2[::-1] in word1_rotational:
        return True
    else:
        return False


def sort_words_by_similarity(file_name):
    # Load the sentence transformer model (for both English and German words)
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # Read CSV and clean data
    df = pd.read_csv(f'{file_name}')
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

            # Generate embeddings and calculate cosine similarity
            embeddings = model.encode([original_word, new_word])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return similarity
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


if __name__ == '__main__':
    sort_words_by_similarity('en.csv')
    sort_words_by_similarity('de.csv')
