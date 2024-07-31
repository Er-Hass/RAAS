from itertools import product
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Torch device: {device}")


class WordCircle:
    def __init__(self, word, case):
        self.word = word
        self.case = case

        self.backward = self.word[::-1]
        self.sequence = self.word_to_sequence(word)
        self.b_seq = torch.flip(self.sequence, [0])
        self.zeros = torch.zeros_like(self.sequence)

        if case:
            self.case_variations = self.generate_case_variations(word)
            self.case_sequences = torch.stack([self.word_to_sequence(variation) for variation in self.case_variations])
            self.extended = self.case_sequences.repeat(self.case_sequences.shape[0], 1)
            self.backw_extended = torch.flip(self.case_sequences, [1]).repeat_interleave(self.case_sequences.shape[0], dim=0)

    def __eq__(self, other):
        if isinstance(other, WordCircle):
            return self.word == other.word
        return False

    def __len__(self):
        return len(self.word)

    @staticmethod
    def word_to_sequence(word):
        # Convert a word to a binary ASCII sequence as PyTorch tensor
        return torch.tensor([int(bit) for char in word for bit in format(ord(char), '08b')], device=device)

    @staticmethod
    def generate_case_variations(word):
        # Generate all upper and lower case combinations of the given word
        return [''.join(variation) for variation in product(*((c.lower(), c.upper()) for c in word))]

    def check_irrelevant(self, other):
        if other.word in self.backward:
            return True

    def check_sequence(self, other):
        if self.case:
            if torch.any(torch.all(torch.bitwise_xor(self.backw_extended, other.extended))):
                return [[self.word, other.word, 'backward', 0]]
        else:
            if not torch.any(torch.bitwise_xor(self.b_seq, other.sequence)):
                return [[self.word, other.word, 'backward', 0]]



if __name__ == '__main__':
    gun = WordCircle('gun', case=True)
    nug = WordCircle('nug', case=True)

    print(gun.check_sequence(nug))
