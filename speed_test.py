from check_sequences import *
from preprocess.get_vocabulary import *
from check_WordCircles import *
from check_SimpleCircle import *
import time


def speed_test(load, process, hardware):
    t = time.time()

    # Load
    if load == 'GetWords':
        test_set = get_meaningful_words('en')[0:1000]
    elif load == 'LoadMeaningful':
        test_set = load_word_list('preprocess/vocabularies/meaningful_words/en.txt')[0:1000]

    l = time.time() - t

    # Process
    if process == 'inOpCaseVar':
        find_matches(test_set, ["test"], name='inOperator', case_variations=True)
    elif process == 'inOpSimpleUpLow':
        find_matches(test_set, ["test"], name='inOperatorSimple', upper_lower=True, simple=True)
    elif process == 'inOpSimpleCaseVar':
        find_matches(test_set, ["test"], name='inOpSimpleCaseVar', case_variations=True, simple=True)
    elif process == 'bitwise_xor':
        find_matches_wc(test_set, ["test"], name='bitwise_xor', case_variations=True)
    elif process == 'simpleCircle':
        find_matches_sc(test_set, ["test"], name='simpleCircle', case_variations=True)

    # Save speed
    speed = time.time() - l - t
    run_name = f"{load}_{process}_{hardware}"
    print(f"{run_name + ':':35}load_time: {l:7.3f}  calc_time: {speed:7.3f} seconds")
    with open('runs.txt', 'a') as file:
        file.write(f"{run_name + ':':35}load_time: {l:7.3f}  calc_time: {speed:7.3f} seconds\n")


if __name__ == '__main__':
    # speed_test('GetWords', 'inOp', 'CPU')
    # speed_test('LoadMeaningful', 'inOp', 'CPU')
    speed_test('LoadMeaningful', 'inOpSimpleUpLow', 'CPU')
    speed_test('LoadMeaningful', 'inOpSimpleCaseVar', 'CPU')
    # speed_test('LoadMeaningful', 'bitwise_xor', 'CPU')
    # speed_test('LoadMeaningful', 'simpleCircle', 'CPU')
