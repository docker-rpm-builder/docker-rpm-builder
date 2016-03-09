.PHONY: test integrationtest testexample clean distclean cleanexample

VIRTUALENV ?= virtualenv-2.7
SHELL := /bin/bash

devenv: setup.py Makefile
	test -r devenv || $(VIRTUALENV) devenv
	source devenv/bin/activate ; python devenv/bin/pip install --editable . --upgrade ; python devenv/bin/pip install wheel ; python devenv/bin/pip install bpython
	touch devenv

test: devenv
	devenv/bin/python -m unittest2 discover -v

integrationtest: devenv test
	devenv/bin/python -m unittest2 discover -p 'integration_test_*' -v

testexample: devenv cleanexample
	source devenv/bin/activate ; cd example/from_dir ; ITERATION=11 python $$(which docker-rpm-builder) dir alanfranz/drb-epel-7-x86-64:latest . ../out_from_dir
	source devenv/bin/activate ; cd example/from_remote_source ; make ;  ITERATION=12 python $$(which docker-rpm-builder) dir --download-sources tmux-drbbuild . ../out_from_remote_source

cleanexample:
	rm -rf example/out_*

clean: cleanexample
	rm -rf tmp build dist 

distclean: clean
	rm -rf devenv *.egg-info
install:
	prefix := /opt
	cp -ar ./* $(prefix)
