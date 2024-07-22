import pandas as pd


def word_to_sequence(word):
    return ''.join([format(ord(char), '08b') for char in word])


def check_subsequence(sequence_1, sequence_2):
    # Sequence_1 has to be longer or equal to sequence_2
    # Returns True if backwards sequence_2 is a subsequence of sequence_1, False otherwise
    # if sequence_1 == sequence_2 or sequence_2 in sequence_1:
    #     return None  # Words are the same or word 2 is part of word 1
    if sequence_1 == sequence_2:
        return None  # Words are the same or word 2 is part of word 1

    sequence_2_backw = sequence_2[::-1]

    for i in range(len(sequence_2)):
        if sequence_2 in sequence_1:
            return False
        elif sequence_2_backw in sequence_1:
            return True
        else:
            sequence_1 = sequence_1[1:] + sequence_1[0]


def bite_off_byte(list1, list2):
    column_names = ['word_1', 'word_2', 'backwards', 'length_difference']
    found_bites = pd.DataFrame(columns=column_names)

    sequence_list1 = [word_to_sequence(word) for word in list1]
    sequence_list2 = [word_to_sequence(word) for word in list2]

    for word1, sequence1 in zip(list1, sequence_list1):
        for word2, sequence2 in zip(list2, sequence_list2):
            # Check which word is longer
            length_difference = len(word1) - len(word2)
            if length_difference < 0:
                length_difference = -length_difference
                backwards = check_subsequence(sequence2, sequence1)
                if backwards is not None:
                    new_row = pd.DataFrame([[word2, word1, backwards, length_difference]], columns=column_names)
                    found_bites = pd.concat([found_bites, new_row], ignore_index=True)
            else:
                backwards = check_subsequence(sequence1, sequence2)
                if backwards is not None:
                    new_row = pd.DataFrame([[word1, word2, backwards, length_difference]], columns=column_names)
                    found_bites = pd.concat([found_bites, new_row], ignore_index=True)

    return found_bites
