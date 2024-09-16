from preprocess.get_vocabulary import load_word_list
from cache.load import *
import pandas as pd
import numpy as np

def generate_case_variations(word):
    variations = []
    for i in range(2**len(word)):
        variation = ''.join(c.upper() if (i & (1 << j)) else c.lower()
                            for j, c in enumerate(word))
        variations.append(variation)
    return variations

def text_to_binary(word):
    return ''.join(format(ord(c), '08b') for c in word)

def check_char_pair(pair):
    pair_b = text_to_binary(pair)
    valid = False

    for offset in range(1, 8):
        pb_off = pair_b[offset:offset+8]
        pb_off_r = pb_off[::-1]
        pb_char = chr(int(pb_off, 2))
        pb_char_r = chr(int(pb_off_r, 2))

        if pb_char in valid_chars:
            if pair not in valid_pairs:
                valid_pairs[pair] = []
            valid_pairs[pair].append((pb_char, offset, 'forward'))
            valid = True

        if pb_char_r in valid_chars:
            if pair not in valid_pairs:
                valid_pairs[pair] = []
            valid_pairs[pair].append((pb_char_r, offset, 'reverse'))
            valid = True

    if not valid:
        non_valid_pairs.add(pair)

def handle_non_valid_pairs(pairs, potential_length, i):
    pairs[i] = None

    # Throw away all pairs between 2 None pairs
    if list(pairs.values()).count(None) >= 2:
        none_indices = [j for j, v in pairs.items() if v is None]
        first_none = none_indices[0]
        last_none = none_indices[-1]
        second_last_none = none_indices[-2]

        none_distance = last_none - second_last_none - 1
        rotational_none_distance = (len(pairs) - last_none + first_none) % len(pairs)

        if none_distance < 5 or rotational_none_distance < 5:  # Less than 5 pairs between
            if none_distance < 5:
                for j in range(second_last_none + 1, last_none):
                    pairs[j] = None
                    potential_length -= 1
            if rotational_none_distance < 5:
                for j in range(last_none + 1, len(pairs)):
                    pairs[j] = None
                    potential_length -= 1
                for j in range(0, first_none):
                    pairs[j] = None
                    potential_length -= 1

    return pairs, potential_length-1, i+1

def word_to_pairs(word):
    word_length = len(word)
    potential_length = word_length
    pairs = {}

    i = 0
    while potential_length >= 5 and i < word_length:
        pair = word[i] + word[(i + 1) % word_length]

        if pair in non_valid_pairs:
            pairs, potential_length, i = handle_non_valid_pairs(pairs, potential_length, i)
            continue

        elif pair in valid_pairs:
            pairs[i] = valid_pairs[pair]
            i += 1

        else:
            check_char_pair(pair)

    return pairs, potential_length

def pairs_to_sequences(pairs, potential_length):
    # Create the pair sequences
    pair_sequences = []
    none_indices = [j for j, v in pairs.items() if v is None]

    if none_indices == []:
        sequence = [v for v in pairs.values()]
        pair_sequences.append(create_sequence_dataframe(pairs))
    else:
        # Rotational sequence
        rotational_sequence = {}
        if none_indices[0] > 0:
            rotational_sequence.update({j: pairs[j] for j in range(none_indices[0])})
        if none_indices[-1] < max(pairs.keys()):
            rotational_sequence.update({j: pairs[j] for j in range(none_indices[-1] + 1, max(pairs.keys()) + 1)})

        if rotational_sequence:
            pair_sequences.append(create_sequence_dataframe(rotational_sequence))
        
        # Add sequences between None values
        for start, end in zip(none_indices, none_indices[1:]):
            sequence = {j: pairs[j] for j in range(start + 1, end)}
            pair_sequences.append(create_sequence_dataframe(sequence))

    return pair_sequences

