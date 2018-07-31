from pathlib import Path

from setuptools import setup, find_packages


setup(
    name="distinfo",
    version = "0.3.0.dev",
    author="Arthur Noel",
    author_email="arthur@0compute.net",
    url="https://github.com/0compute/distinfo",
    description="Extract metadata, including full dependencies, from source distributions",
    long_description=(Path(__file__).parent / "README.md").open().read(),
    long_description_content_type="text/markdown",
    keywords=("packaging", "metadata", "sdist"),
    license="GPL-3.0-or-later",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Software Distribution",
    ],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    entry_points=dict(
        console_scripts=(
            "distinfo = distinfo.cli:main",
        ),
    ),
    setup_requires=(
        "pytest-runner",
    ),
    install_requires=(
        "appdirs",
        "click",
        "coloredlogs",
        "munch",
        "pipreqs",
        "property-manager",
        "ptpython",
        "pytoml",
        "requirementslib",
        "tox",
        "pyyaml",
    ),
    tests_require=(
        "pytest-cov",
    ),
    extras_require=dict(
        dev=(
            "pdbpp",
            "prospector[with_everything]",
            "pytest-sugar",
        ),
    ),
    python_requires=">=3.6",
)
