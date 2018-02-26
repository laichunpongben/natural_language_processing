#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import argparse
from naoqi import ALProxy
from text_normalization import TextNormalization

if __name__ == '__main__':
    test_cases = [
        ['The telephone number is', '25588117'],
        ['The ISBN of this book is', '9780300114652'],
        ['My date of birth is', '11/2/2010'],
        ['Today is', '23.01.2015'],
        ['Tomorrow is', 'Sun May 1st, 2009'],
        ['28 FEBRUARY 2008'],
        ['22 May'],
        ['CXIII'],
        ['Louis', 'XVI', 'of France was guillotined on', '1973/1/21'],
        ['4.9 km2'],
        ['The density of this liquid is', '0.95 g/cm3'],
        ['My IP is', '192.168.54.201'],
        ['The price of the new iphone is', '€800'],
        ['我嘅IP係', '192.168.54.201'],
        ['公司電話號碼係', '25588117'],
        ['新iphone賣', '€800'],
        ['新iphone賣', '¥8000'],
        ['今日係', '1973/18/21']
    ]

    ip = '10.42.0.193'
    port = 9559
    sb_language = 'English'
    # sb_language = 'CantoneseHK'

    tn = TextNormalization()
    tts = ALProxy('ALTextToSpeech', ip, port)
    # tts.setLanguage(sb_language)

    id_ = -10
    text0 = ' '.join(test_cases[id_])
    tts.say(text0, sb_language)

    language_dict = {
        'English': 'en_US',
        'CantoneseHK': 'zh_Hant_HK'
    }
    language = language_dict[sb_language]
    text1 = ' '.join([tn.normalize(word, language) for word in test_cases[id_]])
    tts.say(text1, sb_language)
