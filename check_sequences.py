import pandas as pd
from tqdm import tqdm
from itertools import product


def word_to_sequence(word):
    # Convert a word to a binary sequence
    return ''.join([format(ord(char), '08b') for char in word])


def generate_case_variations(word):
    # Generate all upper and lower case combinations of the given word
    return [''.join(variation) for variation in product(*((c.lower(), c.upper()) for c in word))]


def generate_ul_variations(word):
    # Generate an upper and lower case version of the given word
    return [word.lower(), word.upper()]


def check_circle_sequence(sequence, sub_sequence):
    double_sequence = sequence + sequence  # To represent a circle
    return sub_sequence in double_sequence


def check_subsequence(sequence, sub_sequence):
    # Returns True if backwards sequence_2 is a subsequence of sequence_1, False otherwise
    sequence_2_backw = sub_sequence[::-1]

    if check_circle_sequence(sequence, sequence_2_backw):
        return 'reverse'
    if check_circle_sequence(sequence, sub_sequence):
        return 'forward'


def find_matches(list1, list2, case_variations=False, upper_lower=False, simple=False, name="Search"):
    column_names = ['word_1', 'word_2', 'direction', 'length_difference']
    results = []

    # Generate sequences for all words in list1 and list2
    if list1 == list2:
        same = True
        if case_variations:
            list1 = [variation for word in list1 for variation in generate_case_variations(word)]
        elif upper_lower:
            list1 = [variation for word in list1 for variation in generate_ul_variations(word)]
        list2 = list1.copy()
        sequence_list1 = [word_to_sequence(word) for word in list1]
        sequence_list2 = sequence_list1.copy()
    else:
        same = False
        if case_variations:
            list1 = [variation for word in list1 for variation in generate_case_variations(word)]
            list2 = [variation for word in list2 for variation in generate_case_variations(word)]
        elif upper_lower:
            list1 = [variation for word in list1 for variation in generate_ul_variations(word)]
            list2 = [variation for word in list2 for variation in generate_ul_variations(word)]
        sequence_list1 = [word_to_sequence(word) for word in list1]
        sequence_list2 = [word_to_sequence(word) for word in list2]

    # Compare all words in list1 with all words in list2
    progress_bar = tqdm(zip(list1, sequence_list1), desc=name, total=len(list1), bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m")
    for word1, sequence1 in progress_bar:
        for word2, sequence2 in zip(list2, sequence_list2):
            length_difference = len(word1) - len(word2)

            # Longer word compared with shorter one
            if length_difference == 0 and simple:
                if not word1 == word2 and sequence1 == sequence2[::-1]:
                    direction = 'reverse'
                else:
                    continue
            elif length_difference < 0 and not simple:
                if word1 == word2 or check_subsequence(word2, word1):
                    continue
                direction = check_subsequence(sequence2, sequence1)
            elif not simple:
                if word1 == word2 or check_subsequence(word1, word2):
                    continue
                direction = check_subsequence(sequence1, sequence2)
            else:
                continue

            if direction is not None:
                results.append([word1, word2, direction, abs(length_difference)])
                progress_bar.set_postfix({'matches found': '{}'.format(len(results))})

        # Delete word1 from the list2 to avoid duplicates
        if same:
            sequence_list2.remove(sequence1)
            list2.remove(word1)

    found_matches = pd.DataFrame(results, columns=column_names)
    return found_matches

