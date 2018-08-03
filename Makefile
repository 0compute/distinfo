SHELL = bash -eu -o pipefail

override MAKEFLAGS += --no-builtin-rules --warn-undefined-variables

.DELETE_ON_ERROR:

ARGS ?=

.PHONY: result
result:
	nix-build --show-trace

.PHONY: push
push: result
	cachix push distinfo $<

EGG_INFO = distinfo.egg-info
$(EGG_INFO):
	python setup.py egg_info

.PHONY: test
test: $(EGG_INFO)
	pytest $(ARGS)

.PHONY: utest
utest: override ARGS += -k unit --ignore=tests/functional
utest: test

.PHONY: ftest
ftest: override ARGS += -k functional --ignore=tests/unit
ftest: test

.PHONY: lint
lint:
	prospector --with-tool=mccabe --with-tool=pyroma --with-tool=vulture $(ARGS)

ifdef TRAVIS

define NIX_CONF
cores = $(shell nproc)
max-jobs = $(shell nproc)
sandbox = true
substituters = https://cache.nixos.org https://cachix.cachix.org https://distinfo.cachix.org
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= cachix.cachix.org-1:eWNHQldwUO7G2VkjpnjDbWwy4KQ/HNxht7H4SSoMckM= distinfo.cachix.org-1:nj8IiFYM7vGOYIvh/KZW/DJ7VezbcNep0R4cPNr6lls=
endef
export NIX_CONF

.PHONY: travis-install
travis-install:
	sudo mkdir -p /etc/nix
	echo "$$NIX_CONF" | sudo tee /etc/nix/nix.conf
	nix-env --install --file https://github.com/cachix/cachix/tarball/v0.1.0.2
	sudo pip install codacy-coverage

.PHONY: travis-success
travis-success: push
	python-codacy-coverage -r result/coverage.xml

endif
