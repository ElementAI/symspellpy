import csv
import re
from os import path
from typing import Dict, List


def null_distance_results(string1, string2, max_distance):
    """Determines the proper return value of an edit distance function when
    one or both strings are null.
    """
    if string1 is None:
        if string2 is None:
            return 0
        else:
            return len(string2) if len(string2) <= max_distance else -1
    return len(string1) if len(string1) <= max_distance else -1


def prefix_suffix_prep(string1, string2):
    """Calculates starting position and lengths of two strings such that
    common prefix and suffix substrings are excluded.
    Expects len(string1) <= len(string2)
    """
    # this is also the minimun length of the two strings
    len1 = len(string1)
    len2 = len(string2)
    # suffix common to both strings can be ignored
    while len1 != 0 and string1[len1 - 1] == string2[len2 - 1]:
        len1 -= 1
        len2 -= 1
    # prefix common to both strings can be ignored
    start = 0
    while start != len1 and string1[start] == string2[start]:
        start += 1
    if start != 0:
        len1 -= start
        # length of the part excluding common prefix and suffix
        len2 -= start
    return len1, len2, start


def to_similarity(distance, length):
    return -1 if distance < 0 else 1.0 - distance / length


def try_parse_int64(string):
    try:
        ret = int(string)
    except ValueError:
        return None
    return None if ret < -2 ** 64 or ret >= 2 ** 64 else ret


def parse_words(phrase, preserve_case=False):
    """create a non-unique wordlist from sample text
    language independent (e.g. works with Chinese characters)
    """
    # \W non-words, use negated set to ignore non-words and "_" (underscore)
    # Compatible with non-latin characters, does not split words at
    # apostrophes
    if preserve_case:
        return re.findall(r"([^\W_]+['’]*[^\W_]*)", phrase)
    else:
        return re.findall(r"([^\W_]+['’]*[^\W_]*)", phrase.lower())


def is_acronym(word):
    """Checks is the word is all caps (acronym) and/or contain numbers

    Return:
    True if the word is all caps and/or contain numbers, e.g., ABCDE, AB12C
    False if the word contains lower case letters, e.g., abcde, ABCde, abcDE,
        abCDe, abc12, ab12c
    """
    return re.match(r"\b[A-Z0-9]{2,}\b", word) is not None


class SpaceDelimitedFileIterator:
    """
    Iterator on a space delimited file. This class is limited to single term entries.
    If you want to support entries with multiple terms, use the CsvFileIterator.

    The file format is similar to
        the 23135851162
        of 13151942776
        and 12997637966
        to 12136980858
        a 9081174698
        in 8469404971
        travelling 6271787 traveling
    where one column contains the term to lookup, the number of occurrences in the
    source corpus and the 'canonical utterance' of the term (e.g traveling is preferred over
    travelling). The canonical utterance is optional.
    """

    def __init__(self, corpus: str, term_index: int=0, count_index: int=1, canonical_term_index: int=None):
        if not path.exists(corpus):
            raise FileNotFoundError(f'Could not open file {corpus}')

        self.term_index = term_index
        self.count_index = count_index
        self.canonical_term_index = canonical_term_index
        self.f = open(corpus, 'r')

    def __iter__(self):
        return self

    def __next__(self):
        line = self.f.readline()
        if line:
            line_parts = line.rstrip().split(" ")
            if len(line_parts) >= 2:
                term = line_parts[self.term_index]
                count = try_parse_int64(line_parts[self.count_index])
                if count is not None:
                    canonical_term = line_parts[self.canonical_term_index] if self.canonical_term_index else None
                    return term, count, canonical_term
        raise StopIteration


class CsvFileIterator:
    """
    Iterate over a CSV file.
    The file format must be similar to
       the, 23135851162,
       of, 13151942776,
       and, 12997637966,
       to, 12136980858,
       a, 9081174698,
       in, 8469404971,
       travelling, 6271787, traveling
    where the first column contains the term to lookup, the second column contains the number of
    occurrences in the source corpus and the last column is the 'canonical utterance' of the term
    (e.g traveling is preferred over travelling). The canonical utterance is optional.
    """

    def __init__(self, corpus: str, term_col: str='term', count_col: str='count',
                 canonical_term_col: str='canonical_term'):
        if not path.exists(corpus):
            raise FileNotFoundError(f'Could not open file {corpus}')

        self.f = csv.DictReader(open(corpus, 'r'))
        self.term_col = term_col
        self.count_col = count_col
        self.canonical_term_col = canonical_term_col

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.f)
        count = try_parse_int64(line[self.count_col])
        if count is not None:
            return line[self.term_col], \
                   count, \
                   line[self.canonical_term_col] if self.canonical_term_col in line else None


class ListIterator:
    """
    Iterate over a list for the SymSpell load_dictionary function.

    Args:
        corpus: A list of string to load in the SymSpell instance.
    """
    def __init__(self, corpus: List[str]):
        self.term_index = 0
        self.count_index = 1
        self.canonical_term_index = None
        self.f = corpus

    def __iter__(self):
        for word in self.f:
            yield word.strip().lower(), 1, word
