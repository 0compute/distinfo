include .pyproject/Makefile

$(eval $(call TEST,packages))

test-unit test-functional: export DISTINFO_RAISE_ON_HIT=0

NUM_PROCESSES ?= logical

test-acceptance test-packages: override ARGS += --numprocesses=$(NUM_PROCESSES)

FLAKE_RUNS ?= 30

test-flaky: override ARGS += \
	--flake-finder \
	--flake-runs=$(FLAKE_RUNS) \
	-x
test-flaky: test-acceptance
