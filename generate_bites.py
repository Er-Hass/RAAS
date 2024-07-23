from take_a_bite import *
from get_vocabulary import *


if __name__ == '__main__':
    # en_words = get_meaningful_words('en')
    # print(f"Got {len(en_words)} English words")
    de_words = get_meaningful_words('de')
    print(f"Got {len(de_words)} German words")

    # # en-en
    # bitten_bytes = bite_off_byte(en_words, en_words)
    # bitten_bytes.to_csv('bitten_bytes/eng-eng.csv', index=False)
    #
    # # de-de
    # bitten_bytes = bite_off_byte(de_words, de_words)
    # bitten_bytes.to_csv('bitten_bytes/ger-ger.csv', index=False)
    #
    # # en-de
    # bitten_bytes = bite_off_byte(en_words, de_words)
    # bitten_bytes.to_csv('bitten_bytes/eng-ger.csv', index=False)

    # custom
    custom_words = ['hass', 'erik', 'babysex']
    bitten_bytes = bite_off_byte(custom_words, de_words)