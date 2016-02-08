.PHONY: test integrationtest testexample clean distclean

VIRTUALENV ?= virtualenv-2.7
SHELL := /bin/bash

devenv: setup.py Makefile
	test -r devenv || $(VIRTUALENV) devenv
	devenv/bin/pip install --editable . --upgrade
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython
	touch devenv

test: devenv
	devenv/bin/python -m unittest2 discover -v

integrationtest: devenv test
	devenv/bin/python -m unittest2 discover -p 'integration_test_*' -v

testexample: devenv
	cd example ; rm -rf out_*
	source devenv/bin/activate ; cd example/from_dir ; docker-rpm-builder dir alanfranz/drb-epel-7-x86-64:latest . ../out_from_dir
	source devenv/bin/activate ; cd example/from_remote_source ; docker-rpm-builder dir --download-sources alanfranz/drb-epel-7-x86-64:latest . ../out_from_remote_source

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf devenv *.egg-info
