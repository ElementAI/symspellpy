# test_helpers.py
# Guy Dumais, 2018-09-04
# Copyright (c) 2018 Element AI. All rights reserved.
import csv
import tempfile

import pytest

from spellchecker.helpers import CsvFileIterator, SpaceDelimitedFileIterator


@pytest.mark.parametrize("line_count", [0, 1, 7, 1003])
def test_csv_reader(line_count):
    with tempfile.NamedTemporaryFile('w') as fp:
        col_names = ['term', 'count', 'canonical_term']
        csv_writer = csv.DictWriter(fp, fieldnames=col_names)
        csv_writer.writeheader()
        for _ in range(line_count):
            csv_writer.writerow({'term': 'test', 'count': 1, 'canonical_term': 'test'})
        fp.flush()

        lines = 0
        for term, count, canonical_term in CsvFileIterator(fp.name):
            assert term == 'test'
            assert count == 1
            assert canonical_term == 'test'
            lines += 1

        assert lines == line_count


@pytest.mark.parametrize("line_count", [0, 1, 7, 1003])
def test_space_separated_reader(line_count):
    csv.register_dialect('space', delimiter=' ')

    with tempfile.NamedTemporaryFile('w') as fp:
        col_names = ['term', 'count', 'canonical_term']
        csv_writer = csv.DictWriter(fp, fieldnames=col_names, dialect='space')
        for _ in range(line_count):
            csv_writer.writerow({'term': 'test', 'count': 1, 'canonical_term': 'test'})
        fp.flush()

        def test_lines(term_index, count_index, canonical_term_index,
                       expected_term, expected_count, expected_canonical_term):
            lines = 0
            for term, count, canonical_term in \
                    SpaceDelimitedFileIterator(fp.name, term_index, count_index, canonical_term_index):
                lines += 1
                assert term == expected_term
                assert count == expected_count
                assert canonical_term == expected_canonical_term

            assert lines == line_count

        test_lines(0, 1, None, 'test', 1, None)
        test_lines(0, 1, 2, 'test', 1, 'test')
