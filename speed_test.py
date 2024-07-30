from check_sequences import *
from get_vocabulary import *
import time


def speed_test(load, process, hardware):
    t = time.time()

    # Load
    if load == 'GetWords':
        test_set = get_meaningful_words('en')[0:1000]
    elif load == 'LoadMeaningful':
        test_set = load_word_list('vocabularies/meaningful_words/en.txt')[0:1000]

    # Process
    if process == 'inOperator':
        find_matches(["test"], test_set, name='Speed-Test', case_variations=True)

    # Save speed
    speed = time.time() - t
    run_name = f"{load}_{process}_{hardware}"
    print(f"{run_name + ':':40}{speed:3.3f} seconds")
    with open('runs.txt', 'a') as file:
        file.write(f"{run_name + ':':40}{speed:3.3f}\n")


if __name__ == '__main__':
    speed_test('GetWords', 'inOperator', 'CPU')
    speed_test('LoadMeaningful', 'inOperator', 'CPU')
