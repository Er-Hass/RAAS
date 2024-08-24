from preprocess.get_vocabulary import load_word_list
from cache.load_and_save import *


def generate_case_variations(word):
    variations = []
    for i in range(2**len(word)):
        variation = ''.join(c.upper() if (i & (1 << j)) else c.lower()
                            for j, c in enumerate(word))
        variations.append(variation)
    return variations

def word_to_binary(word):
    return ''.join(format(ord(c), '08b') for c in word)

# def binary_to_word(binary):
#     return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def check_char_pair(pair):
    pair_b = word_to_binary(pair)
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

        if none_distance < 4 or rotational_none_distance < 4:  # Less than 4 pairs between
            if none_distance < 4:
                for j in range(second_last_none + 1, last_none):
                    pairs[j] = None
                    potential_length -= 1
            if rotational_none_distance < 4:
                for j in range(last_none + 1, len(pairs)):
                    pairs[j] = None
                    potential_length -= 1
                for j in range(0, first_none):
                    pairs[j] = None
                    potential_length -= 1

    return pairs, potential_length-1, i+1

def check_word(word):
    word_length = len(word)
    potential_length = word_length
    pairs = {}

    i = 0
    while potential_length >= 4 and i < word_length:
        try:
            pair = word[i] + word[(i + 1) % word_length]
        except IndexError as e:
            print(e)

        if pair in non_valid_pairs:
            pairs, potential_length, i = handle_non_valid_pairs(pairs, potential_length, i)
            continue

        elif pair in valid_pairs:
            pairs[i] = valid_pairs[pair]
            i += 1

        else:
            check_char_pair(pair)

    if potential_length < 4:
        return None
    else:
        # Create the pair sequences
        pair_sequences = []
        none_indices = [j for j, v in pairs.items() if v is None]

        if none_indices == []:
            pair_sequences.append([v for v in pairs.values()])
        else:
            # Rotational sequence
            rotational_sequence = []
            if none_indices[0] > 0:
                rotational_sequence.extend([pairs[j] for j in range(none_indices[0])])
            if none_indices[-1] < max(pairs.keys()):
                rotational_sequence.extend([pairs[j] for j in range(none_indices[-1] + 1, max(pairs.keys()) + 1)])

            if rotational_sequence:
                pair_sequences.append(rotational_sequence)
            
            # Add sequences between None values
            for start, end in zip(none_indices, none_indices[1:]):
                pair_sequences.append([pairs[j] for j in range(start + 1, end)])
    
    for ind, seq in enumerate(pair_sequences):
        print(f"{ind}: {seq}\n{len(seq)}")
        
        



if __name__ == '__main__':
    check_word('Feuerwehrmann')