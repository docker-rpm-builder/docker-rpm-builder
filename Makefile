.PHONY: test integrationtest clean distclean

VIRTUALENV ?= virtualenv-2.7
SHELL := /bin/bash

devenv: setup.py Makefile
	test -r devenv || virtualenv-2.7 devenv
	devenv/bin/pip install --editable . --upgrade
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython
	touch devenv

test: devenv
	devenv/bin/python -m unittest2 discover -v

integrationtest: devenv test
	devenv/bin/python -m unittest2 discover -p 'integration_test_*' -v

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf devenv *.egg-info
