import csv
import re
from collections import OrderedDict
import pandas as pd
import inflect

# Unhandled
# 3691,2,"2008-18-03" month 18
# 1000-300 BCE
# A&M
# 743712,10,"ELECTRONIC","#Grading","hash tag grading"
# Hockey-Reference.com
# 24-
# HHMU
# ISBN
# D'Amico
# US
# $502 million
# (1976) 198
# 111.0/km2
# 7 : 0 0 p m
# 1 : 0 5 a m
# 0:48
# 0:10:33
# 14:07.0
# 4.2.0.2
# 0.5MW
# 5-0 PSPS
# US$0.20
# PrintWPEC
# 0-17 IT
# 1 52-0 FNB
# 0-0 DSK
# .0.60
# .8.0
# .0
# 329.7 million
# $4.0 billion
# $0.75
# 0-9519288-3-XC
# 0-89281-505-1 CD
# 112298,0,"ELECTRONIC","127.0.0.1","o n e t w o s e v e n dot o dot o dot o n e"
# comhttp://www.thetimesonline.com/articles/2005/10/29/news/top_news/f9a7052f127cc0d4862570a8008314e3.txthttp://www.chicagotribune.com/business/showcase/chi-0308140292aug14,0,5485576,full.story
# //web.archive.org/20071206192005/http://www.thisislancashire.co.uk:80/news/headlines/display.var.1824340.0.petition_against_violence_gains_1_500_signatures.php

