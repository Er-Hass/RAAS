from raas import *
from preprocess.get_vocabulary import load_word_list
import pandas as pd
from tqdm import tqdm
import os
import warnings
from multiprocessing import Pool, cpu_count

warnings.filterwarnings("ignore")


def process_word_wrapper(word):
    return process_word(word, check_vocab)


def run_raas(name, input_vocab, check_vocab):
    output_dir = 'matches'
    os.makedirs(output_dir, exist_ok=True)

    num_cores = cpu_count() - 1
    
    with Pool(num_cores) as pool:
        results = list(tqdm(
            pool.imap(process_word_wrapper, input_vocab),
            total=len(input_vocab),
            desc=f"Processing {name}",
            bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m"
        ))

    results = [r for r in results if not r.empty]

    if not results:
        print(f"No new words found for {name}.")
        return

    all_new_words = pd.concat(results, ignore_index=True)
    all_new_words.to_csv(f'{output_dir}/{name}.csv', index=False)

    print(f"Found {len(all_new_words)} new words for {name}.")
    print(f"Results saved in {output_dir}/{name}.csv")


if __name__ == '__main__':
    check_vocab = load_word_list('preprocess/vocabularies/meaningful_words/check_vocab.txt')

    en = load_word_list('preprocess/vocabularies/meaningful_words/en.txt')
    de = load_word_list('preprocess/vocabularies/meaningful_words/de.txt')

    run_raas('en', en, check_vocab)
    run_raas('de', de, check_vocab)