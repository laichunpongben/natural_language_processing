# -*- encoding: UTF-8 -*-

import csv
import re
from collections import OrderedDict
import pandas as pd
import inflect
import roman

# Unhandled
# MMDDYYYY or DDMMYYYY
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
# €1.2 billion
# $0.75
# 0-9519288-3-XC
# 0-89281-505-1 CD
# 1960s
# (1999)1
# "$1.50","one dollar and fifty cents"
# "66511_9","June 23 rd 2014"
# telephone three o o -> three hundred
# 112298,0,"ELECTRONIC","127.0.0.1","o n e t w o s e v e n dot o dot o dot o n e"
# comhttp://www.thetimesonline.com/articles/2005/10/29/news/top_news/f9a7052f127cc0d4862570a8008314e3.txthttp://www.chicagotribune.com/business/showcase/chi-0308140292aug14,0,5485576,full.story
# //web.archive.org/20071206192005/http://www.thisislancashire.co.uk:80/news/headlines/display.var.1824340.0.petition_against_violence_gains_1_500_signatures.php


class TextNormalization(object):
    YEAR = re.compile(r"^[1-9]\d{3} ?$")
    LEADING_ZERO = re.compile(r"^0(?=\d)(?:\d*|\d{1,3}(?:(?: |,)\d{3})*)$")
    DECIMAL_COMMA_OPTIONAL = re.compile(r"^\-?(?=(?:\.|\d))(?:\d*|\d{1,3}(?:(?: |,)\d{3})*)(?:\.\d+)?$")
    ISBN = re.compile(r"^\d[-\d]{11,}\d$")
    TELEPHONE = re.compile(r"^[\d \-\(\)]+\d$")
    TELEPHONE_COMMON = re.compile(r"^(911|999|9-1-1|9-9-9)$")
    IPv4 = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/?\d{0,2}$")
    DECIMAL = re.compile(r"^\d*\.?\d+$")
    MONEY = re.compile(r"^\$?\-?([1-9]{1}[0-9]{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\-?\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))$|^\(\$?([1-9]{1}\d{0,2}(\,\d{3})*(\.\d{0,2})?|[1-9]{1}\d{0,}(\.\d{0,2})?|0(\.\d{0,2})?|(\.\d{1,2}))\)$")
    PERCENT = re.compile(r"^\-?(?=(?:\.|\d))\d+(?:\.\d+)?(?:%| percent)$")
    DATE_YYYYMMDD = re.compile(r"^[1-2]\d{3}(?:\-|\/|\.)(0[1-9]|1[012])(?:\-|\/|\.)?(0[1-9]|[12]\d|3[01])$")
    DATE_MMDDYYYY = re.compile(r"^(0[1-9]|1[012])(?:\-|\/|\.)?(0[1-9]|[12]\d|3[01])(?:\-|\/|\.)?[1-2]\d{3}$")
    DATE_DDMMYYYY = re.compile(r"^(0[1-9]|[12]\d|3[01])(?:\-|\/|\.)?(0[1-9]|1[012])(?:\-|\/|\.)?[1-2]\d{3}$")
    DATE_YYYYMD = re.compile(r"^[1-2]\d{3}(?:\-|\/|\.)([1-9]|1[012])(?:\-|\/|\.)([1-9]|[12]\d|3[01])$")
    DATE_MDYYYY = re.compile(r"^([1-9]|1[012])(?:\-|\/|\.)([1-9]|[12]\d|3[01])(?:\-|\/|\.)[1-2]\d{3}$")
    DATE_DMYYYY = re.compile(r"^([1-9]|[12]\d|3[01])(?:\-|\/|\.)([1-9]|1[012])(?:\-|\/|\.)[1-2]\d{3}$")
    DATE_MMDDYY = re.compile(r"^[0-1]?\d(?:\-|\/|\.)[0-3]?\d(?:\-|\/|\.)\d{2}$")
    DATE_DDMMYY = re.compile(r"^[0-3]?\d(?:\-|\/|\.)[0-1]?\d(?:\-|\/|\.)\d{2}$")
    DATE_MMDD = re.compile(r"^0\d(?:\-|\/|\.)[0-3]\d$")
    DATE_EN_DMY = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?(\, | )?\d{1,2}(?:st|nd|rd|th)? (January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)\.? \d{4}$")
    DATE_EN_DM = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?(\, | )?\d{1,2}(?:st|nd|rd|th)? (January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)\.? ?$")
    DATE_EN_MD = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?(\, | )?(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)\.? \d{1,2}(?:st|nd|rd|th)? ?$")
    DATE_EN_MY = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?(\, | )?(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)\.? \d{4}$")
    DATE_EN_MDY = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?(\, | )?(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)\.? \d{1,2}(?:st|nd|rd|th)?\, \d{4}$")
    YEAR_CALENDAR = re.compile(r"^\d+ (?:BCE|CE|BC|AD|A\.D\.|B\.C\.|B\.C\.E\.|C\.E\.)\.?$")
    TIME = re.compile(r"^\d{4}-\d{4}$")
    PROPER_CASE_CONCAT = re.compile(r"^(?:[A-Z][^A-Z\s\.]+){2,}$")
    MEASURE = re.compile(r"^(?:\d+|\d{1,3}(?:,\d{3})*)(?:\.\d+)?(?:\/| )?(?:m2|m3|km|km2|km3|km²|km\/h|kg\/m3|g\/cm3|mg\/kg|kg|lb|sq mi|mi2|mi|MB|m|ha|cm|nm|mm|ft|sq ft|kHz|Hz|Gy|AU|MW|\"\")$")  # km²
    ROMAN = re.compile(r"^(?=[MDCLXVI]{3,})M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})$")
    ELECTRONIC = None
    FRACTION = None
    KATAKANA = None
    KANJI = None  # 69155, 67022
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
        d.pop(':', None)  # : -> to
        d.pop('-', None)  # - -> to
        d.pop('—', None)  # - -> to
        d.pop('x', None)  # x -> by
        d.pop('X', None)  # x -> tenth
        d['፬'] = 'four'
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
    def normalize_year(text, language='en_US'):
        if language != 'en_US':
            return text

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
                    if text[-2:].startswith('0'):
                        suffix = 'o ' + suffix
                    text_ = prefix + ' ' + suffix
                else:
                    text_ = TextNormalization.digit_transcripter.number_to_words(text)
                    if text.startswith('0'):
                        text_ = 'o ' + text_
                text_ = text_.replace('-', ' ')
                text_ = text_.replace(',', '')
                text_ = text_.replace(' and ', ' ')
                return text_
        except Exception as e:
            print(e)
            print(text)
            raise

    @staticmethod
    def normalize_month(text, language='en_US'):
        if language != 'en_US':
            return text

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
    def normalize_day(text, language='en_US'):
        if language != 'en_US':
            return text

        text_ = text
        if not text_.isdigit():
            text_ = text[:-2]
        day = int(text_)
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
    def normalize_en_month(text):
        d = {
            'jan': 'january',
            'feb': 'february',
            'mar': 'march',
            'apr': 'april',
            'may': 'may',
            'jun': 'june',
            'june': 'june',
            'jul': 'july',
            'july': 'july',
            'aug': 'august',
            'sep': 'september',
            'sept': 'september',
            'oct': 'october',
            'nov': 'november',
            'dec': 'december'
        }
        return d[text.lower()]

    @staticmethod
    def normalize_weekday(text):
        d = {
            'mon': 'monday',
            'tue': 'tuesday',
            'wed': 'wednesday',
            'thu': 'thursday',
            'fri': 'friday',
            'sat': 'saturday',
            'sun': 'sunday'
        }
        return d[text.lower()]

    @staticmethod
    def normalize_proper_case_concat(text):
        text_ = text.replace(' ', '')
        text_ = text.replace("'", '')
        words = re.findall('[A-Z][^A-Z]*', text_)
        text_ = " ".join(words)
        text_ = text_.lower()
        return text_

    @staticmethod
    def normalize_telephone_common(text):
        common = {
            '911': 'nine one one',
            '999': 'nine nine nine',
            '9-1-1': 'nine one one',
            '9-9-9': 'nine nine nine',
        }
        return common[text]

    @staticmethod
    def normalize_telephone(text, language='en_US'):
        text_ = text.replace('(', '')
        text_ = text_.replace(')', '-')
        text_ = text_.replace(' ', '-')
        text_ = re.sub(r"\-+", r"-", text_)
        text_ = " ".join(text_)

        if language == 'en_US':
            d = OrderedDict([
                ('- 1 2 0 0 -', 'sil twelve hundred sil'),
                ('- 1 1 0 0 -', 'sil eleven hundred sil'),
                ('- 1 0 0 0 -', 'sil one thousand sil'),
                ('- 0 9 0 0 -', 'sil o nine hundred sil'),
                ('- 0 8 0 0 -', 'sil o eight hundred sil'),
                ('- 0 7 0 0 -', 'sil o seven hundred sil'),
                ('- 0 6 0 0 -', 'sil o six hundred sil'),
                ('- 0 5 0 0 -', 'sil o five hundred sil'),
                ('- 0 4 0 0 -', 'sil o four hundred sil'),
                ('- 0 3 0 0 -', 'sil o three hundred sil'),
                ('- 0 2 0 0 -', 'sil o two hundred sil'),
                ('- 0 1 0 0 -', 'sil o one hundred sil'),
                ('- 9 0 0 -', 'sil nine hundred sil'),
                ('- 8 0 0 -', 'sil eight hundred sil'),
                ('- 7 0 0 -', 'sil seven hundred sil'),
                ('- 6 0 0 -', 'sil six hundred sil'),
                ('- 5 0 0 -', 'sil five hundred sil'),
                ('- 4 0 0 -', 'sil four hundred sil'),
                ('- 3 0 0 -', 'sil three hundred sil'),
                ('- 2 0 0 -', 'sil two hundred sil'),
                ('- 1 0 0 -', 'sil one hundred sil'),
                ('1', 'one'),
                ('2', 'two'),
                ('3', 'three'),
                ('4', 'four'),
                ('5', 'five'),
                ('6', 'six'),
                ('7', 'seven'),
                ('8', 'eight'),
                ('9', 'nine'),
                ('0', 'o'),
                ('.', 'dot'),
                ('-', 'sil'),
            ])
        else:
            d = OrderedDict([
                ('1', '一'),
                ('2', '二'),
                ('3', '三'),
                ('4', '四'),
                ('5', '五'),
                ('6', '六'),
                ('7', '七'),
                ('8', '八'),
                ('9', '九'),
                ('0', '零'),
            ])

        for k, v in d.items():
            text_ = text_.replace(k, v)

        return text_

    @staticmethod
    def normalize_leading_zero(text):
        d = OrderedDict([
            ('1', 'one'),
            ('2', 'two'),
            ('3', 'three'),
            ('4', 'four'),
            ('5', 'five'),
            ('6', 'six'),
            ('7', 'seven'),
            ('8', 'eight'),
            ('9', 'nine'),
            ('0', 'o'),
            ('-', 'sil')
        ])

        text_ = text.replace('(', '')
        text_ = text_.replace(')', '')
        text_ = text_.replace(' ', '-')
        text_ = " ".join(text_)
        for k, v in d.items():
            text_ = text_.replace(k, v)
        return text_

    @staticmethod
    def normalize_ipv4(text, language='en_US'):
        if language == 'en_US':
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
        else:
            d = {
                '1': '一',
                '2': '二',
                '3': '三',
                '4': '四',
                '5': '五',
                '6': '六',
                '7': '七',
                '8': '八',
                '9': '九',
                '0': '零',
                '.': ',點,',
            }

        normalized_texts = []
        subnet = None
        if '/' in text:
            text, subnet = text.split('/')

        if language == 'en_US':
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
            normalized_text = normalized_text.replace(' and ', ' ')
        else:
            normalized_text = text
            for k, v in d.items():
                normalized_text = normalized_text.replace(k, v)

        return normalized_text

    @staticmethod
    def normalize_measure(text):
        # m3|m2|km|km2|km3|km²|km\/h|g\/cm3|mg\/kg|kg|lb|sq mi|mi2|mi|MB|m|ha|cm|nm|mm|ft|sq ft|kHz|Hz|Gy|AU|MW|\"\"
        measure, normalized_measure = None, None
        d = OrderedDict([
            ('km/h', ['kilometers per hour', 'kilometer per hour']),
            ('kg/m3', ['kilograms per cubic meter', 'kilogram per cubic meter']),
            ('g/cm3', ['grams per c c', 'gram per c c']),
            ('mg/kg', ['milligrams per kilogram', 'milligram per kilogram']),
            ('kHz', ['kilohertz', 'kilohertz']),
            ('km2', ['square kilometers', 'square kilometer']),
            ('km3', ['cubic kilometers', 'cubic kilometer']),
            ('km²', ['square kilometers', 'square kilometer']),
            ('km', ['kilometers', 'kilometer']),
            ('kg', ['kilograms', 'kilogram']),
            ('lb', ['pounds', 'pound']),
            ('m2', ['square meters', 'square meter']),
            ('m3', ['cubic meters', 'cubic meter']),
            ('sq mi', ['square miles', 'square mile']),
            ('mi2', ['square miles', 'square mile']),
            ('mi', ['miles', 'mile']),
            ('sq ft', ['square feet', 'square foot']),
            ('ft', ['feet', 'foot']),
            ('m2', ['square meters', 'square meter']),
            ('cm', ['centimeters', 'centimeter']),
            ('nm', ['nanometers', 'nanometer']),
            ('mm', ['millimeters', 'millimeter']),
            ('ha', ['hectares', 'hectare']),
            ('Hz', ['hertz', 'hertz']),
            ('Gy', ['grays', 'gray']),
            ('AU', ['astronomical units', 'astronomical unit']),
            ('MW', ['megawatts', 'megawatt']),
            ('MB', ['megabytes', 'megabyte']),
            ('""', ['inches', 'inch']),
            ('m', ['meters', 'meter']),
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

        normalized_text = TextNormalization.normalize_decimal(text_)
        if normalized_text == 'one':
            normalized_measure = normalized_measure[1]
        else:
            normalized_measure = normalized_measure[0]

        if is_per:
            normalized_text += ' per'

        normalized_text += ' '
        normalized_text += normalized_measure
        return normalized_text

    @staticmethod
    def normalize_decimal(text):
        text_ = TextNormalization.digit_transcripter.number_to_words(text)
        text_ = text_.replace('-', ' ')
        text_ = text_.replace(',', '')
        text_ = text_.replace(' and ', ' ')

        if text.isdigit():
            if all(c == '0' for c in text) and len(text) > 1:
                text_ = ' '.join('o' * len(text))
            else:
                len_leading_zero = len(text) - len(str(int(text)))
                text_ = 'o ' * len_leading_zero + text_

        if 'point' in text_:
            prefix, suffix = text_.split('point')
            if suffix != ' zero' or not prefix:
                suffix = suffix.replace('zero', 'o')
            text_ = prefix + 'point' + suffix
        return text_

    @staticmethod
    def normalize_roman(text):
        if len(text) <= 1:
            return text
        elif len(text) == 2:
            if text in ['IV', 'VI']:
                int_ = str(roman.fromRoman(text))
                text_ = TextNormalization.normalize_decimal(int_)
                return text_
            else:
                return text
        else:
            int_ = str(roman.fromRoman(text))
            text_ = TextNormalization.normalize_decimal(int_)
            return text_

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

    def normalize(self, text, language='en_US'):
        # if text in self.d_replace.keys():
        #     print('Case REPLACE', text)
        #     return self.d_replace[text]
        # elif text.isupper() and text.isalpha() and len(text) > 1 and self.has_vowel(text):
        #     print('Case UPPER_WORD', text)
        #     return text
        # elif text.isupper() and text.isalpha() and len(text) > 1 and not self.has_vowel(text):
        #     print('Case UPPER_NON_WORD', text)
        #     return " ".join(text.lower())
        # elif text[:-2].isupper() and text.isalpha() and text[-2:] == "'s" and not self.has_vowel(text):
        #     print('Case UPPER_S_0', text)
        #     return " ".join(text[:-2].lower()) + "'s"
        # elif text[:-1].isupper() and text.isalpha() and text[-1:] == "s" and len(text) > 2 and not self.has_vowel(text):  # SEALs
        #     print('Case UPPER_S_1', text)
        #     return " ".join(text[:-1].lower()) + "'s"
        # elif self.YEAR_CALENDAR.match(text):
        #     print('Case YEAR_CALENDAR', text)
        #     return TextNormalization.normalize_year_calendar(text)
        if self.YEAR.match(text) and 1001 <= int(text.strip()) <= 2099:
            print('Case YEAR', text)
            if text.isdigit():
                return TextNormalization.normalize_year(text)
            elif text.endswith(' '):  # TODO: handle xxxties
                return TextNormalization.normalize_year(text[:-1])
            else:
                return text
        elif self.DATE_YYYYMMDD.match(text) or self.DATE_YYYYMD.match(text):
            print('Case DATE_YYYYMMDD', text)
            if '-' in text:
                delimiter = '-'
            elif '/' in text:
                delimiter = '/'
            elif '.' in text:
                delimiter = '.'
            else:
                delimiter = None
            text_ = text.strip()

            if delimiter:
                year, month, day = text_.split(delimiter)
            else:
                year, month, day = text[:4], text[4:6], text[6:]
            try:
                normalized_year = TextNormalization.normalize_year(year, language)
                normalized_month = TextNormalization.normalize_month(month, language)
                normalized_day = TextNormalization.normalize_day(day, language)
                if language == 'en_US':
                    text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                else:
                    text_ = '{0}年{1}月{2}日'.format(normalized_year, normalized_month, normalized_day)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_MMDDYYYY.match(text) or self.DATE_MDYYYY.match(text) or self.DATE_MMDDYY.match(text):
            print('Case DATE_MMDDYYYY', text)
            if '-' in text:
                delimiter = '-'
            elif '/' in text:
                delimiter = '/'
            elif '.' in text:
                delimiter = '.'
            else:
                delimiter = None
            text_ = text.strip()

            if delimiter:
                month, day, year = text_.split(delimiter)
            else:
                month, day, year = text[:2], text[2:4], text[4:]
            try:
                normalized_year = TextNormalization.normalize_year(year, language)
                normalized_month = TextNormalization.normalize_month(month, language)
                normalized_day = TextNormalization.normalize_day(day, language)
                if language == 'en_US':
                    if normalized_day.startswith('tw') or normalized_day.startswith('seventeenth'):
                        text_ = '{0} {1} {2}'.format(normalized_month, normalized_day, normalized_year)
                    else:
                        text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                else:
                    text_ = '{0}年{1}月{2}日'.format(normalized_year, normalized_month, normalized_day)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_DDMMYYYY.match(text) or self.DATE_DMYYYY.match(text) or self.DATE_DDMMYY.match(text):
            print('Case DATE_DDMMYYYY', text)
            if '-' in text:
                delimiter = '-'
            elif '/' in text:
                delimiter = '/'
            elif '.' in text:
                delimiter = '.'
            else:
                delimiter = None
            text_ = text.strip()

            if delimiter:
                day, month, year = text_.split(delimiter)
            else:
                day, month, year = text[:2], text[2:4], text[4:]
            try:
                normalized_year = TextNormalization.normalize_year(year, language)
                normalized_month = TextNormalization.normalize_month(month, language)
                normalized_day = TextNormalization.normalize_day(day, language)
                if language == 'en_US':
                    text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                else:
                    text_ = '{0}年{1}月{2}日'.format(normalized_year, normalized_month, normalized_day)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_MMDD.match(text):
            print('Case DATE_MMDD', text)
            if '-' in text:
                delimiter = '-'
            elif '/' in text:
                delimiter = '/'
            else:
                delimiter = '.'
            text_ = text.strip()
            month, day = text_.split(delimiter)
            try:
                normalized_month = TextNormalization.normalize_month(month)
                normalized_day = TextNormalization.normalize_day(day)
                text_ = '{0} {1}'.format(normalized_month, normalized_day)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_DMY.match(text):
            print('Case DATE_EN_DMY', text)
            text_ = text.strip()
            text_ = text_.replace('.', '')
            words = text_.split(' ')

            weekday = None
            if len(words) == 3:
                day, month, year = words
            else:
                weekday, day, month, year = words
                weekday = weekday.lower().replace(',', '')

            try:
                normalized_year = TextNormalization.normalize_year(year)
                if len(month) <= 4:
                    normalized_month = TextNormalization.normalize_en_month(month.lower())
                else:
                    normalized_month = month.lower()
                normalized_day = TextNormalization.normalize_day(day)
                text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                if weekday:
                    if len(weekday) <= 3:
                        weekday = TextNormalization.normalize_weekday(weekday)
                    text_ = weekday + ' ' +  text_
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MDY.match(text):
            print('Case DATE_EN_MDY', text)
            text_ = text.replace(',', '')
            text_ = text_.replace('.', '')
            words = text_.split(' ')

            weekday = None
            if len(words) == 3:
                month, day, year = words
            else:
                weekday, month, day, year = words
                weekday = weekday.lower().replace(',', '')

            try:
                normalized_year = TextNormalization.normalize_year(year)
                if len(month) <= 4:
                    normalized_month = TextNormalization.normalize_en_month(month.lower())
                else:
                    normalized_month = month.lower()
                normalized_day = TextNormalization.normalize_day(day)
                text_ = '{0} {1} {2}'.format(normalized_month, normalized_day, normalized_year)
                if weekday:
                    if len(weekday) <= 3:
                        weekday = TextNormalization.normalize_weekday(weekday)
                    text_ = weekday + ' ' +  text_
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_DM.match(text):
            print('Case DATE_EN_DM', text)
            text_ = text.strip()
            text_ = text_.replace('.', '')
            words = text_.split(' ')

            weekday = None
            if len(words) == 2:
                day, month = words
            else:
                weekday, day, month = words
                weekday = weekday.lower().replace(',', '')

            try:
                if len(month) <= 4:
                    normalized_month = TextNormalization.normalize_en_month(month.lower())
                else:
                    normalized_month = month.lower()
                normalized_day = TextNormalization.normalize_day(day)
                text_ = 'the {0} of {1}'.format(normalized_day, normalized_month)
                if weekday:
                    if len(weekday) <= 3:
                        weekday = TextNormalization.normalize_weekday(weekday)
                    text_ = weekday + ' ' +  text_
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MD.match(text):
            print('Case DATE_EN_MD', text)
            text_ = text.strip()
            text_ = text_.replace('.', '')
            words = text_.split(' ')

            weekday = None
            if len(words) == 2:
                month, day = words
            else:
                weekday, month, day = words
                weekday = weekday.lower().replace(',', '')

            try:
                if len(month) <= 4:
                    normalized_month = TextNormalization.normalize_en_month(month.lower())
                else:
                    normalized_month = month.lower()
                normalized_day = TextNormalization.normalize_day(day)
                text_ = '{0} {1}'.format(normalized_month, normalized_day)
                if weekday:
                    if len(weekday) <= 3:
                        weekday = TextNormalization.normalize_weekday(weekday)
                    text_ = weekday + ' ' +  text_
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MY.match(text):
            print('Case DATE_EN_MY', text)
            text_ = text.strip()
            text_ = text_.replace('.', '')
            month, year = text_.split(' ')
            try:
                normalized_year = TextNormalization.normalize_year(year)
                if len(month) <= 4:
                    normalized_month = TextNormalization.normalize_en_month(month.lower())
                else:
                    normalized_month = month.lower()
                text_ = '{0} {1}'.format(normalized_month, normalized_year)
                return text_
            except KeyError as e:
                print(e)
                return text
            except Exception as e:
                print(e)
                raise
        elif self.TELEPHONE_COMMON.match(text):
            print('Case TELEPHONE_COMMON', text)
            return TextNormalization.normalize_telephone_common(text)
        elif self.ISBN.match(text):
            print('Case ISBN', text)
            return TextNormalization.normalize_telephone(text, language)
        elif self.LEADING_ZERO.match(text):
            print('Case LEADING_ZERO', text)
            text_ = TextNormalization.normalize_leading_zero(text)
            return text_
        elif self.DECIMAL_COMMA_OPTIONAL.match(text):
            print('Case DECIMAL_COMMA_OPTIONAL', text)
            if text.isdigit():
                if int(text) <= 10000:
                    text_ = TextNormalization.normalize_decimal(text)
                else:
                    text_ = text
            else:
                text_ = TextNormalization.normalize_decimal(text)
            return text_
        elif self.PERCENT.match(text):
            print('Case PERCENT', text)
            if text.startswith('-'):
                is_minus = True
            else:
                is_minus = False

            text_ = text.replace('-', ' ')

            if text_.endswith('%'):
                text_ = text_[:-1]
            else:
                text_ = text_.split(' ')[0]

            text_ = TextNormalization.normalize_decimal(text_)
            text_ += ' percent'
            if is_minus:
                text_ = 'minus ' + text_
            return text_
        elif self.TELEPHONE.match(text):
            print('Case TELEPHONE', text)
            return TextNormalization.normalize_telephone(text)
        elif self.IPv4.match(text):
            print('Case IPv4', text)
            return TextNormalization.normalize_ipv4(text, language)
        elif self.MEASURE.match(text):
            print('Case MEASURE', text)
            return TextNormalization.normalize_measure(text)
        elif self.ROMAN.match(text):
            print('Case ROMAN', text)
            return TextNormalization.normalize_roman(text)
        elif self.PROPER_CASE_CONCAT.match(text):
            print('Case PROPER_CASE_CONCAT', text)
            return text
        elif text.endswith('.') and len(text) > 1:
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
        '2221.8 lb',
        '111.0 kg',
        '11.8 MB',
        '0.7 kg/m3',
        '-355',
        '325 000',
        '-',
        '23.01.2015',
        '11/2/2010',
        '28 FEBRUARY 2008',
        'Saturday, 28 FEBRUARY 2008',
        'Wednesday December 5, 2007',
        'Sunday May 6th, 2009',
        'Saturday, 8 February 1919',
        '22nd March 2007',
        '22 May',
        '27 January ',
        'October 28',
        'Mar 08, 1981',
        '22/03/2010',
        '11/4/2014',
        '14 January ',
        '5-18 JANUARY 2016',
        'June 23 rd 2014',
        '11-20-2009',
        '2-9-2011',
        '01-01-90',
        '20081981',
        '3/17/07',
        '1.40',
        '1.0',
        '.38',
        '2011',
        '2012',
        '2160',
        '05',
        '001',
        '00',
        '0',
        '0800',
        '013',
        'HERBS',
        '1km',
        '１',
        '01 - 6',
        'CXIII',
        '0.95 g/cm3',
        '(1966)3',
        '08.08',
        '978-0-300-11465-2',
        '9780521653947',
        '05 250',
        'o',
        '0',
        '33130',
        '91430',
        '38115',
        '27""',
        '.0',
        '9-1-1',
        '911',
        '999',
        '26787',
        '57950',
        '9268',
        '60',
        '2300-0200',
        'I',
        ''
    ]

    text_normalization = TextNormalization()

    for test_case in test_cases:
        normalized_text = text_normalization.normalize(test_case)
        print(normalized_text)
        print()

    # text_normalization.normalize_all()
