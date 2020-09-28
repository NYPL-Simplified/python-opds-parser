# python-webpub-manifest-parser

[![Build Status](https://travis-ci.com/vbessonov/python-webpub-manifest-parser.svg?branch=master)](https://travis-ci.com/vbessonov/python-webpub-manifest-parser)

Library containing a parser (webpub-manifest-parser) designed to parse [Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest) compatible documents such as [Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0) documents describing electronic publications.

## Usage
1. [Install pyenv](https://github.com/pyenv/pyenv#installation)

3. Install one of the supported Python versions mentioned in [.python-version](.python-version) or other PATCH versions of the same MINOR versions:
```bash
pyenv install <python-version>
```

4. [Install pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation) plugin

5. Create a virtual environment:
```bash
pyenv virtualenv <virtual-env-name>
pyenv activate <virtual-env-name>
```

6. Install the library
```bash
pip install webpub-manifest-parser
``` 
