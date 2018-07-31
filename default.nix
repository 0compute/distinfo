{
  pkgs ? import (builtins.fetchTarball {
    url = "https://github.com/nixos/nixpkgs/archive/a8c71037e041725d40fbf2f3047347b6833b1703.tar.gz";
    sha256 = "1z4cchcw7qgjhy0x6mnz7iqvpswc2nfjpdynxc54zpm66khfrjqw";
  }) {}
}:
with pkgs.lib;
let
  python = pkgs.python3;
  nix-gitignore = import (pkgs.fetchFromGitHub {
    owner = "siers";
    repo = "nix-gitignore";
    rev = "6dd9ece00991003c0f5d3b4da3f29e67956d266e";
    sha256 = "0jn5yryf511shdp8g9pwrsxgk57p6xhpb79dbi2sf5hzlqm2csy4";
  }) { inherit (pkgs) lib; };
in
with rec {

  alabaster = python.pkgs.buildPythonPackage rec {
    pname = "alabaster";
    version = "0.7.11";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "b63b1f4dc77c074d386752ec4a8a7517600f6c0db8cd42980cae17ab7b3275d7";
    };
    doCheck = false;
    meta = {
      description = "A configurable sidebar-enabled Sphinx theme";
      homepage = https://alabaster.readthedocs.io;
    };
  };

  apipkg = python.pkgs.buildPythonPackage rec {
    pname = "apipkg";
    version = "1.5";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "37228cda29411948b422fae072f57e31d3396d2ee1c9783775980ee9c9990af6";
    };
    buildInputs = [ setuptools-scm ];
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    meta = {
      description = "apipkg: namespace control and lazy-import mechanism";
      homepage = https://github.com/pytest-dev/apipkg;
      license = licenses.mit;
    };
  };

  appdirs = python.pkgs.buildPythonPackage rec {
    pname = "appdirs";
    version = "1.4.3";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "9e5896d1372858f8dd3344faf4e5014d21849c756c8d5701f78f8a103b372d92";
    };
    checkInputs = [ unittest2 ];
    checkPhase = "${python.interpreter} -m unittest discover";
    meta = {
      description = "A small Python module for determining appropriate platform-specific dirs, e.g. a \"user data dir\".";
      homepage = http://github.com/ActiveState/appdirs;
      license = licenses.mit;
    };
  };

  astroid = python.pkgs.buildPythonPackage rec {
    pname = "astroid";
    version = "2.0.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "a48b57ede295c3188ef5c84273bc2a8eadc46e4cbb001eae0d49fb5d1fabbb19";
    };
    buildInputs = [ pytest-runner ];
    propagatedBuildInputs = [ lazy-object-proxy six typed-ast wrapt ];
    meta = {
      description = "An abstract syntax tree for Python with inference support.";
      homepage = https://github.com/PyCQA/astroid;
      license = licenses.lgpl3;
    };
  };

  atomicwrites = python.pkgs.buildPythonPackage rec {
    pname = "atomicwrites";
    version = "1.1.5";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "240831ea22da9ab882b551b31d4225591e5e447a68c5e188db5b89ca1d487585";
    };
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    doCheck = false;
    meta = {
      description = "Atomic file writes.";
      homepage = https://github.com/untitaker/python-atomicwrites;
      license = licenses.mit;
    };
  };

  attrs = python.pkgs.buildPythonPackage rec {
    pname = "attrs";
    version = "18.1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e0d0eb91441a3b53dab4d9b743eafc1ac44476296a2053b6ca3af0b139faf87b";
    };
    doCheck = false;
    meta = {
      description = "Classes Without Boilerplate";
      homepage = http://www.attrs.org/;
      license = licenses.mit;
    };
  };

  babel = python.pkgs.buildPythonPackage rec {
    pname = "Babel";
    version = "2.6.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "8cba50f48c529ca3fa18cf81fa9403be176d374ac4d60738b839122dfaaa3d23";
    };
    propagatedBuildInputs = [ pytz ];
    checkInputs = [ freezegun pytest-cov ];
    checkPhase = "pytest";
    meta = {
      description = "Internationalization utilities";
      homepage = http://babel.pocoo.org/;
      license = licenses.bsdOriginal;
    };
  };

  blinker = python.pkgs.buildPythonPackage rec {
    pname = "blinker";
    version = "1.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "471aee25f3992bd325afa3772f1063dbdbbca947a041b8b89466dc00d606f8b6";
    };
    checkInputs = [ nose ];
    checkPhase = "nosetests";
    meta = {
      description = "Fast, simple object-to-object and broadcast signaling";
      homepage = http://pythonhosted.org/blinker/;
      license = licenses.mit;
    };
  };

  brotlipy = python.pkgs.buildPythonPackage rec {
    pname = "brotlipy";
    version = "0.7.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "36def0b859beaf21910157b4c33eb3b06d8ce459c942102f16988cca6ea164df";
    };
    propagatedBuildInputs = [ cffi ];
    checkInputs = [ hypothesis pytest ];
    checkPhase = "pytest";
    PYTEST_ADDOPTS = "-k 'not compression'";
    meta = {
      description = "Python binding to the Brotli library";
      homepage = https://github.com/python-hyper/brotlipy/;
      license = licenses.mit;
    };
  };

  capturer = python.pkgs.buildPythonPackage rec {
    pname = "capturer";
    version = "2.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "090142a58f3f85def3a7dd55d9024d0d1a86d1a88aaf9317c0f146244994a615";
    };
    propagatedBuildInputs = [ humanfriendly ];
    checkInputs = [ pytest-cov ];
    checkPhase = "pytest capturer/tests.py";
    meta = {
      description = "Easily capture stdout/stderr of the current process and subprocesses";
      homepage = https://capturer.readthedocs.io;
    };
  };

  certifi = python.pkgs.buildPythonPackage rec {
    pname = "certifi";
    version = "2018.4.16";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "13e698f54293db9f89122b0581843a782ad0934a4fe0172d2a980ba77fc61bb7";
    };
    doCheck = false;
    meta = {
      description = "Python package for providing Mozilla's CA Bundle.";
      homepage = http://certifi.io/;
      license = licenses.mpl20;
    };
  };

  cffi = python.pkgs.buildPythonPackage rec {
    pname = "cffi";
    version = "1.11.5";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e90f17980e6ab0f3c2f3730e56d1fe9bcba1891eeea58966e89d352492cc74f4";
    };
    propagatedBuildInputs = [ pkgs.libffi pycparser ];
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    setupPyBuildFlags = [ "--parallel $NIX_BUILD_CORES" ];
    meta = {
      description = "Foreign Function Interface for Python calling C code.";
      homepage = http://cffi.readthedocs.org;
      license = licenses.mit;
    };
  };

  chardet = python.pkgs.buildPythonPackage rec {
    pname = "chardet";
    version = "3.0.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "84ab92ed1c4d4f16916e05906b6b75a6c0fb5db821cc65e70cbd64a3e2a5eaae";
    };
    checkInputs = [ hypothesis pytest ];
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    checkPhase = "pytest";
    meta = {
      description = "Universal encoding detector for Python 2 and 3";
      homepage = https://github.com/chardet/chardet;
      license = licenses.lgpl3;
    };
  };

  click = python.pkgs.buildPythonPackage rec {
    pname = "click";
    version = "6.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "f15516df478d5a56180fbf80e68f206010e6d160fc39fa508b65e035fd75130b";
    };
    buildInputs = [ pkgs.glibcLocales ];
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    LANG = "en_US.UTF-8";
    PYTEST_ADDOPTS = "-k 'not test_legacy_callbacks'";
    meta = {
      description = "A simple wrapper around optparse for powerful command line utilities.";
      homepage = http://github.com/mitsuhiko/click;
    };
  };

  colorama = python.pkgs.buildPythonPackage rec {
    pname = "colorama";
    version = "0.3.9";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "48eb22f4f8461b1df5734a074b57042430fb06e1d61bd1e11b078c0fe6d7a1f1";
    };
    doCheck = false;
    meta = {
      description = "Cross-platform colored terminal text.";
      homepage = https://github.com/tartley/colorama;
      license = licenses.bsdOriginal;
    };
  };

  coloredlogs = python.pkgs.buildPythonPackage rec {
    pname = "coloredlogs";
    version = "10.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "b869a2dda3fa88154b9dd850e27828d8755bfab5a838a1c97fbc850c6e377c36";
    };
    propagatedBuildInputs = [ humanfriendly ];
    checkInputs = [ capturer mock pkgs.utillinux pytest-cov verboselogs ];
    checkPhase = "PATH=$out/bin:$PATH\npytest coloredlogs/tests.py";
    meta = {
      description = "Colored terminal output for Python's logging module";
      homepage = https://coloredlogs.readthedocs.io;
      license = licenses.mit;
    };
  };

  contoml = python.pkgs.buildPythonPackage rec {
    pname = "contoml";
    version = "0.32";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "2353275caef3726131c4192379252cc48eb4a15c06df3e1046f783de937eba94";
    };
    propagatedBuildInputs = [ iso8601 pytz six strict-rfc3339 timestamp ];
    doCheck = false;
    meta = {
      description = "Consistent TOML for Python";
      homepage = https://github.com/Jumpscale/python-consistent-toml;
    };
  };

  coverage = python.pkgs.buildPythonPackage rec {
    pname = "coverage";
    version = "4.5.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "56e448f051a201c5ebbaa86a5efd0ca90d327204d8b059ab25ad0f35fbfd79f1";
    };
    doCheck = false;
    setupPyBuildFlags = [ "--parallel $NIX_BUILD_CORES" ];
    meta = {
      description = "Code coverage measurement for Python";
      homepage = https://bitbucket.org/ned/coveragepy;
      license = licenses.asl20;
    };
  };

  decorator = python.pkgs.buildPythonPackage rec {
    pname = "decorator";
    version = "4.3.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "c39efa13fbdeb4506c476c9b3babf6a718da943dab7811c206005a4a956c080c";
    };
    meta = {
      description = "Better living through Python with decorators";
      homepage = https://github.com/micheles/decorator;
      license = licenses.bsd3;
    };
  };

  distlib = python.pkgs.buildPythonPackage rec {
    pname = "distlib";
    version = "0.2.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "cd502c66fc27c535bab62dc4f482e403e2369c2c05281a79cc2d4e2f42a87f20";
      extension = "zip";
    };
    doCheck = false;
    meta = {
      description = "Distribution utilities";
      homepage = https://bitbucket.org/pypa/distlib;
      license = licenses.psfl;
    };
  };

  django = python.pkgs.buildPythonPackage rec {
    pname = "Django";
    version = "2.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "7f246078d5a546f63c28fc03ce71f4d7a23677ce42109219c24c9ffb28416137";
    };
    propagatedBuildInputs = [ pytz ];
    doCheck = false;
    meta = {
      description = "A high-level Python Web framework that encourages rapid development and clean, pragmatic design.";
      homepage = https://www.djangoproject.com/;
      license = licenses.bsdOriginal;
    };
  };

  dnspython = python.pkgs.buildPythonPackage rec {
    pname = "dnspython";
    version = "1.15.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "40f563e1f7a7b80dc5a4e76ad75c23da53d62f1e15e6e517293b04e1f84ead7c";
      extension = "zip";
    };
    checkInputs = [ unittest2 ];
    patchPhase = "rm tests/test_zone.py";
    checkPhase = "${python.interpreter} -m unittest discover";
    meta = {
      description = "DNS toolkit";
      homepage = http://www.dnspython.org;
      license = licenses.bsdOriginal;
    };
  };

  docopt = python.pkgs.buildPythonPackage rec {
    pname = "docopt";
    version = "0.6.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "49b3a825280bd66b3aa83585ef59c4a8c82f2c8a522dbe754a8bc8d08c85c491";
    };
    doCheck = false;
    meta = {
      description = "Pythonic argument parser, that will make you smile";
      homepage = http://docopt.org;
      license = licenses.mit;
    };
  };

  docutils = python.pkgs.buildPythonPackage rec {
    pname = "docutils";
    version = "0.14";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "51e64ef2ebfb29cae1faa133b3710143496eca21c530f3f71424d77687764274";
    };
    checkPhase = "${python.interpreter} test3/alltests.py";
    meta = {
      description = "Docutils -- Python Documentation Utilities";
      homepage = http://docutils.sourceforge.net/;
      license = "public domain, Python, 2-Clause BSD, GPL 3 (see COPYING.txt)";
    };
  };

  dodgy = python.pkgs.buildPythonPackage rec {
    pname = "dodgy";
    version = "0.1.9";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "65e13cf878d7aff129f1461c13cb5fd1bb6dfe66bb5327e09379c3877763280c";
    };
    doCheck = false;
    meta = {
      description = "Dodgy: Searches for dodgy looking lines in Python code";
      homepage = https://github.com/landscapeio/dodgy;
      license = licenses.mit;
    };
  };

  email-validator = python.pkgs.buildPythonPackage rec {
    pname = "email_validator";
    version = "1.0.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "669eaae98d86dbd0ab62ab2f5fbc95d01cb28f8e038aa30ab165b244130949c9";
    };
    propagatedBuildInputs = [ dnspython idna ];
    doCheck = false;
    meta = {
      description = "A robust email syntax and deliverability validation library for Python 2.x/3.x.";
      homepage = https://github.com/JoshData/python-email-validator;
      license = "CC0 (copyright waived)";
    };
  };

  execnet = python.pkgs.buildPythonPackage rec {
    pname = "execnet";
    version = "1.5.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "a7a84d5fa07a089186a329528f127c9d73b9de57f1a1131b82bb5320ee651f6a";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ apipkg ];
    checkInputs = [ pytest-timeout ];
    checkPhase = "pytest testing";
    PYTEST_ADDOPTS = "-k 'not test_close_initiating_remote_no_error'";
    meta = {
      description = "execnet: rapid multi-Python deployment";
      homepage = http://codespeak.net/execnet;
      license = licenses.mit;
    };
  };

  factory-boy = python.pkgs.buildPythonPackage rec {
    pname = "factory_boy";
    version = "2.11.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "6f25cc4761ac109efd503f096e2ad99421b1159f01a29dbb917359dcd68e08ca";
    };
    propagatedBuildInputs = [ faker ];
    doCheck = false;
    meta = {
      description = "A versatile test fixtures replacement based on thoughtbot's factory_bot for Ruby.";
      homepage = https://github.com/FactoryBoy/factory_boy;
      license = licenses.mit;
    };
  };

  faker = python.pkgs.buildPythonPackage rec {
    pname = "Faker";
    version = "0.8.17";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "0e9a1227a3a0f3297a485715e72ee6eb77081b17b629367042b586e38c03c867";
    };
    propagatedBuildInputs = [ python-dateutil text-unidecode ];
    checkInputs = [ email-validator mock ukpostcodeparser ];
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    meta = {
      description = "Faker is a Python package that generates fake data for you.";
      homepage = https://github.com/joke2k/faker;
      license = licenses.mit;
    };
  };

  fancycompleter = python.pkgs.buildPythonPackage rec {
    pname = "fancycompleter";
    version = "0.8";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "d2522f1f3512371f295379c4c0d1962de06762eb586c199620a2a5d423539b12";
    };
    buildInputs = [ setuptools-scm ];
    checkInputs = [ pytest ];
    checkPhase = "pytest -v -rs";
    meta = {
      description = "colorful TAB completion for Python prompt";
      homepage = http://bitbucket.org/antocuni/fancycompleter;
      license = licenses.bsdOriginal;
    };
  };

  first = python.pkgs.buildPythonPackage rec {
    pname = "first";
    version = "2.0.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "3bb3de3582cb27071cfb514f00ed784dc444b7f96dc21e140de65fe00585c95e";
    };
    doCheck = false;
    meta = {
      description = "Return the first true value of an iterable.";
      homepage = http://github.com/hynek/first/;
      license = licenses.mit;
    };
  };

  flake8 = python.pkgs.buildPythonPackage rec {
    pname = "flake8";
    version = "3.5.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "7253265f7abd8b313e3892944044a365e3f4ac3fcdcfb4298f55ee9ddf188ba0";
    };
    buildInputs = [ pytest-runner ];
    propagatedBuildInputs = [ mccabe pycodestyle pyflakes ];
    checkInputs = [ mock ];
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    checkPhase = "pytest";
    meta = {
      description = "the modular source code checker: pep8, pyflakes and co";
      homepage = https://gitlab.com/pycqa/flake8;
      license = licenses.mit;
    };
  };

  flake8-polyfill = python.pkgs.buildPythonPackage rec {
    pname = "flake8-polyfill";
    version = "1.0.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e44b087597f6da52ec6393a709e7108b2905317d0c0b744cdca6208e670d8eda";
    };
    propagatedBuildInputs = [ flake8 ];
    checkInputs = [ mock pep8 pytest ];
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    checkPhase = "pytest";
    meta = {
      description = "Polyfill package for Flake8 plugins";
      homepage = https://gitlab.com/pycqa/flake8-polyfill;
      license = licenses.mit;
    };
  };

  flask = python.pkgs.buildPythonPackage rec {
    pname = "Flask";
    version = "1.0.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "2271c0070dbcb5275fad4a82e29f23ab92682dc45f9dfbc22c02ba9b9322ce48";
    };
    buildInputs = [ pkgs.glibcLocales ];
    propagatedBuildInputs = [ click itsdangerous jinja2 werkzeug ];
    checkInputs = [ blinker coverage greenlet pytest python-dotenv ];
    checkPhase = "pytest";
    LANG = "en_US.UTF-8";
    meta = {
      description = "A simple framework for building complex web applications.";
      homepage = https://www.palletsprojects.com/p/flask/;
      license = licenses.bsdOriginal;
    };
  };

  freezegun = python.pkgs.buildPythonPackage rec {
    pname = "freezegun";
    version = "0.3.10";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "703caac155dcaad61f78de4cb0666dca778d854dfb90b3699930adee0559a622";
    };
    propagatedBuildInputs = [ mock python-dateutil ];
    checkInputs = [ nose ];
    checkPhase = "nosetests";
    meta = {
      description = "Let your Python tests travel through time";
      homepage = https://github.com/spulec/freezegun;
      license = licenses.asl20;
    };
  };

  frosted = python.pkgs.buildPythonPackage rec {
    pname = "frosted";
    version = "1.4.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "d1e5d2b43a064b33c289b9a986a7425fd9a36bed8f519ca430ac7a0915e32b51";
    };
    propagatedBuildInputs = [ pies ];
    doCheck = false;
    meta = {
      description = "A passive Python syntax checker";
      homepage = https://github.com/timothycrosley/frosted;
      license = licenses.mit;
    };
  };

  greenlet = python.pkgs.buildPythonPackage rec {
    pname = "greenlet";
    version = "0.4.14";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "f1cc268a15ade58d9a0c04569fe6613e19b8b0345b64453064e2c3c6d79051af";
    };
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    setupPyBuildFlags = [ "--parallel $NIX_BUILD_CORES" ];
    meta = {
      description = "Lightweight in-process concurrent programming";
      homepage = https://github.com/python-greenlet/greenlet;
      license = licenses.mit;
    };
  };

  httpbin = python.pkgs.buildPythonPackage rec {
    pname = "httpbin";
    version = "0.7.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "cbb37790c91575f4f15757f42ad41d9f729eb227d5edbe89e4ec175486db8dfa";
    };
    propagatedBuildInputs = [ brotlipy decorator raven six ];
    meta = {
      description = "HTTP Request and Response Service";
      homepage = https://github.com/requests/httpbin;
      license = licenses.mit;
    };
  };

  humanfriendly = python.pkgs.buildPythonPackage rec {
    pname = "humanfriendly";
    version = "4.16.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "ed1e98ae056b597f15b41bddcc32b9f21e6ab4f3445f9faad1668675de759f7b";
    };
    doCheck = false;
    meta = {
      description = "Human friendly output for text interfaces using Python";
      homepage = https://humanfriendly.readthedocs.io;
      license = licenses.mit;
    };
  };

  hypothesis = python.pkgs.buildPythonPackage rec {
    pname = "hypothesis";
    version = "3.66.22";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "fbeed752678ef4b2069fa0cd8d087f0f32aff8c5da37bfa0e11a27e3971428c3";
    };
    propagatedBuildInputs = [ attrs coverage ];
    doCheck = false;
    meta = {
      description = "A library for property based testing";
      homepage = https://github.com/HypothesisWorks/hypothesis/tree/master/hypothesis-python;
      license = licenses.mpl20;
    };
  };

  idna = python.pkgs.buildPythonPackage rec {
    pname = "idna";
    version = "2.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "684a38a6f903c1d71d6d5fac066b58d7768af4de2b832e426ec79c30daa94a16";
    };
    meta = {
      description = "Internationalized Domain Names in Applications (IDNA)";
      homepage = https://github.com/kjd/idna;
      license = licenses.bsdOriginal;
    };
  };

  imagesize = python.pkgs.buildPythonPackage rec {
    pname = "imagesize";
    version = "1.0.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "5b326e4678b6925158ccc66a9fa3122b6106d7c876ee32d7de6ce59385b96315";
    };
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    meta = {
      description = "Getting image size from png/jpeg/jpeg2000/gif file";
      homepage = https://github.com/shibukawa/imagesize_py;
      license = licenses.mit;
    };
  };

  iso8601 = python.pkgs.buildPythonPackage rec {
    pname = "iso8601";
    version = "0.1.12";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "49c4b20e1f38aa5cf109ddcd39647ac419f928512c869dc01d5c7098eddede82";
    };
    checkInputs = [ pytest ];
    checkPhase = "pytest --verbose iso8601";
    meta = {
      description = "Simple module to parse ISO 8601 dates";
      homepage = https://bitbucket.org/micktwomey/pyiso8601;
      license = licenses.mit;
    };
  };

  isort = python.pkgs.buildPythonPackage rec {
    pname = "isort";
    version = "4.3.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "b9c40e9750f3d77e6e4d441d8b0266cf555e7cdabdcff33c4fd06366ca761ef8";
    };
    checkInputs = [ mock pytest ];
    checkPhase = python.pkgs.isort.checkPhase;
    meta = {
      description = "A Python utility / library to sort Python imports.";
      homepage = https://github.com/timothycrosley/isort;
      license = licenses.mit;
    };
  };

  itsdangerous = python.pkgs.buildPythonPackage rec {
    pname = "itsdangerous";
    version = "0.24";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "cbb3fcf8d3e33df861709ecaf89d9e6629cff0a217bc2848f1b41cd30d360519";
    };
    checkPhase = "${python.interpreter} tests.py";
    meta = {
      description = "Various helpers to pass trusted data to untrusted environments and back.";
      homepage = http://github.com/mitsuhiko/itsdangerous;
    };
  };

  jedi = python.pkgs.buildPythonPackage rec {
    pname = "jedi";
    version = "0.12.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "b409ed0f6913a701ed474a614a3bb46e6953639033e31f769ca7581da5bd1ec1";
    };
    propagatedBuildInputs = [ parso ];
    checkInputs = [ colorama docopt numpydoc pytest-cache ];
    checkPhase = "pytest jedi test";
    meta = {
      description = "An autocompletion tool for Python that can be used for text editors.";
      homepage = https://github.com/davidhalter/jedi;
      license = licenses.mit;
    };
  };

  jinja2 = python.pkgs.buildPythonPackage rec {
    pname = "Jinja2";
    version = "2.10";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "f84be1bb0040caca4cea721fcbbbbd61f9be9464ca236387158b0feea01914a4";
    };
    propagatedBuildInputs = [ markupsafe ];
    doCheck = false;
    meta = {
      description = "A small but fast and easy to use stand-alone template engine written in pure python.";
      homepage = http://jinja.pocoo.org/;
      license = licenses.bsdOriginal;
    };
  };

  lazy-object-proxy = python.pkgs.buildPythonPackage rec {
    pname = "lazy-object-proxy";
    version = "1.3.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "eb91be369f945f10d3a49f5f9be8b3d0b93a4c2be8f8a5b83b0571b8123e0a7a";
    };
    checkInputs = [ django objproxies pytest-benchmark ];
    checkPhase = "pytest -vv --ignore=src";
    setupPyBuildFlags = [ "--inplace" "--parallel $NIX_BUILD_CORES" ];
    meta = {
      description = "A fast and thorough lazy object proxy.";
      homepage = https://github.com/ionelmc/python-lazy-object-proxy;
      license = licenses.bsdOriginal;
    };
  };

  linecache2 = python.pkgs.buildPythonPackage rec {
    pname = "linecache2";
    version = "1.0.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "4b26ff4e7110db76eeb6f5a7b64a82623839d595c2038eeda662f2a2db78e97c";
    };
    buildInputs = [ pbr ];
    doCheck = false;
    meta = {
      description = "Backports of the linecache module";
      homepage = https://github.com/testing-cabal/linecache2;
    };
  };

  markupsafe = python.pkgs.buildPythonPackage rec {
    pname = "MarkupSafe";
    version = "1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "a6be69091dac236ea9c6bc7d012beab42010fa914c459791d627dad4910eb665";
    };
    meta = {
      description = "Implements a XML/HTML/XHTML Markup safe string for Python";
      homepage = http://github.com/pallets/markupsafe;
      license = licenses.bsdOriginal;
    };
  };

  mccabe = python.pkgs.buildPythonPackage rec {
    pname = "mccabe";
    version = "0.6.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "dd8d182285a0fe56bace7f45b5e7d1a6ebcbf524e8f3bd87eb0f125271b8831f";
    };
    buildInputs = [ pytest-runner ];
    meta = {
      description = "McCabe checker, plugin for flake8";
      homepage = https://github.com/pycqa/mccabe;
      license = licenses.mit;
    };
  };

  mock = python.pkgs.buildPythonPackage rec {
    pname = "mock";
    version = "2.0.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "b158b6df76edd239b8208d481dc46b6afd45a846b7812ff0ce58971cf5bc8bba";
    };
    propagatedBuildInputs = [ pbr six ];
    checkInputs = [ unittest2 ];
    checkPhase = "${python.interpreter} -m unittest discover";
    meta = {
      description = "Rolling backport of unittest.mock for all Pythons";
      homepage = https://github.com/testing-cabal/mock;
    };
  };

  more-itertools = python.pkgs.buildPythonPackage rec {
    pname = "more-itertools";
    version = "4.3.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "c476b5d3a34e12d40130bc2f935028b5f636df8f372dc2c1c01dc19681b2039e";
    };
    propagatedBuildInputs = [ six ];
    checkPhase = "${python.interpreter} -m unittest discover";
    meta = {
      description = "More routines for operating on iterables, beyond itertools";
      homepage = https://github.com/erikrose/more-itertools;
      license = licenses.mit;
    };
  };

  munch = python.pkgs.buildPythonPackage rec {
    pname = "munch";
    version = "2.3.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "6ae3d26b837feacf732fb8aa5b842130da1daf221f5af9f9d4b2a0a6414b0d51";
    };
    propagatedBuildInputs = [ six ];
    doCheck = false;
    meta = {
      description = "A dot-accessible dictionary (a la JavaScript objects).";
      homepage = http://github.com/Infinidat/munch;
      license = licenses.mit;
    };
  };

  mypy = python.pkgs.buildPythonPackage rec {
    pname = "mypy";
    version = "0.620";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "c770605a579fdd4a014e9f0a34b6c7a36ce69b08100ff728e96e27445cef3b3c";
    };
    propagatedBuildInputs = [ typed-ast ];
    doCheck = false;
    meta = {
      description = "Optional static typing for Python";
      homepage = http://www.mypy-lang.org/;
      license = licenses.mit;
    };
  };

  nose = python.pkgs.buildPythonPackage rec {
    pname = "nose";
    version = "1.3.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "f1bffef9cbc82628f6e7d7b40d7e255aefaa1adb6a1b1d26c69a8b79e6208a98";
    };
    doCheck = false;
    meta = {
      description = "nose extends unittest to make testing easier";
      homepage = http://readthedocs.org/docs/nose/;
      license = licenses.lgpl3;
    };
  };

  numpy = python.pkgs.buildPythonPackage rec {
    pname = "numpy";
    version = "1.15.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "f28e73cf18d37a413f7d5de35d024e6b98f14566a10d82100f9dc491a7d449f9";
      extension = "zip";
    };
    buildInputs = [ pkgs.blas pkgs.gfortran ];
    propagatedBuildInputs = [ pytest ];
    checkInputs = [ nose ];
    checkPhase = python.pkgs.numpy.checkPhase;
    NOSE_EXCLUDE = python.pkgs.numpy.NOSE_EXCLUDE;
    enableParallelBuilding = python.pkgs.numpy.enableParallelBuilding;
    passthru = python.pkgs.numpy.passthru;
    patches = python.pkgs.numpy.patches;
    postPatch = python.pkgs.numpy.postPatch;
    preBuild = python.pkgs.numpy.preBuild;
    preConfigure = python.pkgs.numpy.preConfigure;
  };

  numpydoc = python.pkgs.buildPythonPackage rec {
    pname = "numpydoc";
    version = "0.8.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "61f4bf030937b60daa3262e421775838c945dcdd671f37b69e8e4854c7eb5ffd";
    };
    propagatedBuildInputs = [ sphinx ];
    checkInputs = [ nose ];
    checkPhase = "nosetests";
    meta = {
      description = "Sphinx extension to support docstrings in Numpy format";
      homepage = https://numpydoc.readthedocs.io;
      license = licenses.bsdOriginal;
    };
  };

  objproxies = python.pkgs.buildPythonPackage rec {
    pname = "objproxies";
    version = "0.9.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "6d68281b3b44dbda51ee11e460b50e9d0025ea68e16e3fb192fcf9250f229426";
    };
    doCheck = false;
    meta = {
      description = "General purpose proxy and wrapper types";
      homepage = http://github.com/soulrebel/objproxies;
      license = "PSF or ZPL";
    };
  };

  packaging = python.pkgs.buildPythonPackage rec {
    pname = "packaging";
    version = "17.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "f019b770dd64e585a99714f1fd5e01c7a8f11b45635aa953fd41c689a657375b";
    };
    propagatedBuildInputs = [ pyparsing six ];
    checkInputs = [ pretend pytest ];
    checkPhase = "pytest --strict";
    meta = {
      description = "Core utilities for Python packages";
      homepage = https://github.com/pypa/packaging;
      license = "BSD or Apache License, Version 2.0";
    };
  };

  parso = python.pkgs.buildPythonPackage rec {
    pname = "parso";
    version = "0.3.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "35704a43a3c113cce4de228ddb39aab374b8004f4f2407d070b6a2ca784ce8a2";
    };
    checkInputs = [ pytest-cache ];
    checkPhase = "pytest parso test";
    meta = {
      description = "A Python Parser";
      homepage = https://github.com/davidhalter/parso;
      license = licenses.mit;
    };
  };

  pbr = python.pkgs.buildPythonPackage rec {
    pname = "pbr";
    version = "4.2.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1b8be50d938c9bb75d0eaf7eda111eec1bf6dc88a62a6412e33bf077457e0f45";
    };
    doCheck = false;
    meta = {
      description = "Python Build Reasonableness";
      homepage = https://docs.openstack.org/pbr/latest/;
    };
  };

  pdbpp = python.pkgs.buildPythonPackage rec {
    pname = "pdbpp";
    version = "0.9.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "dde77326e4ea41439c243ed065826d53539530eeabd1b6615aae15cfbb9fda05";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ fancycompleter pygments wmctrl ];
    doCheck = false;
    meta = {
      description = "pdb++, a drop-in replacement for pdb";
      homepage = http://github.com/antocuni/pdb;
      license = licenses.bsdOriginal;
    };
  };

  pep8 = python.pkgs.buildPythonPackage rec {
    pname = "pep8";
    version = "1.7.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "fe249b52e20498e59e0b5c5256aa52ee99fc295b26ec9eaa85776ffdb9fe6374";
    };
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    PYTEST_ADDOPTS = "-k 'not test_check_diff'";
    meta = {
      description = "Python style guide checker";
      homepage = http://pep8.readthedocs.org/;
      license = licenses.mit;
    };
  };

  pep8-naming = python.pkgs.buildPythonPackage rec {
    pname = "pep8-naming";
    version = "0.7.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "624258e0dd06ef32a9daf3c36cc925ff7314da7233209c5b01f7e5cdd3c34826";
    };
    propagatedBuildInputs = [ flake8-polyfill ];
    meta = {
      description = "Check PEP-8 naming conventions, plugin for flake8";
      homepage = https://github.com/PyCQA/pep8-naming;
      license = licenses.mit;
    };
  };

  pies = python.pkgs.buildPythonPackage rec {
    pname = "pies";
    version = "2.6.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e8a76923ce0e0f605240901983fe492814a65d3d803efe3013a0e1815b75e4e9";
    };
    doCheck = false;
    meta = {
      description = "The simplest way to write one program that runs on both Python 2 and Python 3.";
      homepage = https://github.com/timothycrosley/pies;
      license = licenses.mit;
    };
  };

  pip = python.pkgs.buildPythonPackage rec {
    pname = "pip";
    version = "18.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "a0e11645ee37c90b40c46d607070c4fd583e2cd46231b1c06e389c5e814eed76";
    };
    doCheck = false;
    installFlags = [ "--ignore-installed" ];
    meta = {
      description = "The PyPA recommended tool for installing Python packages.";
      homepage = https://pip.pypa.io/;
      license = licenses.mit;
    };
  };

  pipreqs = python.pkgs.buildPythonPackage rec {
    pname = "pipreqs";
    version = "0.4.9";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "cec6eecc4685967b27eb386037565a737d036045f525b9eb314631a68d60e4bc";
    };
    propagatedBuildInputs = [ docopt yarg ];
    doCheck = false;
    meta = {
      description = "Pip requirements.txt generator based on imports in project";
      homepage = https://github.com/bndr/pipreqs;
      license = "Apache License";
    };
  };

  pluggy = python.pkgs.buildPythonPackage rec {
    pname = "pluggy";
    version = "0.7.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "95eb8364a4708392bae89035f45341871286a333f749c3141c20573d2b3876e1";
    };
    buildInputs = [ setuptools-scm ];
    doCheck = false;
    meta = {
      description = "plugin and hook calling mechanisms for python";
      homepage = https://github.com/pytest-dev/pluggy;
      license = licenses.mit;
    };
  };

  pretend = python.pkgs.buildPythonPackage rec {
    pname = "pretend";
    version = "1.0.9";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "c90eb810cde8ebb06dafcb8796f9a95228ce796531bc806e794c2f4649aa1b10";
    };
    doCheck = false;
    meta = {
      description = "A library for stubbing in Python";
      homepage = https://github.com/alex/pretend;
      license = licenses.bsdOriginal;
    };
  };

  prompt-toolkit = python.pkgs.buildPythonPackage rec {
    pname = "prompt_toolkit";
    version = "1.0.15";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "858588f1983ca497f1cf4ffde01d978a3ea02b01c8a26a8bbc5cd2e66d816917";
    };
    propagatedBuildInputs = [ six wcwidth ];
    checkInputs = [ pytest ];
    patchPhase = "rm prompt_toolkit/win32_types.py";
    checkPhase = "pytest";
    PYTEST_ADDOPTS = "-k 'not test_pathcompleter_can_expanduser'";
    meta = {
      description = "Library for building powerful interactive command lines in Python";
      homepage = https://github.com/jonathanslenders/python-prompt-toolkit;
    };
  };

  property-manager = python.pkgs.buildPythonPackage rec {
    pname = "property-manager";
    version = "2.3.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "19e1f230f95691ae74123fa43c6928d0f0cc464e841d6375941cda4a0585162f";
    };
    propagatedBuildInputs = [ humanfriendly verboselogs ];
    checkInputs = [ coloredlogs pytest-cov ];
    checkPhase = "pytest property_manager/tests.py";
    meta = {
      description = "Useful property variants for Python programming (required properties, writable properties, cached properties, etc)";
      homepage = https://property-manager.readthedocs.org;
      license = licenses.mit;
    };
  };

  prospector = python.pkgs.buildPythonPackage rec {
    pname = "prospector";
    version = "1.1.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e2e62b656cca5610d397d7dfe76288e9284283be1b551e0495dd6a823390db65";
    };
    propagatedBuildInputs = [
      dodgy
      frosted
      mypy
      pep8-naming
      pydocstyle
      pylint-plugin-utils
      pyroma
      pyyaml
      requirements-detector
      setoptconf
      vulture
    ];
    doCheck = false;
    meta = {
      description = "Prospector: python static analysis tool";
      homepage = http://prospector.readthedocs.io;
      license = licenses.gpl2;
    };
  };

  ptpython = python.pkgs.buildPythonPackage rec {
    pname = "ptpython";
    version = "0.41";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "a78b27a85c5dbe9d89376e7f3aa70a9d8fa15cb45ee5f73a3cc3963b9b528ac1";
    };
    propagatedBuildInputs = [ docopt jedi prompt-toolkit pygments ];
    doCheck = false;
    meta = {
      description = "Python REPL build on top of prompt_toolkit";
      homepage = https://github.com/jonathanslenders/ptpython;
    };
  };

  py = python.pkgs.buildPythonPackage rec {
    pname = "py";
    version = "1.5.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "3fd59af7435864e1a243790d322d763925431213b6b8529c6ca71081ace3bbf7";
    };
    buildInputs = [ setuptools-scm ];
    doCheck = false;
    meta = {
      description = "library with cross-python path, ini-parsing, io, code, log facilities";
      homepage = http://py.readthedocs.io/;
      license = licenses.mit;
    };
  };

  py-cpuinfo = python.pkgs.buildPythonPackage rec {
    pname = "py-cpuinfo";
    version = "4.0.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "6615d4527118d4ea1db4d86dac4340725b3906aa04bf36b7902f7af4425fb25f";
    };
    meta = {
      description = "Get CPU info with pure Python 2 & 3";
      homepage = https://github.com/workhorsy/py-cpuinfo;
      license = licenses.mit;
    };
  };

  pycodestyle = python.pkgs.buildPythonPackage rec {
    pname = "pycodestyle";
    version = "2.3.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "682256a5b318149ca0d2a9185d365d8864a768a28db66a84a2ea946bcc426766";
    };
    meta = {
      description = "Python style guide checker";
      homepage = https://pycodestyle.readthedocs.io/;
      license = licenses.mit;
    };
  };

  pycparser = python.pkgs.buildPythonPackage rec {
    pname = "pycparser";
    version = "2.18";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "99a8ca03e29851d96616ad0404b4aad7d9ee16f25c9f9708a11faf2810f7b226";
    };
    checkInputs = [ pytest ];
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    checkPhase = "pytest";
    meta = {
      description = "C parser in Python";
      homepage = https://github.com/eliben/pycparser;
      license = licenses.bsdOriginal;
    };
  };

  pydocstyle = python.pkgs.buildPythonPackage rec {
    pname = "pydocstyle";
    version = "2.1.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "4d5bcde961107873bae621f3d580c3e35a426d3687ffc6f8fb356f6628da5a97";
    };
    propagatedBuildInputs = [ six snowballstemmer ];
    doCheck = false;
    meta = {
      description = "Python docstring style checker";
      homepage = https://github.com/PyCQA/pydocstyle/;
      license = licenses.mit;
    };
  };

  pyflakes = python.pkgs.buildPythonPackage rec {
    pname = "pyflakes";
    version = "1.6.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "8d616a382f243dbf19b54743f280b80198be0bca3a5396f1d2e1fca6223e8805";
    };
    meta = {
      description = "passive checker of Python programs";
      homepage = https://github.com/PyCQA/pyflakes;
      license = licenses.mit;
    };
  };

  pygments = python.pkgs.buildPythonPackage rec {
    pname = "Pygments";
    version = "2.2.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "dbae1046def0efb574852fab9e90209b23f556367b5a320c0bcb871c77c3e8cc";
    };
    doCheck = false;
    meta = {
      description = "Pygments is a syntax highlighting package written in Python.";
      homepage = http://pygments.org/;
      license = licenses.bsdOriginal;
    };
  };

  pylint = python.pkgs.buildPythonPackage rec {
    pname = "pylint";
    version = "2.1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "0edfec21270725c5aa8e8d8d06ef5666f766e0e748ed2f1ab23624727303b935";
    };
    buildInputs = [ pytest-runner ];
    propagatedBuildInputs = [ astroid isort mccabe ];
    doCheck = false;
    meta = {
      description = "python code static checker";
      homepage = https://github.com/PyCQA/pylint;
      license = licenses.gpl3;
    };
  };

  pylint-plugin-utils = python.pkgs.buildPythonPackage rec {
    pname = "pylint-plugin-utils";
    version = "0.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "8ad25a82bcce390d1d6b7c006c123e0cb18051839c9df7b8bdb7823c53fe676e";
    };
    propagatedBuildInputs = [ pylint ];
    doCheck = false;
    meta = {
      description = "Utilities and helpers for writing Pylint plugins";
      homepage = https://github.com/landscapeio/pylint-plugin-utils;
      license = licenses.gpl2;
    };
  };

  pyparsing = python.pkgs.buildPythonPackage rec {
    pname = "pyparsing";
    version = "2.2.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "0832bcf47acd283788593e7a0f542407bd9550a55a8a8435214a1960e04bcb04";
    };
    doCheck = false;
    meta = {
      description = "Python parsing module";
      homepage = http://pyparsing.wikispaces.com/;
      license = licenses.mit;
    };
  };

  pyroma = python.pkgs.buildPythonPackage rec {
    pname = "pyroma";
    version = "2.3.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "664faca7691a372360cd6ecf04d459c1b7c221013d8e965e0ae83f82a07b57a7";
    };
    propagatedBuildInputs = [ docutils ];
    meta = {
      description = "Test your project's packaging friendliness";
      homepage = https://github.com/regebro/pyroma;
      license = licenses.mit;
    };
  };

  pysocks = python.pkgs.buildPythonPackage rec {
    pname = "PySocks";
    version = "1.6.8";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "3fe52c55890a248676fd69dc9e3c4e811718b777834bcaab7a8125cf9deac672";
    };
    doCheck = false;
    meta = {
      description = "A Python SOCKS client module. See https://github.com/Anorov/PySocks for more information.";
      homepage = https://github.com/Anorov/PySocks;
      license = licenses.bsdOriginal;
    };
  };

  pytest = python.pkgs.buildPythonPackage rec {
    pname = "pytest";
    version = "3.7.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "8214ab8446104a1d0c17fbd218ec6aac743236c6ffbe23abc038e40213c60b88";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ atomicwrites attrs more-itertools pluggy py ];
    checkInputs = [ hypothesis mock nose ];
    patchPhase = "rm testing/test_argcomplete.py";
    checkPhase = "pytest --lsof -ra testing";
    preBuild = "PATH=$out/bin:$PATH";
    meta = {
      description = "pytest: simple powerful testing with Python";
      homepage = http://pytest.org;
      license = licenses.mit;
    };
  };

  pytest-benchmark = python.pkgs.buildPythonPackage rec {
    pname = "pytest-benchmark";
    version = "3.1.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "185526b10b7cf1804cb0f32ac0653561ef2f233c6e50a9b3d8066a9757e36480";
    };
    propagatedBuildInputs = [ py-cpuinfo pytest ];
    doCheck = false;
    meta = {
      description = "A ``py.test`` fixture for benchmarking code. It will group the tests into rounds that are calibrated to the chosen timer. See calibration_ and FAQ_.";
      homepage = https://github.com/ionelmc/pytest-benchmark;
      license = licenses.bsdOriginal;
    };
  };

  pytest-cache = python.pkgs.buildPythonPackage rec {
    pname = "pytest-cache";
    version = "1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "be7468edd4d3d83f1e844959fd6e3fd28e77a481440a7118d430130ea31b07a9";
    };
    propagatedBuildInputs = [ execnet pytest ];
    doCheck = false;
    meta = {
      description = "pytest plugin with mechanisms for caching across test runs";
      homepage = http://bitbucket.org/hpk42/pytest-cache/;
    };
  };

  pytest-cov = python.pkgs.buildPythonPackage rec {
    pname = "pytest-cov";
    version = "2.5.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "03aa752cf11db41d281ea1d807d954c4eda35cfa1b21d6971966cc041bbf6e2d";
    };
    propagatedBuildInputs = [ coverage pytest ];
    doCheck = false;
    meta = {
      description = "Pytest plugin for measuring coverage.";
      homepage = https://github.com/pytest-dev/pytest-cov;
      license = licenses.mit;
    };
  };

  pytest-forked = python.pkgs.buildPythonPackage rec {
    pname = "pytest-forked";
    version = "0.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e4500cd0509ec4a26535f7d4112a8cc0f17d3a41c29ffd4eab479d2a55b30805";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ pytest ];
    patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
    checkPhase = "pytest";
    meta = {
      description = "run tests in isolated forked subprocesses";
      homepage = https://github.com/pytest-dev/pytest-forked;
      license = licenses.mit;
    };
  };

  pytest-httpbin = python.pkgs.buildPythonPackage rec {
    pname = "pytest-httpbin";
    version = "0.3.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "8cd57e27418a7d7d205fcc9802eea246ed06170e3065abfa76c6d9b40553592c";
    };
    propagatedBuildInputs = [ httpbin ];
    doCheck = false;
    meta = {
      description = "Easily test your HTTP library against a local copy of httpbin";
      homepage = https://github.com/kevin1024/pytest-httpbin;
      license = licenses.mit;
    };
  };

  pytest-mock = python.pkgs.buildPythonPackage rec {
    pname = "pytest-mock";
    version = "1.10.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "d89a8209d722b8307b5e351496830d5cc5e192336003a485443ae9adeb7dd4c0";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ pytest ];
    doCheck = false;
    meta = {
      description = "Thin-wrapper around the mock package for easier use with py.test";
      homepage = https://github.com/pytest-dev/pytest-mock/;
      license = licenses.mit;
    };
  };

  pytest-randomly = python.pkgs.buildPythonPackage rec {
    pname = "pytest-randomly";
    version = "1.2.3";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "92ec6745d3ebdd690ecb598648748c9601f16f5afacf83ccef2b50d23e6edb7f";
    };
    propagatedBuildInputs = [ pytest ];
    checkInputs = [ factory-boy numpy ];
    checkPhase = "pytest";
    meta = {
      description = "Pytest plugin to randomly order tests and control random.seed.";
      homepage = https://github.com/adamchainz/pytest-randomly;
      license = licenses.bsdOriginal;
    };
  };

  pytest-runner = python.pkgs.buildPythonPackage rec {
    pname = "pytest-runner";
    version = "4.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "d23f117be39919f00dd91bffeb4f15e031ec797501b717a245e377aee0f577be";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ pytest ];
    patchPhase = "sed -i 's/setuptools_scm>=1.15.0/setuptools_scm/' setup.py";
    doCheck = false;
    meta = {
      description = "Invoke py.test as distutils command with dependency resolution";
      homepage = https://github.com/pytest-dev/pytest-runner;
    };
  };

  pytest-sugar = python.pkgs.buildPythonPackage rec {
    pname = "pytest-sugar";
    version = "0.9.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "ab8cc42faf121344a4e9b13f39a51257f26f410e416c52ea11078cdd00d98a2c";
    };
    propagatedBuildInputs = [ pytest termcolor ];
    doCheck = false;
    meta = {
      description = "py.test is a plugin for py.test that changes the default look and feel of py.test (e.g. progressbar, show tests that fail instantly).";
      homepage = http://pivotfinland.com/pytest-sugar/;
      license = licenses.bsdOriginal;
    };
  };

  pytest-timeout = python.pkgs.buildPythonPackage rec {
    pname = "pytest-timeout";
    version = "1.3.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "4b261bec5782b603c98b4bb803484bc96bf1cdcb5480dae0999d21c7e0423a23";
    };
    buildInputs = [ pkgs.glibcLocales ];
    propagatedBuildInputs = [ pytest ];
    LANG = "en_US.UTF-8";
    doCheck = false;
    meta = {
      description = "py.test plugin to abort hanging tests";
      homepage = http://bitbucket.org/pytest-dev/pytest-timeout/;
      license = licenses.mit;
    };
  };

  pytest-xdist = python.pkgs.buildPythonPackage rec {
    pname = "pytest-xdist";
    version = "1.22.5";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "3308c4f6221670432d01e0b393b333d77c1fd805532e1d64450e8140855eb51b";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ execnet pytest-forked ];
    checkPhase = "pytest";
    PYTEST_ADDOPTS = "-k 'not test_distribution_rsyncdirs_example and not test_init_rsync_roots and not test_looponfail_removed_test and not test_popen_rsync_subdir and not test_rsync_popen_with_path and not test_rsyncignore'";
    meta = {
      description = "pytest xdist plugin for distributed testing and loop-on-failing modes";
      homepage = https://github.com/pytest-dev/pytest-xdist;
      license = licenses.mit;
    };
  };

  python-dateutil = python.pkgs.buildPythonPackage rec {
    pname = "python-dateutil";
    version = "2.7.3";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e27001de32f627c22380a688bcc43ce83504a7bc5da472209b4c70f02829f0b8";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ six ];
    doCheck = false;
    meta = {
      description = "Extensions to the standard Python datetime module";
      homepage = https://dateutil.readthedocs.io;
      license = "Dual License";
    };
  };

  python-dotenv = python.pkgs.buildPythonPackage rec {
    pname = "python-dotenv";
    version = "0.9.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "38f22d75f1180256e60c8b06aa06f5254479c1bf5947430c97e3d737d90e8731";
    };
    doCheck = false;
    meta = {
      description = "Add .env support to your django/flask apps in development and deployments";
      homepage = http://github.com/theskumar/python-dotenv;
    };
  };

  pytoml = python.pkgs.buildPythonPackage rec {
    pname = "pytoml";
    version = "0.1.18";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "dae3c4e31d09eb06a6076d671f2281ee5d2c43cbeae16599c3af20881bb818ac";
    };
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    meta = {
      description = "A parser for TOML-0.4.0";
      homepage = https://github.com/avakar/pytoml;
      license = licenses.mit;
    };
  };

  pytz = python.pkgs.buildPythonPackage rec {
    pname = "pytz";
    version = "2018.5";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "ffb9ef1de172603304d9d2819af6f5ece76f2e85ec10692a524dd876e72bf277";
    };
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    meta = {
      description = "World timezone definitions, modern and historical";
      homepage = http://pythonhosted.org/pytz;
      license = licenses.mit;
    };
  };

  pyyaml = python.pkgs.buildPythonPackage rec {
    pname = "PyYAML";
    version = "3.13";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "3ef3092145e9b70e3ddd2c7ad59bdd0252a94dfe3949721633e41344de00a6bf";
    };
    buildInputs = [ pkgs.libyaml ];
    setupPyBuildFlags = [ "--parallel $NIX_BUILD_CORES" ];
    meta = {
      description = "YAML parser and emitter for Python";
      homepage = http://pyyaml.org/wiki/PyYAML;
      license = licenses.mit;
    };
  };

  raven = python.pkgs.buildPythonPackage rec {
    pname = "raven";
    version = "6.9.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "3fd787d19ebb49919268f06f19310e8112d619ef364f7989246fc8753d469888";
    };
    propagatedBuildInputs = [ blinker flask ];
    patchPhase = "sed -Ei \"s/[=<>,]+[0-9\.]+'/'/g\" setup.py";
    doCheck = false;
    meta = {
      description = "Raven is a client for Sentry (https://getsentry.com)";
      homepage = https://github.com/getsentry/raven-python;
      license = licenses.bsdOriginal;
    };
  };

  requests = python.pkgs.buildPythonPackage rec {
    pname = "requests";
    version = "2.19.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "ec22d826a36ed72a7358ff3fe56cbd4ba69dd7a6718ffd450ff0e9df7a47ce6a";
    };
    propagatedBuildInputs = [ certifi chardet idna urllib3 ];
    checkInputs = [
      pysocks
      pytest-cov
      pytest-httpbin
      pytest-mock
      pytest-xdist
    ];
    checkPhase = ''
      PYTEST_ADDOPTS="$PYTEST_ADDOPTS -n$NIX_BUILD_CORES"
      pytest
    '';
    PYTEST_ADDOPTS = "-k 'not test_POSTBIN and not test_conflicting_post_params and not test_connect_timeout and not test_total_timeout_connect'";
    meta = {
      description = "Python HTTP for Humans.";
      homepage = http://python-requests.org;
      license = licenses.asl20;
    };
  };

  requirements-detector = python.pkgs.buildPythonPackage rec {
    pname = "requirements-detector";
    version = "0.6";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "9fbc4b24e8b7c3663aff32e3eba34596848c6b91bd425079b386973bd8d08931";
    };
    propagatedBuildInputs = [ astroid ];
    doCheck = false;
    meta = {
      description = "Python tool to find and list requirements of a Python project";
      homepage = https://github.com/landscapeio/requirements-detector;
      license = licenses.mit;
    };
  };

  requirements-parser = python.pkgs.buildPythonPackage rec {
    pname = "requirements-parser";
    version = "0.2.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "5963ee895c2d05ae9f58d3fc641082fb38021618979d6a152b6b1398bd7d4ed4";
    };
    doCheck = false;
    meta = {
      description = "Parses Pip requirement files";
      homepage = https://github.com/davidfischer/requirements-parser;
      license = licenses.bsdOriginal;
    };
  };

  requirementslib = python.pkgs.buildPythonPackage rec {
    pname = "requirementslib";
    version = "1.0.11";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "87cd1197cc4b880d710eacbc4fb11fd0564187a1d965382e66cbaa2a1b08744f";
    };
    propagatedBuildInputs = [
      attrs
      contoml
      distlib
      first
      packaging
      pip
      requirements-parser
      toml
    ];
    doCheck = false;
    meta = {
      description = "A tool for converting between pip-style and pipfile requirements.";
      homepage = https://github.com/sarugaku/requirementslib;
      license = licenses.mit;
    };
  };

  setoptconf = python.pkgs.buildPythonPackage rec {
    pname = "setoptconf";
    version = "0.2.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "5b0b5d8e0077713f5d5152d4f63be6f048d9a1bb66be15d089a11c898c3cf49c";
    };
    doCheck = false;
    meta = {
      description = "A module for retrieving program settings from various sources in a consistant method.";
      homepage = https://github.com/jayclassless/setoptconf;
      license = licenses.mit;
    };
  };

  setuptools-scm = python.pkgs.buildPythonPackage rec {
    pname = "setuptools_scm";
    version = "3.0.6";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "a9cd4250443f96947c35e4790513fc008b7cc91c1475b8b523e7c7dd69766437";
    };
    propagatedBuildInputs = [ pkgs.gitMinimal ];
    doCheck = false;
    meta = {
      description = "the blessed package to manage your versions by scm tags";
      homepage = https://github.com/pypa/setuptools_scm/;
      license = licenses.mit;
    };
  };

  six = python.pkgs.buildPythonPackage rec {
    pname = "six";
    version = "1.11.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "70e8a77beed4562e7f14fe23a786b54f6296e34344c23bc42f07b15018ff98e9";
    };
    doCheck = false;
    meta = {
      description = "Python 2 and 3 compatibility utilities";
      homepage = http://pypi.python.org/pypi/six/;
      license = licenses.mit;
    };
  };

  snowballstemmer = python.pkgs.buildPythonPackage rec {
    pname = "snowballstemmer";
    version = "1.2.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "919f26a68b2c17a7634da993d91339e288964f93c274f1343e3bbbe2096e1128";
    };
    doCheck = false;
    meta = {
      description = "This package provides 16 stemmer algorithms (15 + Poerter English stemmer) generated from Snowball algorithms.";
      homepage = https://github.com/shibukawa/snowball_py;
      license = licenses.bsdOriginal;
    };
  };

  sphinx = python.pkgs.buildPythonPackage rec {
    pname = "Sphinx";
    version = "1.7.6";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "217ad9ece2156ed9f8af12b5d2c82a499ddf2c70a33c5f81864a08d8c67b9efc";
    };
    propagatedBuildInputs = [
      alabaster
      babel
      docutils
      imagesize
      jinja2
      packaging
      pygments
      requests
      snowballstemmer
      sphinxcontrib-websupport
    ];
    doCheck = false;
    meta = {
      description = "Python documentation generator";
      homepage = http://sphinx-doc.org/;
      license = licenses.bsdOriginal;
    };
  };

  sphinxcontrib-websupport = python.pkgs.buildPythonPackage rec {
    pname = "sphinxcontrib-websupport";
    version = "1.1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "9de47f375baf1ea07cdb3436ff39d7a9c76042c10a769c52353ec46e4e8fc3b9";
    };
    doCheck = false;
    meta = {
      description = "Sphinx API for Web Apps";
      homepage = http://sphinx-doc.org/;
      license = licenses.bsdOriginal;
    };
  };

  strict-rfc3339 = python.pkgs.buildPythonPackage rec {
    pname = "strict-rfc3339";
    version = "0.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "5cad17bedfc3af57b399db0fed32771f18fc54bbd917e85546088607ac5e1277";
    };
    doCheck = false;
    meta = {
      description = "Strict, simple, lightweight RFC3339 functions";
      homepage = http://www.danielrichman.co.uk/libraries/strict-rfc3339.html;
      license = "GNU General Public License Version 3";
    };
  };

  termcolor = python.pkgs.buildPythonPackage rec {
    pname = "termcolor";
    version = "1.1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1d6d69ce66211143803fbc56652b41d73b4a400a2891d7bf7a1cdf4c02de613b";
    };
    doCheck = false;
    meta = {
      description = "ANSII Color formatting for output in terminal.";
      homepage = http://pypi.python.org/pypi/termcolor;
      license = licenses.mit;
    };
  };

  text-unidecode = python.pkgs.buildPythonPackage rec {
    pname = "text-unidecode";
    version = "1.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "5a1375bb2ba7968740508ae38d92e1f889a0832913cb1c447d5e2046061a396d";
    };
    checkInputs = [ pytest ];
    checkPhase = "pytest";
    meta = {
      description = "The most basic Text::Unidecode port";
      homepage = https://github.com/kmike/text-unidecode/;
      license = "Artistic License";
    };
  };

  timestamp = python.pkgs.buildPythonPackage rec {
    pname = "timestamp";
    version = "0.0.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "b5c7a4539f0d8742b7d6c78febd241ab24903c73c38045690725220ca7eae4ac";
    };
    doCheck = false;
    meta = {
      description = "shortcut for converting datetime to timestamp";
      homepage = http://github.com/jarvys/timestamp;
    };
  };

  toml = python.pkgs.buildPythonPackage rec {
    pname = "toml";
    version = "0.9.4";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "8e86bd6ce8cc11b9620cb637466453d94f5d57ad86f17e98a98d1f73e3baab2d";
    };
    doCheck = false;
    meta = {
      description = "Python Library for Tom's Obvious, Minimal Language";
      homepage = https://github.com/uiri/toml;
      license = "License :: OSI Approved :: MIT License";
    };
  };

  tox = python.pkgs.buildPythonPackage rec {
    pname = "tox";
    version = "3.1.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "9f0cbcc36e08c2c4ae90d02d3d1f9a62231f974bcbc1df85e8045946d8261059";
    };
    buildInputs = [ setuptools-scm ];
    propagatedBuildInputs = [ packaging pluggy py virtualenv ];
    checkInputs = [
      pytest-cov
      pytest-mock
      pytest-randomly
      pytest-timeout
      pytest-xdist
    ];
    patchPhase = "rm tests/test_z_cmdline.py";
    checkPhase = ''
      PYTEST_ADDOPTS="$PYTEST_ADDOPTS -n$NIX_BUILD_CORES"
      pytest --timeout=180 . -n auto
    '';
    PYTEST_ADDOPTS = "-k 'not test_env_variables_added_to_pcall and not test_make_sdist'";
    meta = {
      description = "virtualenv-based automation of test activities";
      homepage = https://tox.readthedocs.org/;
      license = "http://opensource.org/licenses/MIT";
    };
  };

  traceback2 = python.pkgs.buildPythonPackage rec {
    pname = "traceback2";
    version = "1.4.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "05acc67a09980c2ecfedd3423f7ae0104839eccb55fc645773e1caa0951c3030";
    };
    buildInputs = [ pbr ];
    propagatedBuildInputs = [ linecache2 ];
    doCheck = false;
    meta = {
      description = "Backports of the traceback module";
      homepage = https://github.com/testing-cabal/traceback2;
    };
  };

  typed-ast = python.pkgs.buildPythonPackage rec {
    pname = "typed-ast";
    version = "1.1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "57fe287f0cdd9ceaf69e7b71a2e94a24b5d268b35df251a88fef5cc241bf73aa";
    };
    doCheck = false;
    setupPyBuildFlags = [ "--parallel $NIX_BUILD_CORES" ];
    meta = {
      description = "a fork of Python 2 and 3 ast modules with type comment support";
      homepage = https://github.com/python/typed_ast;
      license = licenses.asl20;
    };
  };

  ukpostcodeparser = python.pkgs.buildPythonPackage rec {
    pname = "UkPostcodeParser";
    version = "1.1.2";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "930264efa293db80af0103a4fe9c161b06365598d24bb6fe5403f3f57c70530e";
    };
    doCheck = false;
    meta = {
      description = "UK Postcode parser";
      homepage = https://github.com/hamstah/ukpostcodeparser;
      license = licenses.mit;
    };
  };

  unittest2 = python.pkgs.buildPythonPackage rec {
    pname = "unittest2";
    version = "1.1.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "22882a0e418c284e1f718a822b3b022944d53d2d908e1690b319a9d3eb2c0579";
    };
    propagatedBuildInputs = [ six traceback2 ];
    doCheck = false;
    postPatch = python.pkgs.unittest2.postPatch;
    meta = {
      description = "The new features in unittest backported to Python 2.4+.";
      homepage = http://pypi.python.org/pypi/unittest2;
    };
  };

  urllib3 = python.pkgs.buildPythonPackage rec {
    pname = "urllib3";
    version = "1.23";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "a68ac5e15e76e7e5dd2b8f94007233e01effe3e50e8daddf69acfd81cb686baf";
    };
    doCheck = false;
    meta = {
      description = "HTTP library with thread-safe connection pooling, file post, and more.";
      homepage = https://urllib3.readthedocs.io/;
      license = licenses.mit;
    };
  };

  verboselogs = python.pkgs.buildPythonPackage rec {
    pname = "verboselogs";
    version = "1.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "e33ddedcdfdafcb3a174701150430b11b46ceb64c2a9a26198c76a156568e427";
    };
    doCheck = false;
    meta = {
      description = "Verbose logging level for Python's logging module";
      homepage = https://verboselogs.readthedocs.io;
    };
  };

  virtualenv = python.pkgs.buildPythonPackage rec {
    pname = "virtualenv";
    version = "16.0.0";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "ca07b4c0b54e14a91af9f34d0919790b016923d157afda5efdde55c96718f752";
    };
    doCheck = false;
    meta = {
      description = "Virtual Python Environment builder";
      homepage = https://virtualenv.pypa.io/;
      license = licenses.mit;
    };
  };

  vulture = python.pkgs.buildPythonPackage rec {
    pname = "vulture";
    version = "0.24";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "23d837cf619c3bb75f87bc498c79cd4f27f0c54031ca88a9e05606c9dd627fef";
    };
    checkInputs = [ pytest-cov ];
    checkPhase = "pytest";
    meta = {
      description = "Find dead code";
      homepage = https://github.com/jendrikseipp/vulture;
      license = licenses.mit;
    };
  };

  wcwidth = python.pkgs.buildPythonPackage rec {
    pname = "wcwidth";
    version = "0.1.7";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "3df37372226d6e63e1b1e1eda15c594bca98a22d33a23832a90998faa96bc65e";
    };
    meta = {
      description = "Measures number of Terminal column cells of wide-character codes";
      homepage = https://github.com/jquast/wcwidth;
      license = licenses.mit;
    };
  };

  werkzeug = python.pkgs.buildPythonPackage rec {
    pname = "Werkzeug";
    version = "0.14.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "c3fd7a7d41976d9f44db327260e263132466836cef6f91512889ed60ad26557c";
    };
    doCheck = false;
    meta = {
      description = "The comprehensive WSGI web application library.";
      homepage = https://www.palletsprojects.org/p/werkzeug/;
      license = licenses.bsdOriginal;
    };
  };

  wmctrl = python.pkgs.buildPythonPackage rec {
    pname = "wmctrl";
    version = "0.3";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "d806f65ac1554366b6e31d29d7be2e8893996c0acbb2824bbf2b1f49cf628a13";
    };
    meta = {
      description = "A tool to programmatically control windows inside X";
      homepage = http://bitbucket.org/antocuni/wmctrl;
      license = licenses.bsdOriginal;
    };
  };

  wrapt = python.pkgs.buildPythonPackage rec {
    pname = "wrapt";
    version = "1.10.11";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "d4d560d479f2c21e1b5443bbd15fe7ec4b37fe7e53d335d3b9b0a7b1226fe3c6";
    };
    doCheck = false;
    setupPyBuildFlags = [ "--parallel $NIX_BUILD_CORES" ];
    meta = {
      description = "Module for decorators, wrappers and monkey patching.";
      homepage = https://github.com/GrahamDumpleton/wrapt;
      license = licenses.bsdOriginal;
    };
  };

  yarg = python.pkgs.buildPythonPackage rec {
    pname = "yarg";
    version = "0.1.9";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "55695bf4d1e3e7f756496c36a69ba32c40d18f821e38f61d028f6049e5e15911";
    };
    propagatedBuildInputs = [ requests ];
    doCheck = false;
    meta = {
      description = "A semi hard Cornish cheese, also queries PyPI (PyPI client)";
      homepage = https://yarg.readthedocs.org/;
      license = licenses.mit;
    };
  };

};
python.pkgs.buildPythonPackage rec {
  pname = "distinfo";
  version = "0.3.0.dev0";
  src = nix-gitignore.gitignoreSource ./.;
  buildInputs = [
    pdbpp
    pkgs.glibcLocales
    prospector
    pytest-runner
    pytest-sugar
  ];
  propagatedBuildInputs = [
    appdirs
    click
    coloredlogs
    munch
    pipreqs
    property-manager
    ptpython
    pytoml
    pyyaml
    requirementslib
    tox
  ];
  checkInputs = [ pytest-cov ];
  patchPhase = "find . -type d -name __pycache__ -depth -exec rm -rf {} ';'";
  checkPhase = "pytest && cp coverage.xml $out";
  LANG = "en_US.UTF-8";
  meta = {
    description = "Extract metadata, including full dependencies, from source distributions";
    homepage = https://github.com/0compute/distinfo;
    license = "GPL-3.0-or-later";
  };
}
# nixipy 0.0.0 on python 3.6.5
# argv: nixipy --color --build-extra=dev --directory=../distinfo
