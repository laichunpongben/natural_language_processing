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
# ₉
# Rs 150 Cr
# USD = united states dollars
# Proper case OCTOBER
# zl polish zloty
# 10 a.m. ET
# OCLC => o c l c
# Friday, 7/17/2015
# tampabays10.com
# # => hash
# "61085_6","975 KiB","nine hundred seventy five kibibytes","975 KiB","Private"
# "62797_10","805 KiB","eight hundred five kibibytes","805 KiB","Private"
# "58690_4","9 May 328","nine May three hundred twenty eight","the ninth of may three twenty eight","Private"
# "69389_6","22:00","twenty two","twenty two hundred","Private"
# "59755_5","7-13 2014","7-13 two thousand fourteen","seven sil one three sil two o one four","Private"
# "61527_1","A330","a three three o","a three thirty","Private"
# "50598_7","SR","senior","s r","Private"
# "45579_11","3.5 million dollar","three point five million dollar","three point five million dollars","Private"
# "42120_5","$12.11","twelve point one one dollars","twelve dollars and eleven cents","Private"
# "38570_11","$1,102,117.19","one million one hundred two thousand one hundred seventeen point one nine dollars","one million one hundred two thousand one hundred seventeen dollars and nineteen cents","Private"
# "36275_1","110 million m³","one hundred ten million cubic meters","110 million m³","Private"
# "30522_1","60 US ","sixty US","sixty","Private"
# "18139_6","£77,039.89","seventy seven thousand thirty nine point eight nine pounds","seventy seven thousand thirty nine pounds and eighty nine pence","Private"
# nitrogen monoxide

