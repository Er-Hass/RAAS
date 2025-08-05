def save_pairs(filename, pairs):
    with open(f'cache/{filename}.txt', 'w') as file:
        for pair, values in pairs.items():
            file.write(f'{pair}: {values}\n')

def save_set(filename, set_):
    with open(f'cache/{filename}.txt', 'w') as file:
        for item in set_:
            file.write(f'{item}\n')
