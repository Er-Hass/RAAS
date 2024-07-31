from itertools import product
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class WordCircle:
    def __init__(self, word, case):
        self.word = word
        self.case = case

        self.circle_word = word + word
        self.backward = self.circle_word[::-1]
        self.sequence = self.word_to_sequence(word)
        self.length = len(self.sequence)

        if case:
            self.case_variations = self.generate_case_variations(word)
            self.case_sequences = [self.word_to_sequence(variation) for variation in self.case_variations]

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
        if other.word in self.circle_word or other.word in self.backward:
            return True

    def generate_circle(self, sequence, length):
        # Returns 2 lists of sequences to compare to, each representing a circle in one direction
        circle_f = []
        circle_b = []
        d_seq = torch.cat((sequence, sequence), 0)
        rev_seq = torch.flip(d_seq, [0])

        # Fill circles
        for i in range(0, self.length):
            if i > self.length - length + 1:
                circle_f.append(d_seq[i:i + length])
            circle_b.append(rev_seq[i:i + length])

        return circle_f, circle_b

    def check_sequence(self, other):
        # Self should always be the longer sequence
        zeros = torch.zeros_like(other.sequence)
        matches = []

        if self.case:
            for sv, ss in zip(self.case_variations, self.case_sequences):
                circle_f, circle_b = self.generate_circle(ss, len(other.sequence))
                for ov, os in zip(other.case_variations, other.case_sequences):
                    for ind, c in enumerate(circle_f):  # Forward circle
                        if torch.equal(torch.bitwise_xor(c, os), zeros):
                            # self case variation, other case variation, direction, offset
                            matches.append([sv, ov, 'forward', self.length - len(other.sequence) + 1 + ind])
                    for ind, c in enumerate(circle_b):  # Backward circle
                        if torch.equal(torch.bitwise_xor(c, os), zeros):
                            matches.append([sv, ov, 'backward', ind])
        else:
            circle_f, circle_b = self.generate_circle(self.sequence, len(other.sequence))
            for ind, c in enumerate(circle_f):  # Forward circle
                if torch.equal(torch.bitwise_xor(c, other.sequence), zeros):
                    # self case variation, other case variation, direction, offset
                    matches.append([self.word, other.word, 'forward', self.length - len(other.sequence) + 1 + ind])
            for ind, c in enumerate(circle_b):  # Backward circle
                if torch.equal(torch.bitwise_xor(c, other.sequence), zeros):
                    matches.append([self.word, other.word, 'backward', ind])

        return matches


if __name__ == '__main__':
    TILT = WordCircle('TILT', case=False)
    FREE = WordCircle('FREE', case=False)

    print(TILT.check_sequence(FREE))