class TextNormalization(object):
    YEAR = re.compile(r"^[1-9][0-9]{3} ?$")
    LEADING_ZERO = re.compile(r"^0(?=[0-9])(?:[0-9]*|[0-9]{1,3}(?:(?: |,)[0-9]{3})*)$")
    DECIMAL_COMMA_OPTIONAL = re.compile(r"^\-?(?=(?:\.|[0-9]))(?:[0-9]*|[0-9]{1,3}(?:(?: |,)[0-9]{3})*)(?:\.[0-9]+)?\,? ?$")
    ISBN = re.compile(r"^[0-9][\-0-9]{11,}[0-9]$")
    TELEPHONE = re.compile(r"(?!^\-+$)(^[0-9 \-\(\)].*[\-\(\)]|^[0-9 \-\(\)]{2,}$|^[0-9]+[ \-\(\)].*?[ \-\(\)][0-9]+$)")

    TELEPHONE_COMMON = re.compile(r"^(911|999|9-1-1|9-9-9)$")
    IPv4 = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/?[0-9]{0,2}$")
    DECIMAL = re.compile(r"^[0-9]*\.?[0-9]+$")
    CURRENCY = re.compile(r"^\-?(\$|£|€|¥|USD|US\$|SEK|PKR|XCD|NOK|EGP|DKK|ATS|INR|GMD|GBP|CHF|AED|SAR|THB|UAH|PHP|PLN|ILS|ZAR|HUF|RSD|CZK|VAL|CRC|BEF|CYP|SCR|ARS|SHP|BDT|LTL|PGK|SBD|EUR|BMD|BWP|IDR|CVE|MDL|NAD|BTN|NT\$|CA\$|HK\$|AU\$|NZ\$|A\$|S\$|R\$|RS\.|RS|Rs\.|Rs) ?\-?(?=(?:\.|[0-9]))(?:[0-9]*|[0-9]{1,3}(?:(?: |,)[0-9]{3})*)(?:\.[0-9]+)?")
    PERCENT = re.compile(r"^\-?(?=(?:\.|[0-9]))[0-9]+(?:\.[0-9]+)? ?(?:%| percent)$")
    DATE_YYYYMMDD = re.compile(r"(?i)^(the )?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\.? ?[1-2][0-9]{3}(?:\-|\/|\.)(0[1-9]|1[012])(?:\-|\/|\.)?(0[1-9]|[12][0-9]|3[01])$")
    DATE_MMDDYYYY = re.compile(r"(?i)^(the )?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\.? ?(0[1-9]|1[012])(?:\-|\/|\.)?(0[1-9]|[12][0-9]|3[01])(?:\-|\/|\.)?[1-2][0-9]{3}$")
    DATE_DDMMYYYY = re.compile(r"^(0[1-9]|[12][0-9]|3[01])(?:\-|\/|\.)?(0[1-9]|1[012])(?:\-|\/|\.)?[1-2][0-9]{3}$")
    DATE_YYYYMD = re.compile(r"^[1-2][0-9]{3}(?:\-|\/|\.)([1-9]|1[012])(?:\-|\/|\.)([1-9]|[12][0-9]|3[01])$")
    DATE_MDYYYY = re.compile(r"^([1-9]|1[012])(?:\-|\/|\.)([1-9]|[12][0-9]|3[01])(?:\-|\/|\.)[1-2][0-9]{3}$")
    DATE_DMYYYY = re.compile(r"^([1-9]|[12][0-9]|3[01])(?:\-|\/|\.)([1-9]|1[012])(?:\-|\/|\.)[1-2][0-9]{3}$")
    DATE_MMDDYY = re.compile(r"^[0-1]?[0-9](?:\-|\/|\.)[0-3]?[0-9](?:\-|\/|\.)[0-9]{2}$")
    DATE_DDMMYY = re.compile(r"^[0-3]?[0-9](?:\-|\/|\.)[0-1]?[0-9](?:\-|\/|\.)[0-9]{2}$")
    DATE_MMDD = re.compile(r"^0[0-9](?:\-|\/|\.)[0-3][0-9]$")
    DATE_EN_DMY = re.compile(r"(?i)^(the )?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\.? ?[0-9]{1,2}(?:st|nd|rd|th)?[ \-](January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)[\.\,]?[ \-][0-9]{2,4} ?(?:BCE|CE|BC|AD|A\.D\.|B\.C\.|B\.C\.E\.|C\.E\.)?\.?\,?$")
    DATE_EN_DM = re.compile(r"(?i)^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\.? ?[0-9]{1,2}(?:st|nd|rd|th)? (January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)[\.\,]? ?$")
    DATE_EN_MD = re.compile(r"(?i)^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\.? ?(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)[\.\,]? [0-9]{1,2}(?:st|nd|rd|th)? ?$")
    DATE_EN_MY = re.compile(r"(?i)^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\.? ?(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)[\.\,]? [0-9]{4}$")
    DATE_EN_MDY = re.compile(r"(?i)^(the )?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\.? ?(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)[\.\,]?[ \-][0-9]{1,2}(?:st|nd|rd|th)?\,?[ \-][0-9]{2,4} ?(?:BCE|CE|BC|AD|A\.D\.|B\.C\.|B\.C\.E\.|C\.E\.)?\.?\,?$")
    YEAR_CALENDAR = re.compile(r"^[0-9]+ (?:BCE|CE|BC|AD|A\.D\.|B\.C\.|B\.C\.E\.|C\.E\.)\.?\,?$")
    TIME = re.compile(r"^[0-9]{4}-[0-9]{4}$")
    PROPER_CASE_CONCAT = re.compile(r"^(?:[A-Z][^A-Z\s\.]+){2,}$")
    CAPITAL_LETTER = re.compile(r"^[A-Z]{2,}$")
    MEASURE = re.compile(r"(^\-?((?=(?:\.|[0-9]))(?:[0-9]*|[0-9]{1,3}(?:(?: |,)[0-9]{3})*)(?:\.[0-9]+)?|.*\/|.*\s)(?:(milli)?litres|(milli|centi|kilo)?metres|m2|m²|m3|Km|km|km2|km²|km3|km³|m³|km²|mm²|mi²|mg\/Kg|mSv\/yr|km\/h|km\/s|m\/s|ft\/s|kg\/m3|g\/cm3|mg\/kg|mg\/L|km\/hr|μg\/ml|kcal\/mol|kJ\/mol|kcal\/g|kJ\/g|kJ\/m³|m³\/s|kg\/ha|kWh\/m3|kWh\/m|kg\/m|g\/km|mol|mAh|KiB|GPa|kPa|kJ|kg|Kg|kV|kb|mV|kW|lbs|lb|sq mi|mi2|mi|MB|m|mg|mL|ml|ha|hp|cc|cm|nm|mm|ms|ft|sq ft|kHz|Hz|in|Gy|GB|AU|MW|bbl|mph|rpm|hrs|MHz|GHz|MPa|kJ|KB|kN|yd|oz|USD|EUR|U\.S\.|\"\") ?$|^\-?(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})*)(?:\.[0-9]+)?(?:\/| )?[gmV]$)")
    ROMAN = re.compile(r"(^(?=[MDCLXVI]{3,})M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})$|^(?=[mdclxvi]{3,})m{0,4}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})$)")
    CLOCK = re.compile(r"([0-9]{1,2}[\:\.]?[0-9]{0,2} ?(a\.m\.|p\.m\.|A\.M\.|P\.M\.|am|pm|AM|PM) ?(GMT|IST|ET|EST|EDT|PDT|PST|CST|AEST|UTC)?$|^[0-9]{1,2}[\:\.] ?[0-9]{2} ?(GMT|IST|ET|EST|EDT|PDT|PST|CST|AEST|UTC)?$)")
    SECONDS = re.compile(r"^[0-9]+:[0-9]{2}:[0-9]{2}")
    MILLISECONDS = re.compile(r"^[0-9]+:[0-9]{2}\.[0-9]{2}")
    ELECTRONIC = None
    FRACTION = re.compile(r"(^[0-9]+ ?)?([½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅐⅛⅜⅝⅞⅑⅒] ?$|( 1\/2| 1\/3| 2\/3| 1\/4| 3\/4| 1\/5| 2\/5| 3\/5| 4\/5| 1\/6| 5\/6| 1\/7| 1\/8| 3\/8| 5\/8| 7\/8| 1\/9| 1\/10) ?$|(?<!\/)\-?[0-9]+ ?\/ ?[0-9]+(?!\/))\b")
    ALPHADIGIT = re.compile(r"(^[A-Z]+[ \-]?[0-9]+ ?$|^U\.S\. ?[0-9]+ ?$)")
    KATAKANA = None
    KANJI = None  # 69155, 67022
    HASHTAG = re.compile(r"^#.+$")
    HYPHEN = re.compile(r"^[A-Za-z]+\-$")
    CAPITAL_DOT = re.compile(r"^([A-Z]\. ?)+$")
    REPLACE = re.compile(r"^(49ers|76ers)$")
    URL = re.compile(r"(.*(\.[0-9]\-|\.co|\.doi|\.ini|\.org|\.edu|\.gov|\.net|\.nrg|\.rez|\.but|\.cit|\.exe|\.xls|\.pdf|\.jpg|\.info|\.guns|\.mouse|\.view|\.asus|\.tv|\.mil|\.pl|\.ie|\.ir|\.fm|\.hu|\.hr|\.fr|\.ee|\.uk|\.de|\.ru|\.us|\.es|\.ca|\.ch|\.cx|\.mx|\.be|\.nz|\.va|\.fi|\.ar|\.au|\.at|\.cn|\.kr|\.nl|\.bg|\.it|\.ro|\.cz|\.do|\.eu|\.is|\.no|\.ph|\.gr|\.se|\.jp|\.xyz|www\.|\.htm|http\:|https\:).*|^\.[0-9]\.[0-9]*)")

    digit_transcripter = inflect.engine()
    capitals_path = '/home/ben/github/natural_language_processing/text_normalization_en/capitals'
    with open(capitals_path, 'r') as f:
        capitals = [x[:-1] for x in f.readlines()]

    def __init__(self):
        self.test_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_test_2.csv'
        self.diff_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_train_truncated.csv'
        self.result_path = '/home/ben/github/natural_language_processing/text_normalization_en/result_2.csv'
        self.compare_path = '/home/ben/github/natural_language_processing/text_normalization_en/compare_2.csv'
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
        d['-'] = 'to'
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
    def has_digit(text):
        return any(char.isdigit() for char in text)

    @staticmethod
    def normalize_year(text, language='en_US', previous=None, following=None):
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
                    # if previous in ['/'] or following in ['/']:
                    if False:
                        text_ = TextNormalization.digit_transcripter.number_to_words(text)
                        if text == '00':
                            text_ = 'o o'
                        elif text.startswith('0'):
                            text_ = 'o ' + text_

                    else:
                        prefix = TextNormalization.digit_transcripter.number_to_words(text[:-2])
                        suffix = TextNormalization.digit_transcripter.number_to_words(text[-2:])
                        if text[-2:].startswith('00'):
                            suffix = 'hundred'
                        elif text[-2:].startswith('0'):
                            suffix = 'o ' + suffix
                        text_ = prefix + ' ' + suffix
                else:
                    text_ = TextNormalization.digit_transcripter.number_to_words(text)
                    if text == '00':
                        text_ = 'o o'
                    elif text.startswith('0'):
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
    def normalize_year_calendar(text, previous=None, following=None):
        text_ = text.replace('.', '')
        text_ = text_.replace(',', '')
        year, suffix = text_.split(' ')
        normalized_year = TextNormalization.normalize_year(year, previous=previous, following=following)
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
        text_ = text.lower().strip()
        if text_.endswith('-'):
            text_ = text_[:-1]
        text_ = text_.replace('(', '--')
        text_ = text_.replace(')', '--')
        text_ = text_.replace(' ', '--')
        text_ = text_.replace('-', '--')

        if language == 'en_US':
            d = OrderedDict([
                ('-1200-', ' sil twelve hundred sil '),
                ('-1100-', ' sil eleven hundred sil '),
                ('-1000-', ' sil one thousand sil '),
                ('-0900-', ' sil o nine hundred sil '),
                ('-0800-', ' sil o eight hundred sil '),
                ('-0700-', ' sil o seven hundred sil '),
                ('-0600-', ' sil o six hundred sil '),
                ('-0500-', ' sil o five hundred sil '),
                ('-0400-', ' sil o four hundred sil '),
                ('-0300-', ' sil o three hundred sil '),
                ('-0200-', ' sil o two hundred sil '),
                ('-0100-', ' sil o one hundred sil '),
                ('-900-', ' sil nine hundred sil '),
                ('-800-', ' sil eight hundred sil '),
                ('-700-', ' sil seven hundred sil '),
                ('-600-', ' sil six hundred sil '),
                ('-500-', ' sil five hundred sil '),
                ('-400-', ' sil four hundred sil '),
                ('-300-', ' sil three hundred sil '),
                ('-200-', ' sil two hundred sil '),
                ('-100-', ' sil one hundred sil '),
                ('2300', ' two three o o '),
                ('2200', ' two two o o '),
                ('2100', ' two one o o '),
                ('2000', ' two thousand '),
                ('1900', ' nineteen hundred '),
                ('1800', ' eighteen hundred '),
                ('1700', ' seventeen hundred '),
                ('1600', ' sixteen hundred '),
                ('1500', ' fifteen hundred '),
                ('1400', ' fourteen hundred '),
                ('1300', ' thirteen hundred '),
                ('1200', ' twelve hundred '),
                ('1100', ' eleven hundred '),
                ('1000', ' one thousand '),
                ('0900', ' o nine hundred '),
                ('0800', ' o eight hundred '),
                ('0700', ' o seven hundred '),
                ('0600', ' o six hundred '),
                ('0500', ' o five hundred '),
                ('0400', ' o four hundred '),
                ('0300', ' o three hundred '),
                ('0200', ' o two hundred '),
                ('0100', ' o one hundred '),
                ('900-', ' nine hundred sil '),
                ('800-', ' eight hundred sil '),
                ('700-', ' seven hundred sil '),
                ('600-', ' six hundred sil '),
                ('500-', ' five hundred sil '),
                ('400-', ' four hundred sil '),
                ('300-', ' three hundred sil '),
                ('200-', ' two hundred sil '),
                ('100-', ' one hundred sil '),
                ('1', ' one '),
                ('2', ' two '),
                ('3', ' three '),
                ('4', ' four '),
                ('5', ' five '),
                ('6', ' six '),
                ('7', ' seven '),
                ('8', ' eight '),
                ('9', ' nine '),
                ('0', ' o '),
                ('.', ' dot '),
                ('-', ' sil '),
                ('isbn', ' i s b n '),
                ('oclc', ' o c l c '),
                ('bc', ' b c '),
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

        text_ = re.sub(r" +", r" ", text_).strip()
        text_ = re.sub(r"(sil )+sil", r"sil", text_)
        if text_.startswith('sil '):
            text_ = text_[4:]

        return text_

    @staticmethod
    def normalize_alphadigit(text):
        text = text.lower().strip()
        for i, c in enumerate(text):
            if c.isdigit():
                break
        prefix, suffix = text[:i], text[i:]

        prefix = prefix.strip()
        prefix = prefix.replace('-', '')
        prefix = prefix.replace('.', '')
        prefix = ' '.join(list(prefix))

        print(prefix)
        if prefix == 'u s':
            if int(suffix) <= 2099:
                suffix = TextNormalization.normalize_year(suffix)
            else:
                suffix = TextNormalization.normalize_decimal(suffix)
        else:
            if len(suffix) <= 2:
                suffix = TextNormalization.normalize_decimal(suffix)
            else:
                d = OrderedDict([
                    ('1', ' one '),
                    ('2', ' two '),
                    ('3', ' three '),
                    ('4', ' four '),
                    ('5', ' five '),
                    ('6', ' six '),
                    ('7', ' seven '),
                    ('8', ' eight '),
                    ('9', ' nine '),
                    ('0', ' o '),
                ])
                for k, v in d.items():
                    if k in suffix:
                        suffix = suffix.replace(k, v)

        text = prefix + ' ' + suffix
        return text

    @staticmethod
    def normalize_leading_zero(text, previous=None):
        if previous:
            if len(text) == text.count('0') and previous.isdigit():
                return 'zero'

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
            ('USD', ['united states dollars', 'united states dollar']),
            ('EUR', ['euros', 'euro']),
            ('U.S.', ['', '']),
            ('kcal/mol', ['kilo calories per mole', 'kilo calorie per mole']),
            ('kJ/mol', ['kilo joules per mole', 'kilo joule per mole']),
            ('mSv/yr', ['millisieverts per year', 'millisievert per year']),
            ('km/hr', ['kilometers per hour', 'kilometer per hour']),
            ('km/h', ['kilometers per hour', 'kilometer per hour']),
            ('km/s', ['kilometers per second', 'kilometer per second']),
            ('m/s', ['meters per second', 'meter per second']),
            ('kWh/m3', ['kilo watt hours per cubic meter', 'kilo watt hour per cubic meter']),
            ('kWh/m', ['kilo watt hours per meter', 'kilo watt hour per meter']),
            ('kcal/g', ['kilo calories per gram', 'kilo calorie per gram']),
            ('kJ/g', ['kilo joules per gram', 'kilo joules per gram']),
            ('kJ/m³', ['kilo joules per cubic meter', 'kilo joules per cubic meter']),
            ('kg/m3', ['kilograms per cubic meter', 'kilogram per cubic meter']),
            ('kg/ha', ['kilograms per hectare', 'kilogram per hectare']),
            ('g/cm3', ['grams per c c', 'gram per c c']),
            ('μg/ml', ['micrograms per milliliter', 'microgram per milliliter']),
            ('mg/Kg', ['milligrams per kilogram', 'milligram per kilogram']),
            ('mg/kg', ['milligrams per kilogram', 'milligram per kilogram']),
            ('mg/L', ['milligrams per liter', 'milligram per liter']),
            ('m³/s', ['cubic meters per second', 'cubic meter per second']),
            ('kg/m', ['kilograms per meter', 'kilogram per meter']),
            ('g/km', ['grams per kilometer', 'gram per kilometer']),
            ('mAh', ['milli amp hours', 'milli amp hour']),
            ('mph', ['miles per hour', 'mile per hour']),
            ('rpm', ['revolutions per minute', 'revolution per minute']),
            ('bbl', ['barrels', 'barrel']),
            ('mol', ['moles', 'mole']),
            ('hrs', ['hours', 'hour']),
            ('kHz', ['kilohertz', 'kilohertz']),
            ('MHz', ['megahertz', 'megahertz']),
            ('GHz', ['gigahertz', 'gigahertz']),
            ('MPa', ['megapascals', 'megapascal']),
            ('KiB', ['kibibytes', 'kibibyte']),
            ('GPa', ['giga pascals', 'giga pascal']),
            ('kPa', ['kilopascals', 'kilopascal']),
            ('km2', ['square kilometers', 'square kilometer']),
            ('km3', ['cubic kilometers', 'cubic kilometer']),
            ('km³', ['cubic kilometers', 'cubic kilometer']),
            ('km²', ['square kilometers', 'square kilometer']),
            ('mm²', ['square millimeters', 'square millimeter']),
            ('mi²', ['square miles', 'square mile']),
            ('Km', ['kilometers', 'kilometer']),
            ('km', ['kilometers', 'kilometer']),
            ('Kg', ['kilograms', 'kilogram']),
            ('kg', ['kilograms', 'kilogram']),
            ('kJ', ['kilo joules', 'kilo joule']),
            ('kV', ['kilo volts', 'kilo volt']),
            ('mV', ['milli volts', 'milli volt']),
            ('ms', ['milliseconds', 'millisecond']),
            ('kW', ['kilowatts', 'kilowatt']),
            ('KB', ['kilobytes', 'kilobyte']),
            ('lbs', ['pounds', 'pound']),
            ('lb', ['pounds', 'pound']),
            ('oz', ['ounces', 'ounce']),
            ('m2', ['square meters', 'square meter']),
            ('m²', ['square meters', 'square meter']),
            ('m3', ['cubic meters', 'cubic meter']),
            ('m³', ['cubic meters', 'cubic meter']),
            ('mL', ['milliliters', 'milliliter']),
            ('ml', ['milliliters', 'milliliter']),
            ('sq mi', ['square miles', 'square mile']),
            ('mi2', ['square miles', 'square mile']),
            ('mi', ['miles', 'mile']),
            ('mg', ['milligrams', 'milligram']),
            ('sq ft', ['square feet', 'square foot']),
            ('ft/s', ['feet per second', 'foot per second']),
            ('ft', ['feet', 'foot']),
            ('m2', ['square meters', 'square meter']),
            ('cm', ['centimeters', 'centimeter']),
            ('nm', ['nanometers', 'nanometer']),
            ('mm', ['millimeters', 'millimeter']),
            ('hp', ['horsepower', 'horsepower']),
            ('cc', ['c c', 'c c']),
            ('ha', ['hectares', 'hectare']),
            ('Hz', ['hertz', 'hertz']),
            ('kN', ['kilonewtons', 'kilonewton']),
            ('yd', ['yards', 'yard']),
            ('Gy', ['grays', 'gray']),
            ('GB', ['gigabytes', 'gigabyte']),
            ('AU', ['astronomical units', 'astronomical unit']),
            ('MW', ['megawatts', 'megawatt']),
            ('MB', ['megabytes', 'megabyte']),
            ('kb', ['kilobits', 'kilobit']),
            ('in', ['inches', 'inch']),
            ('a.m.', ['a m', 'a m']),
            ('p.m.', ['p m', 'p m']),
            ('am', ['a m', 'a m']),
            ('pm', ['p m', 'p m']),
            ('""', ['inches', 'inch']),
            ('m', ['meters', 'meter']),
            ('g', ['grams', 'gram']),
            ('V', ['volts', 'volt']),
        ])
        text_ = text
        normalized_measure = None
        for k, v in d.items():
            if text_.endswith(k) or text_.endswith(k + ' '):
                measure, normalized_measure = k, v
                text_ = text_.replace(k, '')
                break

        text_ = text_.replace('metre', 'meter')
        text_ = text_.replace('litre', 'liter')
        text_ = re.sub(r'([0-9])\s+([0-9])', r'\1\2', text_)

        if text_.endswith('/'):
            is_per = True
            text_ = text_.replace('/', '')
        else:
            is_per = False

        words = [x for x in text_.split(' ') if x]
        for index, word in enumerate(words):
            try:
                f = float(word)
                words[index] = TextNormalization.normalize_decimal(word)
            except ValueError:
                pass

        normalized_text = ' '.join(words)

        if normalized_measure:
            if normalized_text in ['one', '', 'per']:
                normalized_measure = normalized_measure[1]
            else:
                normalized_measure = normalized_measure[0]

            if is_per:
                normalized_text += ' per'

            normalized_text += ' '
            normalized_text += normalized_measure

        normalized_text = normalized_text.replace('/', 'per')

        return normalized_text

    @staticmethod
    def normalize_clock(text):
        has_suffix = False
        text = text.replace('a.m.', ' a m')
        text = text.replace('p.m.', ' p m')
        text = text.replace('A.M.', ' a m')
        text = text.replace('P.M.', ' p m')
        text = text.replace('am', ' a m')
        text = text.replace('pm', ' p m')
        text = text.replace('AM', ' a m')
        text = text.replace('PM', ' p m')
        text = text.replace('.', ':')

        for suffix in ['AEST', 'IST', 'UTC', 'GMT', 'EST', 'EDT', 'EST', 'PDT', 'PST', 'CST', 'ET']:
            if suffix in text:
                has_suffix = True
                text = text.replace(suffix, '')
                break

        if (text.endswith(':00') or text.endswith(':00 ')) and text.count(':') < 2:
            text = text.replace(':00', '')
            if int(text.strip()) <= 12:
                text += " o'clock"
            else:
                text += ' hundred'
        text = text.replace(':00', ' ')
        text = text.replace(':', ' ')
        text = text.lstrip('0')

        if has_suffix:
            text += ' '
            text += ' '.join(list(suffix.lower()))
        return text

    @staticmethod
    def normalize_seconds(text):
        suffix = None
        if ' ' in text:
            text, suffix = text.split(' ')
            suffix = ' '.join(list(suffix.lower()))

        hour, minute, second = text.split(':')
        hour = TextNormalization.normalize_decimal(hour)
        minute = TextNormalization.normalize_decimal(minute)
        second = TextNormalization.normalize_decimal(second)

        text = '{0} hours {1} minutes and {2} seconds'.format(hour, minute, second)
        if suffix:
            text += ' ' + suffix

        return text

    @staticmethod
    def normalize_milliseconds(text):
        suffix = None
        if ' ' in text:
            text, suffix = text.split(' ')
            suffix = ' '.join(list(suffix.lower()))

        minute_second, millisecond = text.split('.')
        minute, second = minute_second.split(':')
        minute = TextNormalization.normalize_decimal(minute)
        second = TextNormalization.normalize_decimal(second)
        millisecond = TextNormalization.normalize_decimal(millisecond)

        text = '{0} minutes {1} seconds and {2} milliseconds'.format(minute, second, millisecond)
        if suffix:
            text += ' ' + suffix

        return text

    @staticmethod
    def normalize_fraction(text):
        text = text.replace(' / ', '/')
        text = text.replace('/ ', '/')
        text = text.replace(' /', '/')

        whole, fraction = '', ''
        numerator, denominator = '', ''

        if ' ' in text:
            whole, fraction = text.split(' ')
        else:
            fraction = text

        if '/' in fraction:
            numerator, denominator = fraction.split('/')
            numerator = TextNormalization.normalize_decimal(numerator)
            denominator = TextNormalization.normalize_decimal(denominator)

            if denominator == 'two':
                denominator = 'halves'
                if numerator in ['one', 'minus one']:
                    denominator = 'half'
            elif denominator == 'four':
                denominator = 'quarters'
            elif denominator.endswith('y'):
                denominator = denominator[:-1] + 'ieths'
            elif denominator.endswith('ve'):
                denominator = denominator[:-2] + 'fths'
            elif denominator.endswith('one'):
                denominator = denominator[:-3] + 'firsts'
            elif denominator.endswith('two'):
                denominator = denominator[:-3] + 'seconds'
            elif denominator.endswith('three'):
                denominator = denominator[:-5] + 'thirds'
            elif denominator.endswith('nine'):
                denominator = denominator[:-4] + 'ninths'
            elif denominator.endswith('t'):
                denominator += 'hs'
            else:
                denominator += 'ths'
            # elif denominator.endswith('')

            if numerator == 'one':
                numerator = 'a'
                if denominator.endswith('s'):
                    denominator = denominator[:-1]

            fraction = numerator + ' ' + denominator
            if fraction == 'a first':
                fraction = 'one over one'

        else:
            d = {
                '½': ' and a half',
                '⅓': ' and a third',
                '⅔': ' and two thirds',
                '¼': ' and a quarter',
                '¾': ' and three quarters',
                '⅕': ' and a fifth',
                '⅖': ' and two fifths',
                '⅗': ' and three fifths',
                '⅘': ' and four fifths',
                '⅙': ' and a sixth',
                '⅚': ' and five sixths',
                '⅐': ' and a seventh',
                '⅛': ' and an eighth',
                '⅜': ' and three eighths',
                '⅝': ' and five eighths',
                '⅞': ' and seven eighths',
                '⅑': ' and a nineth',
                '⅒': ' and a tenth',
                # '1/2': ' and a half',
                # '1/3': ' and a third',
                # '2/3': ' and two thirds',
                # '1/4': ' and a quarter',
                # '3/4': ' and three quarters',
                # '1/5': ' and a fifth',
                # '2/5': ' and two fifths',
                # '3/5': ' and three fifths',
                # '4/5': ' and four fifths',
                # '1/6': ' and a sixth',
                # '5/6': ' and five sixths',
                # '1/7': ' and a seventh',
                # '1/8': ' and an eighth',
                # '3/8': ' and three eighths',
                # '5/8': ' and five eighths',
                # '7/8': ' and seven eighths',
                # '1/9': ' and a nineth',
                # '1/10': ' and a tenth',
            }
            for k, v in d.items():
                if k in fraction:
                    fraction = fraction.replace(k, d[k])

        if whole:
            text = whole + ' and ' + fraction
        else:
            text = fraction
        text = text.strip()

        if text.startswith('and a '):
            text = text.replace('and a', 'one')
        elif text.startswith('and '):
            text = text.replace('and ', '')

        if text.startswith('a '):
            text = 'one' + text[1:]

        text = re.sub(r" +", r" ", text)
        text = text.replace('and and', 'and')

        return text

    @staticmethod
    def normalize_currency(text):
        d = OrderedDict([
            ('USD', 'united states dollars'),
            ('US$', 'dollars'),
            ('SEK', 'swedish kronor'),
            ('PKR', 'pakistani rupees'),
            ('XCD', 'east caribbean dollars'),
            ('NOK', 'norwegian kroner'),
            ('EGP', 'egyptian pounds'),
            ('DKK', 'danish kroner'),  # ore
            ('ATS', 'austrian schillings'),
            ('INR', 'indian rupees'),
            ('GMD', 'gambian dalasis'),
            ('GBP', 'pounds'),
            ('CHF', 'swiss francs'),
            ('AED', 'united arab emirates dirhams'),
            ('SAR', 'saudi riyals'),
            ('THB', 'thai bahts'),
            ('UAH', 'ukrainian hryvnias'),
            ('PHP', 'philippine pesos'),
            ('PLN', 'polish zlotys'),
            ('ILS', 'israeli new sheqels'),
            ('ZAR', 'south african rands'),
            ('HUF', 'hungarian forints'),
            ('RSD', 'serbian dinars'),
            ('CZK', 'czech korunas'),
            ('VAL', 'vatican liras'),
            ('CRC', 'costa rican colons'),
            ('BEF', 'belgian francs'),
            ('CYP', 'cypriot pounds'),
            ('SCR', 'seychelles rupees'),
            ('ARS', 'argentine pesos'),
            ('SHP', 'saint helena pounds'),
            ('BDT', 'bangladeshi takas'),
            ('LTL', 'lithuanian litass'),
            ('PGK', 'papua new guinean kina'),
            ('SBD', 'solomon islands dollars'),
            ('EUR', 'euros'),
            ('BMD', 'bermudian dollars'),
            ('BWP', 'botswana pulas'),
            ('IDR', 'indonesian rupiahs'),
            ('CVE', 'cape verde escudos'),
            ('MDL', 'moldovan leus'),
            ('NAD', 'namibian dollars'),
            ('BTN', 'bhutanese ngultrum'),
            ('NT$', 'dollars'),
            ('CA$', 'dollars'),
            ('HK$', 'dollars'),
            ('AU$', 'dollars'),
            ('NZ$', 'dollars'),
            ('A$', 'dollars'),
            ('S$', 'dollars'),
            ('R$', 'reals'),
            ('DM', 'german marks'),
            ('TK', 'takas'),
            ('RS.', 'rupees'),
            ('RS', 'rupees'),
            ('Rs.', 'rupees'),
            ('Rs', 'rupees'),
            ('$', 'dollars'),  # dollars
            ('£', 'pounds'),  # pence
            ('€', 'euros'),
            ('¥', 'yen')
        ])

        for k, v in d.items():
            if k in text:
                text = text.replace(k, '')
                text = re.sub(r'([0-9])\s+([0-9])', r'\1\2', text)
                if len(text) > 8:
                    if text.endswith('thousand') and text[-9].isdigit():
                        text = text[:-8] + ' thousand'
                    elif text.endswith('trillion') and text[-9].isdigit():
                        text = text[:-8] + ' trillion'

                if len(text) > 7:
                    if text.endswith('billion') and text[-8].isdigit():
                        text = text[:-7] + ' billion'
                    elif text.endswith('million') and text[-8].isdigit():
                        text = text[:-7] + ' million'

                if len(text) > 2:
                    if text.endswith('bn') and text[-3].isdigit():
                        text = text[:-2] + ' billion'

                if len(text) > 1:
                    if text[-1] in ['M', 'm'] and text[-2].isdigit():
                        text = text[:-1] + ' million'
                    elif text[-1] in ['K', 'k'] and text[-2].isdigit():
                        text = text[:-1] + ' thousand'
                    elif text[-1] in ['T', 't'] and text[-2].isdigit():
                        text = text[:-1] + ' trillion'
                    elif text[-1] in ['B', 'b'] and text[-2].isdigit():
                        text = text[:-1] + ' billion'
                text = text + ' ' + v
                break

        words = text.split(' ')
        for index, word in enumerate(words):
            try:
                if word == 'cr':
                    words[index] = 'crore'

                f = float(word)
                words[index] = TextNormalization.normalize_decimal(word)
            except ValueError:
                pass

        text = ' '.join(words)

        return text.lower()

    @staticmethod
    def normalize_decimal(text):
        text_ = text.strip()
        if text_.endswith(','):
            text_ = text_[:-1]

        zero_suffix = re.compile(r"[0-9]+\.0+$")
        if zero_suffix.match(text):
            text_ = re.sub(r"\.0+", r"", text_)

        text_ = TextNormalization.digit_transcripter.number_to_words(text_)
        text_ = text_.replace('-', ' ')
        text_ = text_.replace(',', '')
        text_ = text_.replace(' and ', ' ')

        if text.isdigit():
            if all(c == '0' for c in text) and len(text) > 1:
                # text_ = ' '.join('o' * len(text))
                text_ = 'zero'
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
            if text.isupper():
                int_ = str(roman.fromRoman(text))
                text_ = TextNormalization.normalize_decimal(int_)
                return text_
            else:
                if text in ['mix']:
                    return text
                else:
                    return ' '.join(list(text))

    @staticmethod
    def normalize_capital_dot(text):
        return text.lower().replace('.', ' ').strip()

    @staticmethod
    def normalize_capital_letter(text):
        if len(text) >= 2:
            if not text in TextNormalization.capitals and not TextNormalization.has_vowel(text):
                return ' '.join(list(text.lower()))
            else:
                return text
        else:
            return text

    @staticmethod
    def normalize_url(text):
        # no idea why space sperated
        url = ' '.join(list(text.lower()))
        url = url.replace(':', 'colon')
        url = url.replace('.', 'dot')
        url = url.replace('/', 'slash')
        url = url.replace('-', 'dash')
        url = url.replace('#', 'hash')
        url = url.replace('_', 'u n d e r s c o r e')
        url = url.replace('%', 'p e r c e n t')
        url = url.replace(')', 'c l o s i n g p a r e n t h e s i s')
        url = url.replace("'", 's i n g l e q u o t e')
        url = url.replace("~", 't i l d e')
        url = url.replace('1', 'o n e')
        url = url.replace('2', 't w o')
        url = url.replace('3', 't h r e e')
        url = url.replace('4', 'f o u r')
        url = url.replace('5', 'f i v e')
        url = url.replace('6', 's i x')
        url = url.replace('7', 's e v e n')
        url = url.replace('8', 'e i g h t')
        url = url.replace('9', 'n i n e')
        url = url.replace('0', 'o')
        return url

    @staticmethod
    def normalize_hash_tag(text):
        text = text.replace('#', '')
        text = text.lower()
        text = 'hash tag ' + text
        return text

    @staticmethod
    def normalize_hyphen(text):
        text = text.replace('-', '')
        text = text.lower()
        text = ' '.join(list(text))
        return text

    def normalize_all(self):
        print('start normalization')
        self.df_test['after'] = self.df_test['before'].apply(lambda x: self.normalize2(x, previous=x.shift(1), following=x.shift(-1)))

        print('make id')
        self.df_test['id'] = self.df_test['sentence_id'].map(str) + '_' + self.df_test['token_id'].map(str)

        print('make sub df')
        df_compare = self.df_test[['id', 'before', 'after']]
        df_compare = df_compare[df_compare['before'] != df_compare['after']]

        df_result = self.df_test[['id', 'after']]

        print('save as csv')
        df_compare.to_csv(self.compare_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
        df_result.to_csv(self.result_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

    def normalize2(self, text, language='en_US', previous=None, following=None):
        normalized_text, case = self.normalize(text, language, previous=previous, following=following)
        words = [x for x in normalized_text.split(' ') if x]
        for index, word in enumerate(words):
            if self.DECIMAL_COMMA_OPTIONAL.match(word):
                words[index] = TextNormalization.normalize_decimal(word)

        return ' '.join(words), case

    def normalize(self, text, language='en_US', previous=None, following=None):
        normalized_text = ''
        case = ''
        # if text in self.d_replace.keys():
        #     print('Case REPLACE', text)
        #     normalized_text = self.d_replace[text]
        # elif text.isupper() and text.isalpha() and len(text) > 1 and self.has_vowel(text):
        #     print('Case UPPER_WORD', text)
        #     normalized_text = text
        # elif text.isupper() and text.isalpha() and len(text) > 1 and not self.has_vowel(text):
        #     print('Case UPPER_NON_WORD', text)
        #     normalized_text = " ".join(text.lower())
        # elif text[:-2].isupper() and text.isalpha() and text[-2:] == "'s" and not self.has_vowel(text):
        #     print('Case UPPER_S_0', text)
        #     normalized_text = " ".join(text[:-2].lower()) + "'s"
        # elif text[:-1].isupper() and text.isalpha() and text[-1:] == "s" and len(text) > 2 and not self.has_vowel(text):  # SEALs
        #     print('Case UPPER_S_1', text)
        #     normalized_text = " ".join(text[:-1].lower()) + "'s"

        if isinstance(text, float) and pd.isnull(text):
            case = 'NULL'
            normalized_text = ""
        elif text in ['-'] and (previous and following):
            case = 'TO_1'
            if (previous.isdigit() and following.isdigit()):
                normalized_text = 'to'
            else:
                normalized_text = text
        elif text in ['~', ':'] and previous and following:
            case = 'TO_2'
            if (previous.isdigit() and following.isdigit()):
                normalized_text = 'to'
            else:
                normalized_text = text
        elif text in ['x', 'x '] and previous and following:
            case = 'BY'
            if (TextNormalization.has_digit(previous) and TextNormalization.has_digit(following)):
                normalized_text = 'by'
            else:
                normalized_text = text
        elif text == 'min' and previous:
            case = 'MIN'
            if previous.isdigit():
                normalized_text = 'minute'
            else:
                normalized_text = text
        elif text in ['no', 'No', 'NO'] and following:
            case = 'NUM'
            if following.isdigit():
                normalized_text = 'number'
            else:
                normalized_text = text
        elif text in ['#'] and following:
            case = 'HASH'
            if not following.isdigit():
                normalized_text = 'hash'
            else:
                normalized_text = 'number'
        elif self.YEAR_CALENDAR.match(text):
            case = 'YEAR_CALENDAR'
            print('Case YEAR_CALENDAR', text)
            normalized_text = TextNormalization.normalize_year_calendar(text, previous=previous, following=following)
        elif self.YEAR.match(text) and 1001 <= int(text.strip()) <= 2099:
            case = 'YEAR'
            print('Case YEAR', text)
            if text.isdigit():
                normalized_text = TextNormalization.normalize_year(text, previous=previous, following=following)
            elif text.endswith(' '):  # TODO: handle xxxties
                normalized_text = TextNormalization.normalize_year(text[:-1], previous=previous, following=following)
            else:
                normalized_text = text
        elif self.DATE_YYYYMMDD.match(text) or self.DATE_YYYYMD.match(text):
            case = 'DATE_YYYYMMDD'
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

            weekday = None
            if not text_[0].isdigit():
                for i, c in enumerate(text_):
                    if c.isdigit():
                        break
                weekday, text_ = text_[:i], text_[i:]
                weekday = weekday.lower().strip()
                weekday = weekday.replace(',', '')
                weekday = weekday.replace('.', '')
                if len(weekday) <= 3:
                    weekday = TextNormalization.normalize_weekday(weekday)

            if delimiter:
                year, month, day = text_.split(delimiter)
            else:
                year, month, day = text[:4], text[4:6], text[6:]
            try:
                normalized_year = TextNormalization.normalize_year(year, language, previous=previous, following=following)
                normalized_month = TextNormalization.normalize_month(month, language)
                normalized_day = TextNormalization.normalize_day(day, language)
                if language == 'en_US':
                    text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                else:
                    text_ = '{0}年{1}月{2}日'.format(normalized_year, normalized_month, normalized_day)
                if weekday:
                    text_ = weekday + ' ' + text_
                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_MMDDYYYY.match(text) or self.DATE_MDYYYY.match(text) or self.DATE_MMDDYY.match(text):
            case = 'DATE_MMDDYYYY'
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

            weekday = None
            if not text_[0].isdigit():
                for i, c in enumerate(text_):
                    if c.isdigit():
                        break
                weekday, text_ = text_[:i], text_[i:]
                weekday = weekday.lower().strip()
                weekday = weekday.replace(',', '')
                weekday = weekday.replace('.', '')
                if len(weekday) <= 3:
                    weekday = TextNormalization.normalize_weekday(weekday)

            if delimiter:
                month, day, year = text_.split(delimiter)
            else:
                month, day, year = text[:2], text[2:4], text[4:]
            try:
                normalized_year = TextNormalization.normalize_year(year, language, previous=previous, following=following)
                normalized_month = TextNormalization.normalize_month(month, language)
                normalized_day = TextNormalization.normalize_day(day, language)
                if language == 'en_US':
                    if normalized_day.startswith('tw') or normalized_day.startswith('seventeenth'):
                        text_ = '{0} {1} {2}'.format(normalized_month, normalized_day, normalized_year)
                    else:
                        text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                    if weekday:
                        text_ = weekday + ' ' + text_
                else:
                    text_ = '{0}年{1}月{2}日'.format(normalized_year, normalized_month, normalized_day)
                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_DDMMYYYY.match(text) or self.DATE_DMYYYY.match(text) or self.DATE_DDMMYY.match(text):
            case = 'DATE_DDMMYYYY'
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
                normalized_year = TextNormalization.normalize_year(year, language, previous=previous, following=following)
                normalized_month = TextNormalization.normalize_month(month, language)
                normalized_day = TextNormalization.normalize_day(day, language)
                if language == 'en_US':
                    text_ = 'the {0} of {1} {2}'.format(normalized_day, normalized_month, normalized_year)
                else:
                    text_ = '{0}年{1}月{2}日'.format(normalized_year, normalized_month, normalized_day)
                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_MMDD.match(text):
            case = 'DATE_MMDD'
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
                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_DMY.match(text):
            case = 'DATE_EN_DMY'
            print('Case DATE_EN_DMY', text)
            text_ = text.strip()
            if text.strip().startswith('the '):
                text_ = text_[4:]
            text_ = text_.replace('.', '')
            text_ = text_.replace(',', '')
            text_ = text_.replace('-', ' ')
            words = text_.split(' ')

            weekday, calendar = None, None
            if len(words) == 3:
                day, month, year = words
            else:
                if len(words) > 4:
                    weekday, day, month, year, calendar = words
                    weekday = weekday.lower().replace(',', '')
                    calendar = ' '.join(list(calendar.lower()))
                else:
                    if words[-1].isdigit():
                        weekday, day, month, year = words
                        weekday = weekday.lower().replace(',', '')
                    else:
                        day, month, year, calendar = words
                        calendar = ' '.join(list(calendar.lower()))

            try:
                normalized_year = TextNormalization.normalize_year(year, previous=previous, following=following)
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
                if calendar:
                    text_ += ' ' + calendar

                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MDY.match(text):
            case = 'DATE_EN_MDY'
            print('Case DATE_EN_MDY', text)
            text_ = text.strip()
            if text.strip().startswith('the '):
                text_ = text[4:]
            text_ = text_.replace('.', '')
            text_ = text_.replace(',', '')
            text_ = text_.replace('-', ' ')
            words = text_.split(' ')

            weekday, calendar = None, None
            if len(words) == 3:
                month, day, year = words
            else:
                if len(words) > 4:
                    weekday, month, day, year, calendar = words
                    weekday = weekday.lower().replace(',', '')
                    calendar = ' '.join(list(calendar.lower()))
                else:
                    if words[-1].isdigit():
                        weekday, month, day, year = words
                        weekday = weekday.lower().replace(',', '')
                    else:
                        month, day, year, calendar = words
                        calendar = ' '.join(list(calendar.lower()))

            try:
                normalized_year = TextNormalization.normalize_year(year, previous=previous, following=following)
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
                if calendar:
                    text_ += ' ' + calendar

                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_DM.match(text):
            case = 'DATE_EN_DM'
            print('Case DATE_EN_DM', text)
            text_ = text.strip()
            text_ = text_.replace('.', '')
            text_ = text_.replace(',', '')
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
                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MD.match(text):
            case = 'DATE_EN_MD'
            print('Case DATE_EN_MD', text)
            text_ = text.strip()
            text_ = text_.replace('.', '')
            text_ = text_.replace(',', '')
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
                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.DATE_EN_MY.match(text):
            case = 'DATE_EN_MY'
            print('Case DATE_EN_MY', text)
            text_ = text.strip()
            text_ = text_.replace('.', '')
            text_ = text_.replace(',', '')
            month, year = text_.split(' ')
            try:
                normalized_year = TextNormalization.normalize_year(year, previous=previous, following=following)
                if len(month) <= 4:
                    normalized_month = TextNormalization.normalize_en_month(month.lower())
                else:
                    normalized_month = month.lower()
                text_ = '{0} {1}'.format(normalized_month, normalized_year)
                normalized_text = text_
            except KeyError as e:
                print(e)
                normalized_text = text
            except Exception as e:
                print(e)
                raise
        elif self.TELEPHONE_COMMON.match(text):
            case = 'TELEPHONE_COMMON'
            print('Case TELEPHONE_COMMON', text)
            normalized_text = TextNormalization.normalize_telephone_common(text)
        elif self.ISBN.match(text):
            case = 'ISBN'
            print('Case ISBN', text)
            if text.isdigit():
                normalized_text = TextNormalization.normalize_decimal(text)
            else:
                normalized_text = TextNormalization.normalize_telephone(text, language)
        elif self.LEADING_ZERO.match(text):
            case = 'LEADING_ZERO'
            print('Case LEADING_ZERO', text)
            normalized_text = TextNormalization.normalize_leading_zero(text)
        elif self.DECIMAL_COMMA_OPTIONAL.match(text):
            case = 'DECIMAL_COMMA_OPTIONAL'
            print('Case DECIMAL_COMMA_OPTIONAL', text)
            if text.isdigit():
                if int(text) <= 10000:
                    normalized_text = TextNormalization.normalize_decimal(text)
                else:
                    normalized_text = text
            else:
                normalized_text = TextNormalization.normalize_decimal(text)
        elif self.PERCENT.match(text):
            case = 'PERCENT'
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
            normalized_text = text_
        elif self.MEASURE.match(text):
            case = 'MEASURE'
            print('Case MEASURE', text)
            normalized_text = TextNormalization.normalize_measure(text)
        elif self.CLOCK.match(text):
            case = 'CLOCK'
            print('Case CLOCK', text)
            normalized_text = TextNormalization.normalize_clock(text)
        elif self.SECONDS.match(text):
            case = 'SECONDS'
            print('Case SECONDS', text)
            normalized_text = TextNormalization.normalize_seconds(text)
        elif self.MILLISECONDS.match(text):
            case = 'MILLISECONDS'
            print('Case MILLISECONDS', text)
            normalized_text = TextNormalization.normalize_milliseconds(text)
        elif self.FRACTION.match(text):
            case = 'FRACTION'
            print('Case FRACTION', text)
            normalized_text = TextNormalization.normalize_fraction(text)
        elif self.CURRENCY.match(text):
            case = 'CURRENCY'
            print('Case CURRENCY', text)
            normalized_text = TextNormalization.normalize_currency(text)
        elif self.ALPHADIGIT.match(text):
            case = 'ALPHADIGIT'
            print('Case ALPHADIGIT', text)
            normalized_text = TextNormalization.normalize_alphadigit(text)
        elif self.TELEPHONE.match(text):
            case = 'TELEPHONE'
            print('Case TELEPHONE', text)
            normalized_text = TextNormalization.normalize_telephone(text)
        elif self.IPv4.match(text):
            case = 'IPV4'
            print('Case IPv4', text)
            normalized_text = TextNormalization.normalize_ipv4(text, language)

        elif self.ROMAN.match(text):
            case = 'ROMAN'
            print('Case ROMAN', text)
            normalized_text = TextNormalization.normalize_roman(text)
        elif self.URL.match(text):
            case = 'URL'
            print('Case URL', text)
            normalized_text = TextNormalization.normalize_url(text)
        elif self.HASHTAG.match(text):
            case = 'HASHTAG'
            print('Case HASHTAG', text)
            normalized_text = TextNormalization.normalize_hash_tag(text)
        elif self.HYPHEN.match(text):
            case = 'HYPHEN'
            print('Case HYPHEN', text)
            normalized_text = TextNormalization.normalize_hyphen(text)
        elif self.PROPER_CASE_CONCAT.match(text):
            case = 'PROPER_CASE_CONCAT'
            print('Case PROPER_CASE_CONCAT', text)
            normalized_text = text
        elif self.CAPITAL_DOT.match(text):
            case = 'CAPITAL_DOT'
            print('Case CAPITAL_DOT')
            normalized_text = TextNormalization.normalize_capital_dot(text)
        elif self.CAPITAL_LETTER.match(text):
            case = 'CAPITAL_LETTER'
            print('Case CAPITAL_LETTER')
            normalized_text = TextNormalization.normalize_capital_letter(text)
        elif self.REPLACE.match(text):
            case = 'REPLACE'
            print('Case REPLACE')
            d = {
                '49ers': 'forty niners',
                '76ers': 'seventy sixers'
            }
            normalized_text = d[text]
        # elif text.endswith('.') and len(text) > 1:
        #     case = 'LETTER'
        #     print('Case LETTER', text)
        #     text_ = text.replace('.', '').strip().lower()
        #     text_ = text_.replace(' ', '')
        #     text_ = " ".join(text_)
        #     normalized_text = text_
        else:
            case = 'NO_CHANGE'
            print('Case NO_CHANGE', text)
            normalized_text = text

        return normalized_text, case

if __name__ == '__main__':
    test_cases = [
        ('OutRun', None),
        ('0-306-80821-8', None),
        ('2012-08-16', None),
        ('432 BCE', None),
        ('432 BC.', None),
        ('53 CE', None),
        ('4000 B.C.', None),
        ('WORLD', None),
        ('O. C.', None),
        ("D'Amigo", None),
        ("-0.7%", None),
        ("25%", None),
        ("1.08 percent", None),
        ('0-306-80821-8', None),
        ('0 9512309 6 4', None),
        ('127.0.0.1', None),
        ('192.168.5.20/24', None),
        ('2500 MW', None),
        ('4.9 km2', None),
        ('5km2', None),
        ('26.9/km2', None),
        ('2221.8 lb', None),
        ('111.0 kg', None),
        ('11.8 MB', None),
        ('0.7 kg/m3', None),
        ('-355', None),
        ('325 000', None),
        ('-', None),
        ('23.01.2015', None),
        ('11/2/2010', None),
        ('28 FEBRUARY 2008', None),
        ('Saturday, 28 FEBRUARY 2008', None),
        ('Wednesday December 5, 2007', None),
        ('Sunday May 6th, 2009', None),
        ('Saturday, 8 February 1919', None),
        ('22nd March 2007', None),
        ('22 May', None),
        ('27 January ', None),
        ('October 28', None),
        ('Mar 08, 1981', None),
        ('22/03/2010', None),
        ('11/4/2014', None),
        ('5-18 JANUARY 2016', None),
        ('14 January ', None),
        ('June 23 rd 2014', None),
        ('11-20-2009', None),
        ('2-9-2011', None),
        ('01-01-90', None),
        ('20081981', None),
        ('3/17/07', None),
        ('1.40', None),
        ('1.0', None),
        ('.38', None),
        ('2011', None),
        ('2012', None),
        ('2160', None),
        ('05', None),
        ('001', None),
        ('00', None),
        ('0', None),
        ('0800', None),
        ('013', None),
        ('HERBS', None),
        ('1km', None),
        ('１', None),
        ('01 - 6', None),
        ('CXIII', None),
        ('0.95 g/cm3', None),
        ('08.08', None),
        ('(1966)3', None),
        ('978-0-300-11465-2', None),
        ('9780521653947', None),
        ('05 250', None),
        ('o', None),
        ('0', 'zero'),
        ('00', 'o o'),
        ('000', 'o o o'),
        ('33130', None),
        ('91430', None),
        ('38115', None),
        ('27""', None),
        ('.0', None),
        ('9-1-1', None),
        ('911', None),
        ('999', None),
        ('26787', None),
        ('57950', None),
        ('9268', None),
        ('60', None),
        ('2300-0200', None),
        ('I', None),
        ('', None),
        ('10:30 p.m.', None),
        ('1000 BCE.', None),
        ('６', None),
        ('0100-0400', None),
        ('Playbill.com', None),
        ('4/24/00', None),
        ('3.3 million m²', None),
        ('21 years', 'twenty one years'),
        ('15,500 km2', 'fifteen thousand five hundred square kilometers'),
        ('10 a.m.', 'ten a m'),
        ('-2,000/ha', None),
        ('-2,000 ha', None),
        ('4 ½', 'four and a half'),
        ('4½', 'four and a half'),
        ('¼', 'one quarter'),
        ('1¼ mi', None),
        ('2, ', 'two'),
        ('18.7 g', 'eighteen point seven grams'),
        ('3.25 million', None),
        ('83 %', 'eighty three percent'),
        ('78.03 %', 'seventy eight point o three percent'),
        ('450 mV', None),
        ('8 May,', 'the eighth of may'),
        ('80, ', 'eighty'),
        ('May 11th 2011', None),
        ('Friday, 7/17/2015', None),
        ('20152012', 'twenty million one hundred fifty two thousand twelve'),
        ("20140115","twenty million one hundred forty thousand one hundred fifteen"),
        ("19171930","nineteen million one hundred seventy one thousand nine hundred thirty"),
        # ("19840306","one nine eight four o three o six"),
        ('3 80 GB', None),
        ('/m', 'per meter'),
        ('8 million m²', 'eight million square meters'),
        ("200 ms","two hundred milliseconds"),
        ('$745,244', None),
        ('100 metres', 'one hundred meters'),
        ('3700 BC', None),
        ('12:35 a.m.', 'twelve thirty five a m'),
        ('US$100,000', 'one hundred thousand dollars'),
        ('$ 16.8 billion', 'sixteen point eight billion dollars'),
        ('１', '１'),
        ('per km2', 'per square kilometer'),
        ('2: 45', 'two forty five'),
        ('51 BCE,', 'fifty one b c e'),
        ('415 B.C.', 'four fifteen b c'),
        ('2 Feb 70', None),
        ('7-13 2014', None),
        ('the 27 June 2007', 'the twenty seventh of june two thousand seven'),
        ('7 770', None),
        ('7 770ha', None),
        ('7770ha', None),
        ('NOK 1.2 billion', None),
        ('6:00', "six o'clock"),
        ('16:00', "sixteen hundred"),
        ('22 feb 2016', 'the twenty second of february twenty sixteen'),
        ('£295m', 'two hundred ninety five million pounds'),
        ('9 December 2005,', 'the ninth of december two thousand five'),
        ('$303.8m', 'three hundred three point eight million dollars'),
        ('$500M', 'five hundred million dollars'),
        ('$120 000', 'one hundred twenty thousand dollars'),
        ('$44.00', 'forty four dollars'),
        ("$7.0 Million","seven million dollars"),
        ('35059-098', None),
        ('US$5 million', 'five million dollars'),
        ('$300,000', 'three hundred thousand dollars'),
        ('$300k', 'three hundred thousand dollars'),
        ('$4billion', 'four billion dollars'),
        ('$12B', 'twelve billion dollars'),
        ("Rs 10 lakh","ten lakh rupees"),
        ("Rs 4,000 cr","four thousand crore rupees"),
        ("Rs 1,000 crore","one thousand crore rupees"),
        ('LB', None),
        ('/ km²', 'per square kilometers'),
        ('XK', 'x k'),
        ('C64 ', None),
        ('KB', None),
        ('CRC2142', 'two thousand one hundred forty two costa rican colons'),
        ('CYP-450', 'minus four hundred fifty cypriot pounds'),
        ('MDL-72222', 'minus seventy two thousand two hundred twenty two moldovan leus'),
        ('BMD-1', None),
        ('DKK 50 000', None),
        ('NAD83', None),
        ('PHP387M', None),
        ('7:30PM IST', 'seven thirty p m i s t'),
        ('04.20pm IST', 'four twenty p m i s t'),
        ('16:53:20 UTC', None),  # and twenty seconds
        ('12:32 UTC', 'twelve thirty two u t c'),
        ('06:00 UTC', "six o'clock u t c"),
        ('15:00 GMT', 'fifteen hundred g m t'),
        ('18:37 GMT', 'eighteen thirty seven g m t'),
        ('02:30 PM ET', 'two thirty p m e t'),
        ('4pm ET', 'four p m e t'),
        ('4:06 PM ET', 'four o six p m e t'),
        ('10:29 PM ET', 'ten twenty nine p m e t'),
        ('10 p.m. ET', 'ten p m e t'),
        ('9:00 pm ET', 'nine p m e t'),
        ('11:14 PM EDT', 'eleven fourteen p m e d t'),
        ('8:45 PM CST', 'eight forty five p m c s t'),
        ('2:08PM PDT', 'two o eight p m p d t'),
        ('8:00 AM PST', 'eight a m p s t'),
        ('10:24am EST', 'ten twenty four a m e s t'),
        ('8 pm AEST', 'eight p m a e s t'),
        ('3.32pm GMT', 'three thirty two p m g m t'),
        ('12:38 P.M. EST', 'twelve thirty eight p m e s t'),
        ("2:34.19","two minutes thirty four seconds and nineteen milliseconds"),
        ("17 november 2016", "the seventeenth of november twenty sixteen"),
        ('Thursday, 17-Nov-2016', None),
        ('14TH OCTOBER 2013', "the fourteenth of october twenty thirteen"),
        ('Fri, 07/22/2011', "friday july twenty second twenty eleven"),
        ("Friday March 7, 1980","friday march seventh nineteen eighty"),
        ('23-Mar-1998', "the twenty third of march nineteen ninety eight"),
        ('10-April-2014', "the tenth of april twenty fourteen"),
        ('6/03/2014', None),
        ('Sun. 2017-03-16', "sunday the sixteenth of march twenty seventeen"),
        ('12-NOV-1874', 'the twelfth of november eighteen seventy four'),
        ("1743.06.23","the twenty third of june seventeen forty three"),
        ("01.10.2008","the tenth of january two thousand eight"),
        ("20:00:00 EDT","twenty hours zero minutes and zero seconds e d t"),
        ("26.9.2000","the twenty sixth of september two thousand"),
        ("2:28.12","two minutes twenty eight seconds and twelve milliseconds"),
        ('¥3 Billion', 'three billion yen'),
        # ("£77,039.89", "seventy seven thousand thirty nine pounds and eighty nine pence"),
        # ("$88434.05","eighty eight thousand four hundred thirty four dollars and five cents"),
        ('144kb', 'one hundred forty four kilobits'),
        ('76ers', 'seventy sixers'),
        ('49ers', 'forty niners'),
        ('2min', None),
        ('19617 12-JUL-1999 MINISTERIO DE JUSTICIA', None),
        ('(1904) 1 CLR 497', None),
        ('(1992) 2 SCC 105', None),
        ('cv-', 'c v'),
        ('pyran-', 'p y r a n'),
        ('#EndMommyWars', 'hash tag endmommywars'),
        ('2013in', 'two thousand thirteen inches'),
        ('485 U.S. ', 'four hundred eighty five'),
        ('U.S.', 'u s'),
        ("$612 MILLION", "six hundred twelve million dollars"),
        ("200 C.E.","two hundred c e"),
        ("0.008 AU","zero point o o eight astronomical units"),
        (".5AU","point five astronomical units"),
        ("1795 / 1805","one thousand seven hundred ninety five one thousand eight hundred fifths"),
        ("1507/8","one thousand five hundred seven eighths"),
        ("3/2009","three two thousand ninths"),
        ("66/100","sixty six one hundredths"),
        ("2009/106982","two thousand nine one hundred six thousand nine hundred eighty seconds"),
        ("8 1/2","eight and a half"),
        ("1995/20","one thousand nine hundred ninety five twentieths"),
        ("3520/3540","three thousand five hundred twenty three thousand five hundred fortieths"),
        ("5/2001","five two thousand firsts"),
        ("26/11","twenty six elevenths"),
        ("0/110","zero one hundred tenths"),
        ("1/1","one over one"),
        ("6/4","six quarters"),
        ("90/ 3","ninety thirds"),
        ("-3202/11","minus three thousand two hundred two elevenths"),
        ("-495/95", "minus four hundred ninety five ninety fifths"),
        ("33 1/3", "thirty three and a third"),
        # ("36,578/15","thirty six thousand five hundred seventy eight fifteenths"),
        ("-5/5", None),
        ("-1/2","minus one half"),
        ("1/2","one half"),
        ("16/2","sixteen halves"),
        # ("172.22.0.0/15", "o n e s e v e n t w o dot t w e n t y t w o dot o dot o s l a s h f i f t e e n"),
        ('49ers', 'forty niners'),
        ('76ers', 'seventy sixers'),
        ('XXXV', 'thirty five'),
        ('xxxv', 'x x x v'),
        ("22.9/sq mi", "twenty two point nine per square miles"),
        ("8 10 1 212 XXXXXXX", None),
        ("2015-2016 YOUNG COMPOSERS", None),
        ("494-498 ISBN 0405077114", None),
        ("124-100 RA-82005", None),
        # ("50/60 Hz", 'fifty sixtieths hertz'),
        ("26 August 1303 CE.","the twenty sixth of august thirteen o three c e"),
        ("February 27, 1893 AD","february twenty seventh eighteen ninety three a d"),
        ("(", "("),
        (")", ")"),
        ("-", "-"),
        ("--", "--"),
        ("---", "---"),
        ("6435-", "six four three five"),
        ("8-7-2","eight sil seven sil two"),
        ("(2014) 38","two o one four sil three eight"),
        ("(1993)9","one nine nine three sil nine"),
        ("978-0-19-507678-3","nine seven eight sil o sil one nine sil five o seven six seven eight sil three"),
        ("14 8 1 5 38-30 17 5","one four sil eight sil one sil five sil three eight sil three o sil one seven sil five"),
        ("11-5 MAC","one one sil five sil mac"),
        ("0-333-73432-7 ISBN 1-56159-228-5","o sil three three three sil seven three four three two sil seven sil i s b n sil one sil five six one five nine sil two two eight sil five"),
        ("000 UNITS PER YEAR IN 2013","o o o sil units sil per sil year sil in sil two o one three"),
        ("350-340 BC","three five o sil three four o sil b c"),
        ("600-1000 AD","six hundred sil one thousand sil ad"),
        ("2007-216676 ECRYPT II","two o o seven sil two one six six seven six sil ecrypt sil ii"),
        ("183-188 ISBN 3-932965-86-8","one eight three sil one eight eight sil i s b n sil three sil nine three two nine six five sil eight six sil eight"),
        ("0812979699 OCLC 234316192","o eight one two nine seven nine six nine nine sil o c l c sil two three four three one six one nine two"),
        ("51 -- 1995 ADOPTION ACT","five one sil one nine nine five sil adoption sil act"),
        ("1-800-RUNAWAY","one sil eight hundred sil runaway"),
        ("138-EE","one three eight sil ee"),
        ("5-5-5","five sil five sil five"),
        ("(2007) 79-92","two o o seven sil seven nine sil nine two"),
        ("978-964-5983-33-6","nine seven eight sil nine six four sil five nine eight three sil three three sil six"),
        ("20(1) 65-72","two o sil one sil six five sil seven two"),
        ("978- 0-906294-72-7","nine seven eight sil o sil nine o six two nine four sil seven two sil seven"),
        ("0891-1851","o eight nine one sil one eight five one"),
        ("2223-2261","two two two three sil two two six one"),
        ("(24)27","two four sil two seven"),
        ("0719040019","o seven one nine o four o o one nine"),
        ("91-63 TO MOVE ON TO TORONTO 2015 FINAL","nine one sil six three sil to sil move sil on sil to sil toronto sil two o one five sil final"),
        # ("720-WGN","seven two o sil w g n"),
        # ("1205-1209x1211","one two o five sil one two o nine extension one two one one"),
        # ("0-8176-3647-1 MR 13218861994","o sil eight one seven six sil three six four seven sil one sil mister sil one three two one eight eight six one nine nine four"),
        ("17193107","seventeen million one hundred ninety three thousand one hundred seven"),
        ("9780824820664","nine trillion seven hundred eighty billion eight hundred twenty four million eight hundred twenty thousand six hundred sixty four"),
        ("06080291-","o six o eight o two nine one"),
        ("001005353","o o one o o five three five three"),
        ("B14","b fourteen"),
        ("M261","m two six one"),
        ("M31","m thirty one"),
        ("A1689","a one six eight nine"),
        ("I-49","i forty nine"),
        ("CR 16","c r sixteen"),
        ("US 3607316","u s three million six hundred seven thousand three hundred sixteen"),
        ("US2008013385","u s two billion eight million thirteen thousand three hundred eighty five"),
        ("U.S. 1828","u s eighteen twenty eight"),
        ("Interstate 86","interstate eighty six"),
        ("C01","c o one"),
        ("A330","a three thirty"),
        ("B03003","b o three o o three"),
        ("C00150367","c o o one five o three six seven"),
        ("C3047 ","c three o four seven"),
        ("M0 ","m o"),
        ("M020","m twenty"),
        ('C107 ', None),
        ('C613', None),
        ("I-5","i five"),
        ("A310","a three ten"),
        ("10:35:47","ten hours thirty five minutes and forty seven seconds"),
        ('15:37.39', 'fifteen minutes thirty seven seconds and thirty nine milliseconds'),
        ('18:30:00 GMT', 'eighteen hours thirty minutes and zero seconds g m t'),
        ("8:00pm","eight p m"),
        ("1:10","one ten"),
        ("20:00","twenty hundred"),
        ("10:00","ten o'clock"),
        ("4:07","four o seven"),
        ("1:00pm","one p m"),
        ("2 pm","two p m"),
        # ("00:01","zero o one"),
        ("0.8.7.0","o dot e i g h t dot s e v e n dot o"),
        ("16.14.12.10","s i x t e e n dot f o u r t e e n dot t w e l v e dot t e n"),
        ("10.47.16.5", None)
    ]

    text_normalization = TextNormalization()

    for test_case in test_cases:
        normalized_text, case = text_normalization.normalize2(test_case[0])
        print(normalized_text)
        if test_case[1]:
            assert normalized_text == test_case[1]
        print()

    # print(text_normalization.normalize_year('2011'))
    # print(text_normalization.normalize_year('2011', previous='-'))
    # print(text_normalization.normalize_year('2011', following='-'))

    # text_normalization.normalize_all()
