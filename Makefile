include .pyproject/Makefile

$(eval $(call TEST,ptest,packages))

NUM_PROCESSES ?= logical

.atest .ptest: override ARGS += --numprocesses=$(NUM_PROCESSES)

.utest .ftest: export DISTINFO_RAISE_ON_HIT=0

FLAKE_MAX_MINUTES ?= 5

atest: override ARGS += -x --flake-finder --flake-max-minutes=$(FLAKE_MAX_MINUTES)

.PHONY: push
push:
	nix-shell --packages cachix --run "nix-build | cachix push distinfo"
