include .skel/Makefile

$(eval $(call TEST,ptest,acceptance/test_packages.py))

NUM_PROCESSES ?= auto

atest ptest: override ARGS += --numprocesses=$(NUM_PROCESSES)

utest ftest: export DISTINFO_RAISE_ON_HIT=0

.PHONY: push
push:
	nix-shell --packages cachix --run "nix-build | cachix push distinfo"