class TextNormalization(object):
    DIGIT = re.compile(r"^\d+$")
    DECIMAL_COMMA_OPTIONAL = re.compile(r"^(?:\d*|\d{1,3}(?:,\d{3})*)(?:\.\d+)?$")
    TELEPHONE = re.compile(r"^[\d \-\(\)]+\d$")
    IPv4 = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/?\d{0,2}$")
    DECIMAL = re.compile(r"^\d*\.?\d+$")
    MONEY = re.compile(r"^\$?\-?([1-9]{1}[0-9]{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\-?\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\(\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))\)$")
    PERCENT = re.compile(r"^\-?\d+(?:\.\d+)?(?:%| percent)$")
    DATE_YYYYMMDD = re.compile(r"^[1-2]\d{3}\-[0-1]\d\-[0-3]\d$")
    DATE_EN_DMY = re.compile(r"^\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$")
    DATE_EN_MY = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$")
    DATE_EN_MDY = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}\, \d{4}$")
    YEAR_CALENDAR = re.compile(r"^\d+ (?:BCE|CE|BC|AD|A\.D\.|B\.C\.|B\.C\.E\.|C\.E\.)\.?$")
    PROPER_CASE_CONCAT = re.compile(r"^(?:[A-Z][^A-Z\s\.]+){2,}$")
    MEASURE = re.compile(r"^(?:\d+|\d{1,3}(?:,\d{3})*)(?:\.\d+)?(?:\/| )?(?:m2|km|km2|km3|km²|km\/h|kg\/m3|g\/cm3|mg\/kg|sq mi|mi|MB|m|ha|cm|nm|ft|sq ft|Gy|AU|MW)$")  # km²
    ELECTRONIC = None
    FRACTION = None
    KATAKANA = None
    KANJI = None  # 69155
    URL = None

    digit_transcripter = inflect.engine()

    def __init__(self):
        self.test_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_test.csv'
        self.diff_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_train_truncated.csv'
        self.result_path = '/home/ben/github/natural_language_processing/text_normalization_en/result.csv'
        self.compare_path = '/home/ben/github/natural_language_processing/text_normalization_en/compare.csv'
        self.df_test = pd.read_csv(self.test_path)
        print(self.df_test.shape)

        self.df_diff = pd.read_csv(self.diff_path)

        self.d_replace = self.get_replace_dict()

    def get_replace_dict(self):
        is_verbatim = self.df_diff['class'] == 'VERBATIM'
        is_plain = self.df_diff['class'] == 'PLAIN'
        is_ordinal = self.df_diff['class'] == 'ORDINAL'
        df = self.df_diff[is_verbatim | is_plain | is_ordinal]
        df = df[['before', 'after']]
        d = df.set_index('before').T.to_dict('records')[0]
        d.pop('no', None)  # no -> number
        d.pop('I', None)  # I -> the first
        # print(d)
        # print(len(d.keys()))
        # print(d['#'])
        return d

    @staticmethod
    def has_vowel(text):
        if 'A' in text:
            return True
        elif 'E' in text:
            return True
        elif 'O' in text:
            return True
        elif 'I' in text:
            return True
        elif 'U' in text:
            return True
        else:
            return False

    @staticmethod
    def normalize_year(text):
        d = {
            '20000': 'twenty thousand',
            '19000': 'nineteen thousand',
            '18000': 'eighteen thousand',
            '17000': 'seventeen thousand',
            '16000': 'sixteen thousand',
            '15000': 'fifteen thousand',
            '14000': 'fourteen thousand',
            '13000': 'thirteen thousand',
            '12000': 'twelve thousand',
            '11000': 'eleven thousand',
            '10000': 'ten thousand',
            '9000': 'nine thousand',
            '8000': 'eight thousand',
            '7000': 'seven thousand',
            '6000': 'six thousand',
            '5000': 'five thousand',
            '4000': 'four thousand',
            '3000': 'three thousand',
            '2000': 'two thousand',
            '2001': 'two thousand one',
            '2002': 'two thousand two',
            '2003': 'two thousand three',
            '2004': 'two thousand four',
            '2005': 'two thousand five',
            '2006': 'two thousand six',
            '2007': 'two thousand seven',
            '2008': 'two thousand eight',
            '2009': 'two thousand nine',
            '1900': 'nineteen hundred',
            '1800': 'eighteen hundred',
            '1700': 'seventeen hundred',
            '1600': 'sixteen hundred',
            '1500': 'fifteen hundred',
            '1400': 'fourteen hundred',
            '1300': 'thirteen hundred',
            '1200': 'twelve hundred',
            '1100': 'eleven hundred',
            '1000': 'one thousand',
            '900': 'nine hundred',
            '800': 'eight hundred',
            '700': 'seven hundred',
            '600': 'six hundred',
            '500': 'five hundred',
            '400': 'four hundred',
            '300': 'three hundred',
            '200': 'two hundred',
            '100': 'one hundred',
        }
        try:
            if text in d.keys():
                return d[text]
            else:
                if len(text) > 2:
                    prefix = TextNormalization.digit_transcripter.number_to_words(text[:-2])
                    suffix = TextNormalization.digit_transcripter.number_to_words(text[-2:])
                    text_ = prefix + ' ' + suffix
                else:
                    text_ = TextNormalization.digit_transcripter.number_to_words(text)
                text_ = text_.replace('-', ' ')
                text_ = text_.replace(',', '')
                return text_
        except Exception as e:
            print(e)
            print(text)
            # return text
            raise

    @staticmethod
    def normalize_month(text):
        month = int(text)
        d = {
            1: 'january',
            2: 'february',
            3: 'march',
            4: 'april',
            5: 'may',
            6: 'june',
            7: 'july',
            8: 'august',
            9: 'september',
            10: 'october',
            11: 'november',
            12: 'december'
        }
        return d[month]

    @staticmethod
    def normalize_day(text):
        day = int(text)
        d = {
            1: 'first',
            2: 'second',
            3: 'third',
            4: 'fourth',
            5: 'fifth',
            6: 'sixth',
            7: 'seventh',
            8: 'eighth',
            9: 'ninth',
            10: 'tenth',
            11: 'eleventh',
            12: 'twelfth',
            13: 'thirteenth',
            14: 'fourteenth',
            15: 'fifteenth',
            16: 'sixteenth',
            17: 'seventeenth',
            18: 'eighteenth',
            19: 'nineteenth',
            20: 'twentieth',
            21: 'twenty first',
            22: 'twenty second',
            23: 'twenty third',
            24: 'twenty fourth',
            25: 'twenty fifth',
            26: 'twenty sixth',
            27: 'twenty seventh',
            28: 'twenty eighth',
            29: 'twenty ninth',
            30: 'thirtieth',
            31: 'thirty first',
        }
        return d[day]

    @staticmethod
    def normalize_year_calendar(text):
        text_ = text.replace('.', '')
        year, suffix = text_.split(' ')
        normalized_year = TextNormalization.normalize_year(year)
        normalized_suffix = " ".join(suffix.lower())
        text_ = normalized_year + ' ' + normalized_suffix
        return text_

    @staticmethod
    def normalize_proper_case_concat(text):
        text_ = text.replace(' ', '')
        text_ = text.replace("'", '')
        words = re.findall('[A-Z][^A-Z]*', text_)
        text_ = " ".join(words)
        text_ = text_.lower()
        return text_

    @staticmethod
    def normalize_telephone(text):
        d = {
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine',
            '0': 'o',
            '-': 'sil',
            '.': 'dot'
        }

        text_ = text.replace('(', '')
        text_ = text_.replace(')', '')
        text_ = text_.replace(' ', '-')
        text_ = " ".join(text_)
        for k, v in d.items():
            text_ = text_.replace(k, v)
        return text_

    @staticmethod
    def normalize_ipv4(text):
        d = {
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine',
            '0': 'o',
            '-': 'sil',
            '.': 'dot',
            '/': 'slash'
        }

        normalized_texts = []
        subnet = None
        if '/' in text:
            text, subnet = text.split('/')
        ip_nums = text.split('.')
        for x in ip_nums:
            if int(x) > 100:
                num_text = " ".join(x)
                for k, v in d.items():
                    num_text = num_text.replace(k, v)
                normalized_texts.append(num_text)
            else:
                normalized_texts.append(TextNormalization.digit_transcripter.number_to_words(int(x)))
        normalized_text = " dot ".join(normalized_texts)

        if subnet:
            normalized_subnet = TextNormalization.digit_transcripter.number_to_words(int(subnet))
            normalized_text += ' slash {0}'.format(normalized_subnet)

        normalized_text = normalized_text.replace('-', ' ')
        normalized_text = normalized_text.replace(',', '')

        return normalized_text

    @staticmethod
    def normalize_measure(text):
        # m2|km|km2|km3|km²|km\/h|g\/cm3|mg\/kg|sq mi|mi|MB|m|ha|cm|nm|ft|sq ft|Gy|AU|MW
        measure, normalized_measure = None, None
        d = OrderedDict([
            ('km/h', 'kilometers per hour'),
            ('kg/m3', 'kilograms per cubic meter'),
            ('g/cm3', 'gram per c c'),
            ('mg/kg', 'milligrams per kilogram'),
            ('km2', 'square kilometers'),
            ('km3', 'cubic kilometers'),
            ('km²', 'square kilometers'),
            ('km', 'kilometers'),
            ('m2', 'square meters'),
            ('sq mi', 'square miles'),
            ('mi', 'miles'),
            ('sq ft', 'square feet'),
            ('ft', 'feet'),
            ('m2', 'square meters'),
            ('cm', 'centimeters'),
            ('nm', 'nanometers'),
            ('ha', 'hectares'),
            ('Gy', 'gray'),
            ('AU', 'astronomical units'),
            ('MW', 'megawatts'),
            ('MB', 'megabytes'),
            ('m', 'meters'),
        ])
        text_ = text
        for k, v in d.items():
            if k in text_:
                measure, normalized_measure = k, v
                text_ = text_.replace(k, '')
                break

        if text_.endswith('/'):
            is_per = True
            text_ = text_.replace('/', '')
        else:
            is_per = False

        normalized_text = TextNormalization.digit_transcripter.number_to_words(text_)
        normalized_text = normalized_text.replace('-', ' ')
        normalized_text = normalized_text.replace(',', '')

        if is_per:
            normalized_text += ' per'

        normalized_text += ' '
        normalized_text += normalized_measure
        return normalized_text

    def normalize_all(self):
        print('start normalization')
        self.df_test['after'] = self.df_test['before'].apply(lambda x: self.normalize(x))

        print('make id')
        self.df_test['id'] = self.df_test['sentence_id'].map(str) + '_' + self.df_test['token_id'].map(str)

        print('make sub df')
        df_compare = self.df_test[['id', 'before', 'after']]
        df_compare = df_compare[df_compare['before'] != df_compare['after']]

        df_result = self.df_test[['id', 'after']]

        print('save as csv')
        df_compare.to_csv(self.compare_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
        df_result.to_csv(self.result_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

    def normalize(self, text):
        if text in self.d_replace.keys():
            print('Case REPLACE', text)
            return self.d_replace[text]
        elif text.isupper() and text.isalpha() and len(text) > 1 and self.has_vowel(text):
            print('Case UPPER_WORD', text)
            return text
        elif text.isupper() and text.isalpha() and len(text) > 1 and not self.has_vowel(text):
            print('Case UPPER_NON_WORD', text)
            return " ".join(text.lower())
        elif text[:-2].isupper() and text.isalpha() and text[-2:] == "'s" and not self.has_vowel(text):
            print('Case UPPER_S_0', text)
            return " ".join(text[:-2].lower()) + "'s"
        elif text[:-1].isupper() and text.isalpha() and text[-1:] == "s" and len(text) > 2 and not self.has_vowel(text):  # SEALs
            print('Case UPPER_S_1', text)
            return " ".join(text[:-1].lower()) + "'s"
        elif self.DIGIT.match(text) and 1100 <= int(text) <= 2099:
            print('Case YEAR', text)
            return TextNormalization.normalize_year(text)
        elif self.YEAR_CALENDAR.match(text):
            print('Case YEAR_CALENDAR', text)
            return TextNormalization.normalize_year_calendar(text)
        elif self.DECIMAL_COMMA_OPTIONAL.match(text):  # DECIMAL
            print('Case DECIMAL_COMMA_OPTIONAL', text)
            text_ = TextNormalization.digit_transcripter.number_to_words(text)
            text_ = text_.replace('-', ' ')
            text_ = text_.replace(',', '')
            return text_
        elif self.PERCENT.match(text):
            print('Case PERCENT', text)
            if text.startswith('-'):
                is_minus = True
            else:
                is_minus = False

            text_ = text.replace('-', ' ')

            if text_.endswith('%'):
                text_ = TextNormalization.digit_transcripter.number_to_words(text_[:-1]) + ' percent'
            else:
                text_ = TextNormalization.digit_transcripter.number_to_words(text_.split(' ')[0]) + ' percent'
            text_ = text_.replace('-', ' ')
            text_ = text_.replace(',', '')

            if is_minus:
                text_ = 'minus ' + text_
            return text_
        elif self.DATE_YYYYMMDD.match(text):
            print('Case DATE_YYYYMMDD', text)
            year, month, day = text.split('-')
            try:
                normalized_year = TextNormalization.normalize_year(year)
                normalized_month = TextNormalization.normalize_month(month)
                normalized_day = TextNormalization.normalize_day(day)
                text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_DMY.match(text):
            print('Case DATE_EN_DMY', text)
            day, month, year = text.split(' ')
            try:
                normalized_year = TextNormalization.normalize_year(year)
                normalized_month = month.lower()
                normalized_day = TextNormalization.normalize_day(day)
                text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MY.match(text):
            print('Case DATE_EN_MY', text)
            month, year = text.split(' ')
            try:
                normalized_year = TextNormalization.normalize_year(year)
                normalized_month = month.lower()
                text_ = '{0} {1}'.format(normalized_month, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MDY.match(text):
            print('Case DATE_EN_MDY', text)
            text0 = text.replace(',', '')
            month, day, year = text0.split(' ')
            try:
                normalized_year = TextNormalization.normalize_year(year)
                normalized_month = month.lower()
                normalized_day = TextNormalization.normalize_day(day)
                text_ = '{0} {1} {2}'.format(normalized_month, normalized_day, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.TELEPHONE.match(text):  # TELEPHONE
            print('Case TELEPHONE', text)
            return TextNormalization.normalize_telephone(text)
        elif self.IPv4.match(text):
            print('Case IPv4', text)
            return TextNormalization.normalize_ipv4(text)
        elif self.MEASURE.match(text):
            print('Case MEASURE', text)
            return TextNormalization.normalize_measure(text)
        elif self.PROPER_CASE_CONCAT.match(text):
            print('Case PROPER_CASE_CONCAT', text)
            return TextNormalization.normalize_proper_case_concat(text)
        elif text.endswith('.') and len(text) > 1:  # LETTER
            print('Case LETTER', text)
            text_ = text.replace('.', '').strip().lower()
            text_ = text_.replace(' ', '')
            text_ = " ".join(text_)
            return text_
        else:
            print('Case NO_CHANGE', text)
            return text

if __name__ == '__main__':
    test_cases = [
        'OutRun',
        '0-306-80821-8',
        '2012-08-16',
        '432 BCE',
        '432 BC.',
        '53 CE',
        '4000 B.C.',
        'WORLD',
        'O. C.',
        "D'Amigo",
        "-0.7%",
        "25%",
        "1.08 percent",
        '0-306-80821-8',
        '0 9512309 6 4',
        '127.0.0.1',
        '192.168.5.20/24',
        '2500 MW',
        '4.9 km2',
        '5km2',
        '26.9/km2',
        '11.8 MB',
        '0.7 kg/m3'
    ]

    text_normalization = TextNormalization()
    text_normalization.normalize_all()

    for test_case in test_cases:
        normalized_text = text_normalization.normalize(test_case)
        print(normalized_text)
        print()
