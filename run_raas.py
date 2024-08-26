from raas import *
from cache.save import *
from preprocess.get_vocabulary import load_word_list
import pandas as pd
from tqdm import tqdm
import os

def process_word(word, check_vocab):
    results = set()  # Use a set to automatically remove duplicates
    case_variations = generate_case_variations(word)
    
    for case_variation in case_variations:
        pairs, potential_length = word_to_pairs(case_variation)
        if potential_length < 4:
            continue
        pair_sequences = pairs_to_sequences(pairs, potential_length)
        new_words = sequences_to_words(pair_sequences)
        if not new_words.empty and 'new_word' in new_words.columns:
            valid_new_words = new_words[new_words['new_word'].str.lower().isin(check_vocab)]
            for _, row in valid_new_words.iterrows():
                results.add((word, row['new_word'], row['starting_letter'], row['offset'], row['direction']))
    
    # Convert the set of tuples to a DataFrame
    df = pd.DataFrame(list(results), columns=['orig_word', 'starting_letter', 'new_word', 'offset', 'direction'])
    
    # Add a column for case variations
    df['case_variations'] = [case_variations] * len(df)
    
    return df

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
    
    # Convert case_variations list to a string for CSV storage
    all_new_words['case_variations'] = all_new_words['case_variations'].apply(lambda x: ', '.join(x))
    
    all_new_words.to_csv(f'{output_dir}/{name}.csv', index=False)

    # Final save of valid_pairs and non_valid_pairs
    save_pairs('valid_pairs', valid_pairs)
    save_set('non_valid_pairs', non_valid_pairs)

    print(f"Found {len(all_new_words)} new words for {name}.")
    print(f"Results saved in {output_dir}/{name}.csv")

if __name__ == '__main__':
    en = load_word_list('preprocess/vocabularies/meaningful_words/en.txt')
    de = load_word_list('preprocess/vocabularies/meaningful_words/de.txt')

    # test_words = ['Feuerwehrmann', 'Hello', 'World', 'Python']
    # run_raas('test', test_words, en + de)
    run_raas('en', en[:50], en + de)
    # run_raas('de', de, en + de)