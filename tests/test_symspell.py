import csv
import sys
import tempfile
from os import pardir, path


from spellchecker.helpers import CsvFileIterator, SpaceDelimitedFileIterator
from spellchecker.symspell import SymSpell, Verbosity


def test_words_with_shared_prefix_should_retain_counts():
    sym_spell = SymSpell(16, 1, 3)
    sym_spell.create_dictionary_entry("pipe", 5)
    sym_spell.create_dictionary_entry("pips", 10)

    result = sym_spell.lookup("pipe", Verbosity.ALL, 1)
    assert 2 == len(result)
    assert "pipe" == result[0].term
    assert 5 == result[0].count
    assert "pips" == result[1].term
    assert 10 == result[1].count

    result = sym_spell.lookup("pips", Verbosity.ALL, 1)
    assert 2 == len(result)
    assert "pips" == result[0].term
    assert 10 == result[0].count
    assert "pipe" == result[1].term
    assert 5 == result[1].count

    result = sym_spell.lookup("pip", Verbosity.ALL, 1)
    assert 2 == len(result)
    assert "pips" == result[0].term
    assert 10 == result[0].count
    assert "pipe" == result[1].term
    assert 5 == result[1].count


def test_add_additional_counts_should_not_add_word_again():
    sym_spell = SymSpell()
    word = "hello"
    sym_spell.create_dictionary_entry(word, 11)
    assert 1 == sym_spell.word_count

    sym_spell.create_dictionary_entry(word, 3)
    assert 1 == sym_spell.word_count


def test_add_additional_counts_should_increase_count():
    sym_spell = SymSpell()
    word = "hello"
    sym_spell.create_dictionary_entry(word, 11)
    result = sym_spell.lookup(word, Verbosity.TOP)
    count = result[0].count if len(result) == 1 else 0
    assert 11 == count

    sym_spell.create_dictionary_entry(word, 3)
    result = sym_spell.lookup(word, Verbosity.TOP)
    count = result[0].count if len(result) == 1 else 0
    assert 11 + 3 == count


def test_add_additional_counts_should_not_overflow():
    sym_spell = SymSpell()
    word = "hello"
    sym_spell.create_dictionary_entry(word, sys.maxsize - 10)
    result = sym_spell.lookup(word, Verbosity.TOP)
    count = result[0].count if len(result) == 1 else 0
    assert sys.maxsize - 10 == count

    sym_spell.create_dictionary_entry(word, 11)
    result = sym_spell.lookup(word, Verbosity.TOP)
    count = result[0].count if len(result) == 1 else 0
    assert sys.maxsize == count


def test_verbosity_should_control_lookup_results():
    sym_spell = SymSpell()
    sym_spell.create_dictionary_entry("steam", 1)
    sym_spell.create_dictionary_entry("steams", 2)
    sym_spell.create_dictionary_entry("steem", 3)

    result = sym_spell.lookup("steems", Verbosity.TOP, 2)
    assert 1 == len(result)
    result = sym_spell.lookup("steems", Verbosity.CLOSEST, 2)
    assert 2 == len(result)
    result = sym_spell.lookup("steems", Verbosity.ALL, 2)
    assert 3 == len(result)


def test_lookup_should_return_most_frequent():
    sym_spell = SymSpell()
    sym_spell.create_dictionary_entry("steama", 4)
    sym_spell.create_dictionary_entry("steamb", 6)
    sym_spell.create_dictionary_entry("steamc", 2)
    result = sym_spell.lookup("stream", Verbosity.TOP, 2)
    assert 1 == len(result)
    assert "steamb" == result[0].term
    assert 6 == result[0].count


def test_lookup_should_find_exact_match():
    sym_spell = SymSpell()
    sym_spell.create_dictionary_entry("steama", 4)
    sym_spell.create_dictionary_entry("steamb", 6)
    sym_spell.create_dictionary_entry("steamc", 2)
    result = sym_spell.lookup("streama", Verbosity.TOP, 2)
    assert 1 == len(result)
    assert "steama" == result[0].term


def test_lookup_should_not_return_non_word_delete():
    sym_spell = SymSpell(16, 2, 7, 10)
    sym_spell.create_dictionary_entry("pawn", 10)
    result = sym_spell.lookup("paw", Verbosity.TOP, 0)
    assert not len(result)
    result = sym_spell.lookup("awn", Verbosity.TOP, 0)
    assert not len(result)


def test_lookup_should_not_return_low_count_word():
    sym_spell = SymSpell(16, 2, 7, 10)
    sym_spell.create_dictionary_entry("pawn", 1)
    result = sym_spell.lookup("pawn", Verbosity.TOP, 0)
    assert not len(result)


def test_lookup_should_not_return_low_count_word_that_are_also_delete_word():
    sym_spell = SymSpell(16, 2, 7, 10)
    sym_spell.create_dictionary_entry("flame", 20)
    sym_spell.create_dictionary_entry("flam", 1)
    result = sym_spell.lookup("flam", Verbosity.TOP, 0)
    assert not len(result)


