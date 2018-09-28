# Spell Checker
[![CircleCI](https://circleci.com/gh/ElementAI/eai-spellchecker/tree/master.svg?style=svg)](https://circleci.com/gh/ElementAI/eai-spellchecker/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/ElementAI/eai-spellchecker/badge.svg?branch=master)](https://coveralls.io/github/ElementAI/eai-spellchecker?branch=master)

This code is based on [symspellpy](https://github.com/mammothb/symspellpy) a Python port of 
[SymSpell](https://github.com/wolfgarbe/SymSpell) v6.3, which provides much higher speed and 
lower memory consumption. 


## Usage
[Samples](./samples) can be run using

```bash
poetry run python samples/simple_spellcheck.py
```

## Contributing
If you don't have experience with Poetry you may want to first read the 
[introductory guide](https://elementai.atlassian.net/wiki/spaces/PIE/pages/560726075/Poetry+User+Guide).


### Environment Setup
To setup your local environment simply run `make bootstrap` and `make install`. The virtual environment will be
created by Poetry in `.venv`.

### Building and Uploading to PyPI

<em>This is assuming that you have already configured poetry to push to our 
internal pypi repo. If not, please refer to the 
[introductory guide](https://elementai.atlassian.net/wiki/spaces/PIE/pages/560726075/Poetry+User+Guide).</em>
 
Make your changes as usual and check the build is green (i.e. the tests are passing). 
Once this is done, update to the wanted version using the `poetry version` command. Don't forget
to push the updated `pyproject.toml`. Finally, you can build and publish the library with `poetry` 
using the `publish` command, like so:

```bash
poetry publish -r eai-core --build
```

This will use the poetry config value for `repositories.eai-core` and `http-basic.eai-core` to
authenticate and upload to the specified repo. So be sure the values are set appropriately
beforehand.

It is also possible to only build with `poetry build`.