def create_sequence_dataframe(sequence):
    df_data = []
    for pair_index, pair_data in sequence.items():
        chars, offsets, directions = zip(*pair_data)
        df_data.append({
            'char': list(chars),
            'offset': list(offsets),
            'direction': list(directions)
        })
    return pd.DataFrame(df_data)

def sequences_to_words(pair_sequences):
    new_words_data = []

    for sequence in pair_sequences:
        for offset in range(1, 8):
            for direction in ['forward', 'reverse']:
                word = ''
                for index, row in sequence.iterrows():
                    chars = row['char']
                    offsets = row['offset']
                    directions = row['direction']
                    
                    matching_chars = [char for char, char_offset, char_direction in zip(chars, offsets, directions)
                                      if char_offset == offset and char_direction == direction]
                    
                    if matching_chars:
                        word += matching_chars[0]  # Add the first matching character
                    else:
                        if len(word) >= 5:
                            for i in range(len(word) - 3):
                                new_word = word[i:]
                                if direction == 'reverse':
                                    new_word = new_word[::-1]  # Reverse the word if direction is 'reverse'
                                new_words_data.append({
                                    'new_word': new_word,
                                    'starting_letter': index - len(word) + i,
                                    'offset': offset,
                                    'direction': direction
                                })
                        word = ''
                
                if len(word) >= 5:
                    for i in range(len(word) - 3):
                        new_word = word[i:]
                        if direction == 'reverse':
                            new_word = new_word[::-1]  # Reverse the word if direction is 'reverse'
                        new_words_data.append({
                            'new_word': new_word,
                            'starting_letter': sequence.index[-1] - len(word) + i + 1,
                            'offset': offset,
                            'direction': direction
                        })

    return pd.DataFrame(new_words_data)

def generate_new_words(word):
    pairs, potential_length = word_to_pairs(word)
    if potential_length < 5:
        return pd.DataFrame()
    pair_sequences = pairs_to_sequences(pairs, potential_length)
    new_words = sequences_to_words(pair_sequences)

    return new_words

def add_or_update_entry(word, new_word_data, case_variation, valid_new_words):
    key = (word, new_word_data['new_word'])  # Use tuple of 'original_word' and 'new_word' as unique key

    # If the key already exists, update case variations
    if key in valid_new_words:
        valid_new_words[key]['case_variations'].append(case_variation)
    else:
        # If it doesn't exist, create a new entry
        valid_new_words[key] = {
            'original_word': word,
            'new_word': new_word_data['new_word'],
            'case_variations': [case_variation],
            'starting_letter': new_word_data['starting_letter'],
            'offset': new_word_data['offset'],
            'direction': new_word_data['direction']
        }

    return valid_new_words

def process_word(word, check_vocab):
    valid_new_words = {}
    case_variations = generate_case_variations(word)

    for case_variation in case_variations:
        new_words = generate_new_words(case_variation)
        if not new_words.empty:
            potential_words = list(new_words['new_word'].str.lower())
            for ind, p_word in enumerate(potential_words):
                if p_word in (check_vocab):
                    valid_new_words = add_or_update_entry(word, new_words.iloc[ind], case_variation, valid_new_words)

    return pd.DataFrame.from_dict(valid_new_words, orient='index').reset_index(drop=True)

def verify_generated_word(original_word, new_word, direction):
    original_binary = text_to_binary(original_word)
    new_word_binary = text_to_binary(new_word)
    
    if direction == 'reverse':
        new_word_binary = new_word_binary[::-1]
    
    # Double the original binary to handle rotation
    rotational_binary = original_binary + original_binary
    
    return new_word_binary in rotational_binary


if __name__ == '__main__':
    word = 'Feuerwehreinsatzfahrzeug'

    pairs, potential_length = word_to_pairs(word)
    print(potential_length)
    print(pairs)
    pair_sequences = pairs_to_sequences(pairs, potential_length)
    for sequence in pair_sequences:
        print(sequence.to_string())
    new_words = sequences_to_words(pair_sequences)
    print(new_words.to_string())
