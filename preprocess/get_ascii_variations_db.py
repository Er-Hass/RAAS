import os.path
import multiprocessing as mp
from tqdm import tqdm
from get_vocabulary import load_word_list
import torch
from itertools import product
import pandas as pd
from supabase import Client, create_client
import io
import h5py
from concurrent.futures import ProcessPoolExecutor, as_completed


supabase: Client = create_client("http://127.0.0.1:54321",
                                 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")


def generate_case_variations(word):
    # Generate all upper and lower case combinations of the given word
    return [''.join(variation) for variation in product(*((c.lower(), c.upper()) if c != 'ß' else (c,) for c in word))]


def word_to_sequence(word, device):
    # Convert a word to a binary ASCII sequence as PyTorch tensor
    return torch.tensor([int(bit) for char in word for bit in format(ord(char), '08b')], device=device)


def ascii_variations(word, device):
    # Generate all ASCII case variations of the given word
    return torch.stack([word_to_sequence(variation, device) for variation in generate_case_variations(word)])


def replace_umlauts(word):
    replacements = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'Ä': 'Ae',
        'Ö': 'Oe',
        'Ü': 'Ue',
        'ß': 'ss'
    }
    for umlaut, replacement in replacements.items():
        word = word.replace(umlaut, replacement)
    return word


def store_ascii_vector(word, vector):
    vector_np = vector.cpu().numpy()

    buffer = io.BytesIO()
    with h5py.File(buffer, 'w', libver='latest') as f:
        f.create_dataset('vector', data=vector_np, compression='gzip')
    buffer.seek(0)

    response = (
        supabase.storage.from_("ascii_vectors")
        .upload(f"{word}.h5", buffer.getvalue())
    )

    return response


def store_ascii_variations(word, device):
    torch.cuda.empty_cache()

    variations = ascii_variations(word, device)
    extended = variations.repeat(variations.shape[0], 1)
    backw_interleave = torch.flip(variations, [1]).repeat_interleave(variations.shape[0], dim=0)

    store_ascii_vector(f"{word}_extended", extended.cpu())
    store_ascii_vector(f"{word}_backw_interleave", backw_interleave.cpu())


def process_word(word, language_code):
    if language_code == 'de':
        word = replace_umlauts(word)

    try:
        response = (
            supabase.table(f"ascii_variations_{language_code}")
            .insert({
                "word": word,
                "extended": f"{word}_extended.h5",
                "backw_interleave": f"{word}_backw_interleave.h5",
                "len": len(word)})
            .execute()
        )

        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            store_ascii_variations(word, device)

        except torch.cuda.OutOfMemoryError as e:
            try:
                device = torch.device("cpu")
                store_ascii_variations(word, device)

            except Exception as e:
                print(f"Error processing {word} on CPU: {e}")

        except Exception as e:
            print(f"Error processing {word}: {e}")

    except Exception as e:
        print(f"Error inserting {word}: {e}")


def get_circle_variations(vocab, name="", language_code="en", workers=3):
    with tqdm(total=len(vocab), desc=f"Processing {name}", bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m") as pbar:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_word, word, language_code) for word in vocab]
            for _ in as_completed(futures):
                pbar.update(1)


def main(workers):
    de = load_word_list('vocabularies/meaningful_words/de.txt')
    get_circle_variations(de, name='Deutsch', language_code='de', workers=workers)

    en = load_word_list('vocabularies/meaningful_words/en.txt')
    # en = en[0:100]  # For testing
    get_circle_variations(en, name='English', language_code='en', workers=workers)

if __name__ == '__main__':
    mp.set_start_method('spawn')
    main(workers=1)
    # process_word("test", "en")