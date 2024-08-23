from get_vocabulary import *
from get_ascii_variations_db import *


if __name__ == '__main__':
    print(f"English words: {len(save_meaningful_words('en', min=4, max=10))}")
    print(f"German words: {len(save_meaningful_words('de', min=4, max=10))}")

    mp.set_start_method('spawn')
    main(workers=1)