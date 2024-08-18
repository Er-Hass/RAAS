import os.path
from tqdm import tqdm
from preprocess.get_vocabulary import load_word_list
import torch
from itertools import product
import pandas as pd
from supabase import Client, create_client
import io


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Torch device: {device}")
supabase: Client = create_client("http://127.0.0.1:54321",
                                 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")


def generate_case_variations(word):
    # Generate all upper and lower case combinations of the given word
    return [''.join(variation) for variation in product(*((c.lower(), c.upper()) for c in word))]


def word_to_sequence(word):
    # Convert a word to a binary ASCII sequence as PyTorch tensor
    return torch.tensor([int(bit) for char in word for bit in format(ord(char), '08b')], device=device)


def ascii_variations(word):
    # Generate all ASCII case variations of the given word
    return torch.stack([word_to_sequence(variation) for variation in generate_case_variations(word)])


def store_ascii_vector(word, vector):
    # Save the tensor to a file
    buffer = io.BytesIO()
    torch.save(vector, buffer)
    buffer.seek(0)

    response = (
        supabase.storage.from_("ascii_vectors")
        .upload(f"{word}", buffer.getvalue())
    )

    return response


def get_circle_variations(vocab, name=""):
    df = pd.DataFrame(columns=['word', 'extended', 'backw_extended', 'len'])
    progress_bar = tqdm(vocab, desc=f"Circle variations {name}", total=len(vocab), bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m")

    for word in progress_bar:
        variations = ascii_variations(word)
        extended = variations.repeat(variations.shape[0], 1)
        backw_interleave = torch.flip(variations, [1]).repeat_interleave(variations.shape[0], dim=0)

        try:
            response = (
                supabase.table("ascii_variations")
                .insert({
                    "word": word,
                    "extended": f"{word}_extended.pt",
                    "backw_interleave": f"{word}_backw_interleave.pt",
                    "len": len(word)})
                .execute()
            )
            store_ascii_vector(f"{word}_extended.pt", extended)
            store_ascii_vector(f"{word}_backw_interleave.pt", backw_interleave)

        except Exception as e:
            print(f"Error inserting {word}: {e}")


if __name__ == '__main__':
    en = load_word_list('vocabularies/meaningful_words/en.txt')
    # de = load_word_list('vocabularies/meaningful_words/de.txt')

    # get_circle_variations(en, engine, name='English')
    # get_circle_variations(de, engine, name='Deutsch')
    get_circle_variations(en[:1000], name='Test')

    # circle_folder = 'vocabularies/ascii_variations'
    # print(en_circles.head())
    # print(de_circles.head())
    # en.to_csv(os.path.join(circle_folder, 'en.csv'), index=False)
    # de.to_csv(os.path.join(circle_folder, 'de.csv'), index=False)
