def load_pairs(filename):
    with open(f'cache/{filename}.txt', 'r') as file:
        return {line.strip().split(':', 1)[0]: eval(line.strip().split(':', 1)[1]) for line in file}

def load_set(filename):
    with open(f'cache/{filename}.txt', 'r') as file:
        return set(line.strip() for line in file)

valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZäöüÄÖÜß-'
non_valid_pairs = load_set('non_valid_pairs')
valid_pairs = load_pairs('valid_pairs')

def save_pairs(filename, pairs):
    with open(f'cache/{filename}.txt', 'w') as file:
        for pair, values in pairs.items():
            file.write(f'{pair}: {values}\n')

def save_set(filename, set_):
    with open(f'cache/{filename}.txt', 'w') as file:
        for item in set_:
            file.write(f'{item}\n')