import itertools
from collections import defaultdict
from tqdm import tqdm
import supabase
from preprocess.get_vocabulary import load_word_list


def word_to_binary(word):
    return ''.join(format(ord(c), '08b') for c in word)

def binary_to_word(binary):
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def generate_case_variations(word):
    return [''.join(c.lower() if i & 1 else c.upper() for i, c in enumerate(word))
            for i in range(2**len(word))]

def find_ras_matches(vocab1, vocab2, include_case_variations=False, use_supabase=False):
    binary_dict = defaultdict(list)
    results = []

    # Initialize Supabase client if needed
    if use_supabase:
        supabase_url = "YOUR_SUPABASE_URL"
        supabase_key = "YOUR_SUPABASE_KEY"
        supabase_client = supabase.create_client(supabase_url, supabase_key)

    # Preprocess words into binary representations
    total_words = len(vocab1) + len(vocab2)
    with tqdm(total=total_words, desc="Preprocessing") as pbar:
        for word in itertools.chain(vocab1, vocab2):
            variations = generate_case_variations(word) if include_case_variations else [word]
            for variation in variations:
                binary = word_to_binary(variation)
                for i in range(len(binary)):
                    rotated = binary[i:] + binary[:i]
                    binary_dict[rotated].append((variation, i))
            pbar.update(1)

    # Find matches
    total_comparisons = len(vocab1) * len(vocab2) if vocab1 != vocab2 else len(vocab1) * (len(vocab1) - 1) // 2
    with tqdm(total=total_comparisons, desc="Finding matches") as pbar:
        for word1 in vocab1:
            variations1 = generate_case_variations(word1) if include_case_variations else [word1]
            for variation1 in variations1:
                binary1 = word_to_binary(variation1)
                for length in range(1, len(binary1) + 1):
                    for i in range(len(binary1)):
                        sub_binary = binary1[i:i+length] + binary1[:max(0, i+length-len(binary1))]
                        matches = binary_dict[sub_binary]
                        for variation2, offset in matches:
                            if variation2 in vocab2 and variation1 != variation2:
                                direction = "forward" if sub_binary == binary1[i:i+length] else "reverse"
                                match = {
                                    "word1": variation1,
                                    "word2": variation2,
                                    "offset": i,
                                    "length_diff": len(variation1) - len(variation2),
                                    "direction": direction
                                }
                                if use_supabase:
                                    supabase_client.table("ras_matches").insert(match).execute()
                                else:
                                    results.append(match)
            pbar.update(len(vocab2) if vocab1 != vocab2 else len(vocab1) - 1)

    return results

# Example usage
vocab1 = load_word_list('preprocess/vocabularies/meaningful_words/en.txt')
# vocab2 = load_word_list('preprocess/vocabularies/meaningful_words/de.txt')

matches = find_ras_matches(vocab1, vocab1, include_case_variations=True, use_supabase=False)

if not use_supabase:
    # Save results to a file
    with open('ras_matches.txt', 'w') as f:
        for match in matches:
            f.write(f"{match['word1']} matches {match['word2']} at offset {match['offset']}, "
                    f"length difference {match['length_diff']}, direction {match['direction']}\n")