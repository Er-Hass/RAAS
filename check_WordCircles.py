from ascii_circle import *
from tqdm import tqdm
import pandas as pd


def find_matches_wc(list1, list2, case_variations=False, name="Search"):
    column_names = ['word_1', 'word_2', 'direction', 'offset']
    results = []

    # Generate sequences for all words in list1 and list2
    list1 = [WordCircle(word, case_variations) for word in list1]
    if list1 == list2:
        same = True
        list2 = list1.copy()
    else:
        same = False
        list2 = [WordCircle(word, case_variations) for word in list2]

    # Compare all words in list1 with all words in list2
    progress_bar = tqdm(list1, desc=name, total=len(list1), bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m")
    for word1 in progress_bar:
        for word2 in list2:
            length_difference = len(word1) - len(word2)

            # Longer word compared with shorter one
            if length_difference < 0:
                if word2 == word1 or word2.check_irrelevant(word1):
                    continue
                results += word2.check_sequence(word1)
            else:
                if word1 == word2 or word1.check_irrelevant(word2):
                    continue
                results += word1.check_sequence(word2)

            progress_bar.set_postfix({'matches found': '{}'.format(len(results))})

        # Delete word1 from the list2 to avoid duplicates
        if same:
            list2.remove(word1)

    found_matches = pd.DataFrame(results, columns=column_names)
    return found_matches
