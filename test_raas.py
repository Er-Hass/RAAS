import unittest
from raas import *
import pandas as pd

class MyTestCase(unittest.TestCase):
    def test_word_to_binary(self):
        self.assertEqual(text_to_binary('hello'), '0110100001100101011011000110110001101111')


    def test_generate_case_variations(self):
        self.assertSetEqual(
            set(generate_case_variations('hel')),
            {'hel', 'Hel', 'hEl', 'heL', 'HEl', 'HeL', 'hEL', 'HEL'})


    def test_check_char_pair(self):
        valid_pairs = {}
        non_valid_pairs = set()
        check_char_pair('ab')
        check_char_pair('pa')
        self.assertEqual(valid_pairs, {'ab': [('C', 1, 'reverse'), ('h', 4, 'reverse'), ('X', 6, 'forward')]})
        self.assertEqual(non_valid_pairs, {'pa'})


    def test_word_to_pairs(self):
        word = 'Feuerwehrmanneinsatzfahrzeug'
        pairs, potential_length = word_to_pairs(word)
        self.assertEqual(potential_length, 28)
        self.assertEqual(len(pairs), 28)
        self.assertIn(0, pairs)
        self.assertIn(27, pairs)
        self.assertEqual(pairs[0], [('f', 4, 'forward'), ('f', 4, 'reverse'), ('L', 7, 'reverse')])
        self.assertEqual(pairs[27], [('s', 1, 'reverse'), ('t', 4, 'forward')])


    def test_pairs_to_sequences(self):
        word = 'Feuerwehrmanneinsatzfahrzeug'
        pairs, potential_length = word_to_pairs(word)
        pair_sequences = pairs_to_sequences(pairs, potential_length)
        
        self.assertIsInstance(pair_sequences, list)
        self.assertEqual(len(pair_sequences), 1)
        
        sequence = pair_sequences[0]
        self.assertIsInstance(sequence, pd.DataFrame)
        self.assertEqual(len(sequence), 28)
        self.assertEqual(list(sequence.columns), ['char', 'offset', 'direction'])
        
        # Test specific rows
        self.assertEqual(sequence.iloc[0]['char'], ['f', 'f', 'L'])
        self.assertEqual(sequence.iloc[0]['offset'], [4, 4, 7])
        self.assertEqual(sequence.iloc[0]['direction'], ['forward', 'reverse', 'reverse'])
        
        self.assertEqual(sequence.iloc[9]['char'], ['k', 'Ö', 'Ö', 'k', 'X'])
        self.assertEqual(sequence.iloc[9]['offset'], [3, 3, 4, 4, 6])
        self.assertEqual(sequence.iloc[9]['direction'], ['forward', 'reverse', 'forward', 'reverse', 'forward'])
        
        self.assertEqual(sequence.iloc[27]['char'], ['s', 't'])
        self.assertEqual(sequence.iloc[27]['offset'], [1, 4])
        self.assertEqual(sequence.iloc[27]['direction'], ['reverse', 'forward'])
        
        # Test that all rows have the correct structure
        for _, row in sequence.iterrows():
            self.assertIsInstance(row['char'], list)
            self.assertIsInstance(row['offset'], list)
            self.assertIsInstance(row['direction'], list)
            self.assertEqual(len(row['char']), len(row['offset']))
            self.assertEqual(len(row['char']), len(row['direction']))


    def test_handle_non_valid_pairs(self):
        pairs = {0: [('a', 1, 'forward')], 1: None, 2: [('a', 1, 'forward')], 3: [('b', 2, 'reverse')],
                 4: [('c', 3, 'forward')], 5: [('c', 3, 'forward')], 6: [('d', 4, 'reverse')], 7: [('e', 5, 'forward')]}
        potential_length = 7
        i = 4
        result_pairs, result_potential_length, result_i = handle_non_valid_pairs(pairs, potential_length, i)
        self.assertEqual(result_potential_length, 4)
        self.assertEqual(result_i, 5)
        self.assertEqual(result_pairs, {0: [('a', 1, 'forward')], 1: None, 2: None, 3: None, 4: None,
                                        5: [('c', 3, 'forward')], 6: [('d', 4, 'reverse')], 7: [('e', 5, 'forward')]})


    def test_create_sequence_dataframe(self):
        sequence = {
            0: [('a', 1, 'forward'), ('b', 2, 'reverse')],
            1: [('c', 3, 'forward')],
            2: [('d', 4, 'reverse'), ('e', 5, 'forward')]
        }
        df = create_sequence_dataframe(sequence)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ['char', 'offset', 'direction'])
        self.assertEqual(df['char'][0], ['a', 'b'])
        self.assertEqual(df['offset'][1], [3])
        self.assertEqual(df['direction'][2], ['reverse', 'forward'])


    def test_sequences_to_words(self):
        word = 'Feuerwehrmanneinsatzfahrzeug'
        pairs, potential_length = word_to_pairs(word)
        pair_sequences = pairs_to_sequences(pairs, potential_length)
        new_words = sequences_to_words(pair_sequences)

        self.assertIsInstance(new_words, pd.DataFrame)
        self.assertEqual(list(new_words.columns), ['new_word', 'starting_letter', 'offset', 'direction'])
        self.assertGreater(len(new_words), 0)

        # Test all generated words
        for _, row in new_words.iterrows():
            generated_word = row['new_word']
            direction = row['direction']

            self.assertTrue(
                verify_generated_word(word, generated_word, direction),
                f"Failed to verify '{generated_word}' in '{word}' with direction '{direction}'"
            )

        # Additional checks for DataFrame structure and content
        self.assertTrue(all(new_words['starting_letter'].between(0, len(word) - 1)))
        self.assertTrue(all(new_words['offset'].between(1, 7)))
        self.assertTrue(all(new_words['direction'].isin(['forward', 'reverse'])))
        self.assertTrue(all(new_words['new_word'].str.len() >= 4))
