import unittest
from raas import *


class MyTestCase(unittest.TestCase):
    def test_word_to_binary(self):
        self.assertEqual(word_to_binary('hello'), '0110100001100101011011000110110001101111')

    # def test_binary_to_word(self):
    #     self.assertEqual(binary_to_word('0110100001100101011011000110110001101111'), 'hello')

    def test_generate_case_variations(self):
        self.assertSetEqual(
            set(generate_case_variations('hel')),
            {'hel', 'Hel', 'hEl', 'heL', 'HEl', 'HeL', 'hEL', 'HEL'})

    def test_check_char_pair(self):
        check_char_pair('ab')
        check_char_pair('pa')
        self.assertEqual(valid_pairs, {'ab': [('C', 1, 'reverse'), ('h', 4, 'reverse'), ('X', 6, 'forward')]})
        self.assertEqual(non_valid_pairs, {'pa'})
