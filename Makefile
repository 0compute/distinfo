include .skel/Makefile

utest ftest: export DISTINFO_RAISE_ON_HIT=0

$(eval $(call TEST,ptest,acceptance/test_packages.py))

NUM_PROCESSES ?= logical

atest ptest: override ARGS += --numprocesses=$(NUM_PROCESSES)

# default is 50, this seems to be enough
FLAKE_RUNS ?= 20

atest: override ARGS += -x --flake-finder --flake-runs=$(FLAKE_RUNS)

.PHONY: push
push:
	nix-shell --packages cachix --run "nix-build | cachix push distinfo"
