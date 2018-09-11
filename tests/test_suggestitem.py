# test_suggestitem.py
# Guy Dumais, 2018-09-11
# Copyright (c) 2018 Element AI. All rights reserved.

from spellchecker.symspell import SuggestItem


def test_suggest_item_sorting():
    suggest_items = [
        SuggestItem('Ste-Paule', 'St-Paul', "Saint-Paul-d'Abbotsford", 2, 1),
        SuggestItem('Ste-Paule', 'St-Paul', 'Saint-Paul', 2, 10),
        SuggestItem('Ste-Paule', 'St-Paul', "Saint-Paul-de-l'Île-aux-Noix", 2, 7),
    ]

    # Saint-Paul because is has more occurrences
    assert sorted(suggest_items)[0].term == 'Saint-Paul'
    assert sorted(suggest_items)[0].count == 10

    suggest_items.append(
        SuggestItem('San Pualo', 'San Paulo', 'San Paulo City', 1, 1)
    )

    # San Paulo City because input 'San Pualo' closer to matching key 'San Paulo'
    assert sorted(suggest_items)[0].term == 'San Paulo City'
    assert sorted(suggest_items)[0].distance == 1

    suggest_items.append(
        SuggestItem('San Paulo', 'Sao Paulo', 'São Paulo', 1, 1)
    )

    # São Paulo because input San Paulo is closer to canonical term São Paulo
    assert sorted(suggest_items)[0].term == 'São Paulo'
    assert sorted(suggest_items)[0].matching_term == 'Sao Paulo'
