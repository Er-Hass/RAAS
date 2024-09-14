from raas import *
from cache.save import *
from preprocess.get_vocabulary import load_word_list
import pandas as pd
from tqdm import tqdm
import os
import warnings

warnings.filterwarnings("ignore")


def run_raas(name, input_vocab, check_vocab):
    output_dir = 'matches'
    os.makedirs(output_dir, exist_ok=True)

    results = []
    with tqdm(total=len(input_vocab), desc=f"Processing {name}",
              bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m") as pbar:
        for word in input_vocab:
            word_results = process_word(word, check_vocab)
            if not word_results.empty:
                results.append(word_results)
            pbar.update(1)
            pbar.set_postfix({'Results': sum(len(r) for r in results)})

            if pbar.n % 1000 == 0:
                save_pairs('valid_pairs', valid_pairs)
                save_set('non_valid_pairs', non_valid_pairs)

    if not results:
        print(f"No new words found for {name}.")
        return

    all_new_words = pd.concat(results, ignore_index=True)
    # all_new_words = all_new_words[['original_word', 'new_word', 'case_variations', 'starting_letter', 'offset', 'direction']]
    all_new_words.to_csv(f'{output_dir}/{name}.csv', index=False)

    # Final save of valid_pairs and non_valid_pairs
    save_pairs('valid_pairs', valid_pairs)
    save_set('non_valid_pairs', non_valid_pairs)

    print(f"Found {len(all_new_words)} new words for {name}.")
    print(f"Results saved in {output_dir}/{name}.csv")

if __name__ == '__main__':
    en = load_word_list('preprocess/vocabularies/meaningful_words/en.txt')
    de = load_word_list('preprocess/vocabularies/meaningful_words/de.txt')

    # test_words = ['blistering', 'farmyard', 'papas']
    # run_raas('test', test_words, en + de)
    run_raas('en', en[:50], en + de)
    # run_raas('de', de, en + de)