import pandas as pd
from tqdm import tqdm
from itertools import product


def word_to_sequence(word):
    # Convert a word to a binary sequence
    return ''.join([format(ord(char), '08b') for char in word])


def generate_case_variations(word):
    # Generate all upper and lower case combinations of the given word
    return [''.join(variation) for variation in product(*((c.lower(), c.upper()) for c in word))]


def is_subsequence(small, large):
    it = iter(large)
    return all(char in it for char in small)


def check_subsequence(sequence, sub_sequence):
    # Sequence_1 has to be longer or equal to sequence_2
    # Returns True if backwards sequence_2 is a subsequence of sequence_1, False otherwise

    if sequence == sub_sequence or sub_sequence in sequence:
        return None  # Words are the same or word 2 is part of word 1

    sequence_2_backw = sub_sequence[::-1]

    if is_subsequence(sub_sequence, sequence):
        return False
    elif is_subsequence(sequence, sequence_2_backw):
        return True


def bite_off_byte(list1, list2):
    column_names = ['word_1', 'word_2', 'backwards', 'length_difference']
    results = []

    if list1 == list2:
        list1 = [variation for word in list1 for variation in generate_case_variations(word)]
        sequence_list1 = [word_to_sequence(word) for word in list1]
        list2 = list1.copy()
        sequence_list2 = sequence_list1.copy()
    else:
        list1 = [variation for word in list1 for variation in generate_case_variations(word)]
        list2 = [variation for word in list2 for variation in generate_case_variations(word)]
        sequence_list1 = [word_to_sequence(word) for word in list1]
        sequence_list2 = [word_to_sequence(word) for word in list2]

    for word1, sequence1 in tqdm(zip(list1, sequence_list1), total=len(list1), bar_format="\033[92m{l_bar}{bar:25}{r_bar}\033[0m"):
        for word2, sequence2 in zip(list2, sequence_list2):
            length_difference = len(word1) - len(word2)

            if length_difference < 0:
                if word1 == word2 or word1 in word2:
                    continue
                length_difference = -length_difference
                backwards = check_subsequence(sequence2, sequence1)
            else:
                if word1 == word2 or word2 in word1:
                    continue
                backwards = check_subsequence(sequence1, sequence2)

            if backwards is not None:
                results.append([word1, word2, backwards, length_difference])

    found_bites = pd.DataFrame(results, columns=column_names)
    return found_bites
