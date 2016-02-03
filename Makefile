.PHONY: test integrationtest clean distclean

VIRTUALENV ?= virtualenv-2.7
SHELL := /bin/bash

devenv: setup.py
	test -r devenv || $(VIRTUALENV) devenv
	devenv/bin/pip install --editable . --upgrade
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython

test: devenv
	devenv/bin/python -m unittest2 discover -v

integrationtest: devenv test
	devenv/bin/python -m unittest2 discover -p 'integration_test_*' -v

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf devenv *.egg-info
