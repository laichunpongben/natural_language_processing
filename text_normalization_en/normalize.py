import csv
import re
import pandas as pd
import inflect

# Unhandled
# 3691,2,"2008-18-03"
# BritannicaMark
# 1000 BCE

class TextNormalization(object):
    DIGIT = re.compile(r"^\d+$")
    DIGIT_COMMA_OPTIONAL = re.compile(r"^(\d+|\d{1,3}(,\d{3})*)(\.\d+)?$")
    TELEPHONE = re.compile(r"^[\d\-\(\)]+\d$")
    DECIMAL = re.compile(r"^\d*\.?\d+$")
    MONEY = re.compile(r"^\$?\-?([1-9]{1}[0-9]{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\-?\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\(\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))\)$")
    PERCENT = re.compile(r"\d+(?:\.\d+)?%")
    DATE_YYYYMMDD = re.compile(r"^[1-2]\d{3}\-[0-1]\d\-[0-3]\d$")
    DATE_EN_DMY = re.compile(r"^\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$")
    DATE_EN_MY = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$")
    DATE_EN_MDY = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}\, \d{4}$")
    MEASURE = None  # km²
    ELECTRONIC = None
    FRACTION = None
    KATAKANA = None
    KANJI = None  # 69155

    def __init__(self):
        self.test_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_test.csv'
        self.diff_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_train_truncated.csv'
        self.result_path = '/home/ben/github/natural_language_processing/text_normalization_en/result.csv'
        self.compare_path = '/home/ben/github/natural_language_processing/text_normalization_en/compare.csv'
        self.df_test = pd.read_csv(self.test_path)
        print(self.df_test.shape)

        self.df_diff = pd.read_csv(self.diff_path)

        self.d_replace = self.get_replace_dict()
        self.d_telephone = self.get_telephone_dict()
        self.digit_transcripter = inflect.engine()

    def get_replace_dict(self):
        is_verbatim = self.df_diff['class'] == 'VERBATIM'
        is_plain = self.df_diff['class'] == 'PLAIN'
        is_ordinal = self.df_diff['class'] == 'ORDINAL'
        df = self.df_diff[is_verbatim | is_plain | is_ordinal]
        df = df[['before', 'after']]
        d = df.set_index('before').T.to_dict('records')[0]
        d.pop('no', None)  # no -> number
        d.pop('I', None)  # I -> the first
        print(d)
        print(len(d.keys()))
        print(d['#'])
        return d

    def get_telephone_dict(self):
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
            '-': 'sil'
        }
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

    def normalize_year(self, text):
        d = {
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
            '1100': 'eleven hundred'
        }
        try:
            if text in d.keys():
                return d[text]
            else:
                prefix = self.digit_transcripter.number_to_words(text[:2])
                suffix = self.digit_transcripter.number_to_words(text[2:])
                text_ = prefix + ' ' + suffix
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
            print('case 0', text)
            return self.d_replace[text]
        elif text.isupper() and text.isalpha() and len(text) > 1 and not self.has_vowel(text):
            print('case 1', text)
            return " ".join(text.lower())
        elif text[:-2].isupper() and text.isalpha() and text[-2:] == "'s" and not self.has_vowel(text):
            print('case 2', text)
            return " ".join(text[:-2].lower()) + "'s"
        elif text[:-1].isupper() and text.isalpha() and text[-1:] == "s" and len(text) > 2 and not self.has_vowel(text):  # SEALs
            print('case 3', text)
            return " ".join(text[:-1].lower()) + " s"
        elif self.DIGIT.match(text) and 1100 <= int(text) <= 2099:
            print('case 4', text)
            return self.normalize_year(text)
        elif self.DECIMAL.match(text):  # DECIMAL
            print('case 5', text)
            text_ = self.digit_transcripter.number_to_words(text)
            text_ = text_.replace('-', ' ')
            text_ = text_.replace(',', '')
            return text_
        elif self.DIGIT_COMMA_OPTIONAL.match(text):  # DECIMAL
            print('case 6', text)
            text_ = self.digit_transcripter.number_to_words(text)
            text_ = text_.replace('-', ' ')
            text_ = text_.replace(',', '')
            return text_
        elif self.PERCENT.match(text):
            print('case 7', text)
            text_ = self.digit_transcripter.number_to_words(text[:-1]) + ' percent'
            text_ = text.replace('-', ' ')
            text_ = text.replace(',', '')
            return text_
        elif self.DATE_YYYYMMDD.match(text):
            print('case 8', text)
            year, month, day = text.split('-')
            try:
                normalized_year = self.normalize_year(year)
                normalized_month = self.normalize_month(month)
                normalized_day = self.normalize_day(day)
                text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_DMY.match(text):
            print('case 9', text)
            day, month, year = text.split(' ')
            try:
                normalized_year = self.normalize_year(year)
                normalized_month = month.lower()
                normalized_day = self.normalize_day(day)
                text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MY.match(text):
            print('case 10', text)
            month, year = text.split(' ')
            try:
                normalized_year = self.normalize_year(year)
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
            print('case 11', text)
            text0 = text.replace(',', '')
            month, day, year = text0.split(' ')
            try:
                normalized_year = self.normalize_year(year)
                normalized_month = month.lower()
                normalized_day = self.normalize_day(day)
                text_ = '{0} {1} {2}'.format(normalized_month, normalized_day, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.TELEPHONE.match(text):  # TELEPHONE
            print('case 12', text)
            text_ = text.replace('(', '')
            text_ = text_.replace(')', '')
            text_ = text_.replace(' ', '-')
            text_ = " ".join(text_)
            for k, v in self.d_telephone.items():
                text_ = text_.replace(k, v)
            return text_
        elif text.endswith('.') and len(text) > 1:  # LETTER
            print('case 13', text)
            text_ = text.replace('.', '').strip().lower()
            text_ = text_.replace(' ', '')
            text_ = " ".join(text_)
            return text_
        else:
            print('case 14', text)
            return text

    @staticmethod
    def get_verbatim():
        verbatim = {
            '-': 'to',
            '#': 'number', #hash
            '%': 'percent',
            '&': 'and',
            "π": "pi",
            "ρ": "rho",
            "ο": "omicron",
            "σ": "sigma",
            "ε": "epsilon",
            "υ": "upsilon",
            "χ": "chi",
            "θ": "theta",
            "τ": "tau",
            "ω": "omega",
            "ν": "nu",
            "η": "eta",
            "α": "alpha",
            "ζ": "zeta",
            "μ": "mu",
            "ς": "sigma",
            "γ": "gamma",
            "Ο": "omicron",
            "ι": "iota",
            "δ": "delta",
            "κ": "kappa",
            "Μ": "mu",
            "λ": "lambda",
            'pp': 'p p',
            'Dfb': 'd f b',
            'tr': 't r',
            'Bt': 'b t',
            'Bf': 'b f',
            'Kh': 'k h',
            'Rt': 'r t',
            'Phd': 'p h d',
            'pbk': 'pbk',
            'km': 'k m',
            'X h': 'x h',
            'F r': 'f r',
            'F t': 'f t',
            'vs': 'versus'
        }
        return verbatim


if __name__ == '__main__':
    text_normalization = TextNormalization()
    text_normalization.normalize_all()