def test_lookup_should_replicate_noisy_results():
    cwd = path.realpath(path.dirname(__file__))
    dictionary_path = path.realpath(path.join(
        cwd, pardir, "spellchecker", "frequency_dictionary_en_82_765.txt"))
    query_path = path.join(cwd, "fortests", "noisy_query_en_1000.txt")

    edit_distance_max = 2
    prefix_length = 7
    verbosity = Verbosity.CLOSEST
    sym_spell = SymSpell(83000, edit_distance_max, prefix_length)
    dict_iter = SpaceDelimitedFileIterator(dictionary_path, 0, 1)
    sym_spell.load_dictionary(dict_iter)

    test_list = []
    with open(query_path, "r") as infile:
        for line in infile.readlines():
            line_parts = line.rstrip().split(" ")
            if len(line_parts) >= 2:
                test_list.append(line_parts[0])
    result_sum = 0
    for phrase in test_list:
        result_sum += len(sym_spell.lookup(phrase, verbosity,
                                           edit_distance_max))
    assert 4945 == result_sum


def test_lookup_compound():
    cwd = path.realpath(path.dirname(__file__))
    dictionary_path = path.realpath(path.join(
        cwd, pardir, "spellchecker", "frequency_dictionary_en_82_765.txt"))

    edit_distance_max = 2
    prefix_length = 7
    sym_spell = SymSpell(83000, edit_distance_max, prefix_length)
    dict_iter = SpaceDelimitedFileIterator(dictionary_path, 0, 1)
    sym_spell.load_dictionary(dict_iter)

    typo = ("whereis th elove hehad dated forImuch of thepast who "
            "couqdn'tread in sixthgrade and ins pired him")
    correction = ("where is the love he had dated for much of the past "
                  "who couldn't read in sixth grade and inspired him")
    results = sym_spell.lookup_compound(typo, edit_distance_max)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = "in te dhird qarter oflast jear he hadlearned ofca sekretplan"
    correction = ("in the third quarter of last year he had learned of a "
                  "secret plan")
    results = sym_spell.lookup_compound(typo, edit_distance_max)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = ("the bigjest playrs in te strogsommer film slatew ith plety "
            "of funn")
    correction = ("the biggest players in the strong summer film slate "
                  "with plenty of fun")
    results = sym_spell.lookup_compound(typo, edit_distance_max)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = ("Can yu readthis messa ge despite thehorible sppelingmsitakes")
    correction = ("can you read this message despite the horrible "
                  "spelling mistakes")
    results = sym_spell.lookup_compound(typo, edit_distance_max)
    assert 1 == len(results)
    assert correction == results[0].term


def test_lookup_compound_ignore_non_words():
    cwd = path.realpath(path.dirname(__file__))
    dictionary_path = path.realpath(path.join(
        cwd, pardir, "spellchecker", "frequency_dictionary_en_82_765.txt"))

    edit_distance_max = 2
    prefix_length = 7
    sym_spell = SymSpell(83000, edit_distance_max, prefix_length)
    dict_iter = SpaceDelimitedFileIterator(dictionary_path, 0, 1)
    sym_spell.load_dictionary(dict_iter)

    typo = ("whereis th elove 123 hehad dated forImuch of THEPAST who "
            "couqdn'tread in SIXTHgrade and ins pired him")
    correction = ("where is the love 123 he had dated for much of THEPAST "
                  "who couldn't read in sixth grade and inspired him")
    results = sym_spell.lookup_compound(typo, edit_distance_max, True)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = "in te DHIRD 1 qarter oflast jear he hadlearned ofca sekretplan"
    correction = ("in the DHIRD 1 quarter of last year he had learned "
                  "of a secret plan")
    results = sym_spell.lookup_compound(typo, edit_distance_max, True)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = ("the bigjest playrs in te stroGSOmmer film slatew ith PLETY "
            "of 12 funn")
    correction = ("the biggest players in the strong summer film slate "
                  "with PLETY of 12 fun")
    results = sym_spell.lookup_compound(typo, edit_distance_max, True)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = ("Can yu readtHIS messa ge despite thehorible 1234 "
            "sppelingmsitakes")
    correction = ("can you read this message despite the horrible 1234 "
                  "spelling mistakes")
    results = sym_spell.lookup_compound(typo, edit_distance_max, True)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = ("Can yu readtHIS messa ge despite thehorible AB1234 "
            "sppelingmsitakes")
    correction = ("can you read this message despite the horrible AB1234 "
                  "spelling mistakes")
    results = sym_spell.lookup_compound(typo, edit_distance_max, True)
    assert 1 == len(results)
    assert correction == results[0].term

    typo = "PI on leave, arrange Co-I to do screening"
    correction = "PI on leave arrange co i to do screening"
    results = sym_spell.lookup_compound(typo, edit_distance_max, True)
    assert 1 == len(results)
    assert correction == results[0].term


def test_lookup_with_canonical_term():
    with tempfile.NamedTemporaryFile('w') as fp:
        col_names = ['term', 'count', 'canonical_term']
        csv_writer = csv.DictWriter(fp, fieldnames=col_names)
        csv_writer.writeheader()
        canonical_term = 'canonical test'
        for _ in range(10):
            csv_writer.writerow({'term': 'test', 'count': 1, 'canonical_term': canonical_term})
        fp.flush()

        sym_spell = SymSpell()
        sym_spell.load_dictionary(CsvFileIterator(fp.name))
        suggestions = sym_spell.lookup('Test', Verbosity.CLOSEST)
        assert 1 == len(suggestions)
        assert suggestions[0].term == canonical_term
