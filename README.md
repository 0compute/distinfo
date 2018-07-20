# Distinfo

[![Quality](https://app.codacy.com/project/badge/Grade/810984e4772f4a20863e1c384c54a5a6)](https://app.codacy.com/gh/0compute/distinfo/dashboard)
[![Coverage](https://app.codacy.com/project/badge/Coverage/810984e4772f4a20863e1c384c54a5a6)](https://app.codacy.com/gh/0compute/distinfo/dashboard)

`distinfo` is a library for extracting metadata from Python distributions.

It includes standard metadata per Python Metadata 2.1 plus an extra attribute, "ext",
for extended metadata. Metadata is collected from:
  * parsing of pyproject.toml, if dynamic also by calling PEP517 hook
    "prepare_metadata_for_build_wheel"
  * execution of the setup.py script
  * dist and egg info directories

## Usage

Print requirements and metadata:

``` python
>>> import distinfo
>>>
>>> dist = await distinfo.from_path("/path/to/package/source")
>>> distinfo.dump(dist)
author_email:
- A N Other <ano@example.org>
classifier:
- 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
- 'Operating System :: POSIX'
- 'Programming Language :: Python :: 3'
ext:
  build_backend: flit_core.buildapi
  collectors:
    PathMetadata: false
    PyProjectMetadata: true
  format: pyproject
  packages:
  - example
  path: /path/to/package/source
  scripts:
    example: example.cli:main
  tests:
  - tests
home_page: https://example.org
license: GPL-3.0-or-later
metadata_version: '2.1'
name: example
requires:
  build_system_requires:
  - flit-core<4,>=3.2
  dev:
  - pycmd
  run:
  - click
  - requests
  test:
  - pytest
requires_python: '>=3.10'
summary: Example project
version: 1.0.0
```

Cli output (yaml):

    $ distinfo /path/to/package/source

Cli specify format:

    $ distinfo -f [json|msgpack] /path/to/package/source

## Specifications

https://packaging.python.org/specifications/

### Metadata

* [Core Metadata](https://packaging.python.org/en/latest/specifications/core-metadata/)
* [PEP 241 - Metadata for Python Software Packages 1.0](https://www.python.org/dev/peps/pep-0241/)
* [PEP 314 - Metadata for Python Software Packages 1.1](https://www.python.org/dev/peps/pep-0314/)
* [PEP 345 - Metadata for Python Software Packages 1.2](https://www.python.org/dev/peps/pep-0345/)
* [PEP 517 - A build-system independent format for source trees](https://www.python.org/dev/peps/pep-0517/)
* [PEP 518 - Specifying Minimum Build System Requirements for Python Projects](https://www.python.org/dev/peps/pep-0518/)
* [PEP 566 - Metadata for Python Software Packages 2.1](https://www.python.org/dev/peps/pep-0566/)
* [PEP 621 - Storing project metadata in pyproject.toml](https://www.python.org/dev/peps/pep-0621/)
* [PEP 426 - Metadata for Python Software Packages 2.0 (withdrawn)](https://www.python.org/dev/peps/pep-0426/)
* [PEP 459 -- Standard Metadata Extensions for Python Software Packages (withdrawn)](https://www.python.org/dev/peps/pep-0459/)

### Dependencies

* [PEP 440 - Version Identification and Dependency Specification](https://www.python.org/dev/peps/pep-0440/)
* [PEP 508 - Dependency specification for Python Software Packages](https://www.python.org/dev/peps/pep-0508/)
