.PHONY: test integrationtest testexample clean distclean cleanexample install increase_minor_version

VIRTUALENV ?= virtualenv-2.7
SHELL := /bin/bash
SRC_ROOT = drb
FIND := $(shell which gfind || which find)

devenv: setup.py Makefile
	test -r devenv || $(VIRTUALENV) devenv
	source devenv/bin/activate ; python devenv/bin/pip install --editable . --upgrade ; python devenv/bin/pip install wheel ; python devenv/bin/pip install bpython
	touch devenv

test: devenv
	devenv/bin/python -m unittest discover -v
	$(FIND) $(SRC_ROOT) -type f -name '*.py' | { ! xargs grep -H $$'\t' ; } || { echo 'found tabs in some py file' ; exit 1 ; }

integrationtest: devenv test
	devenv/bin/python -m unittest discover -p 'integration_test_*' -v

testexample: devenv cleanexample
	source devenv/bin/activate ; cd example/from_dir ; ITERATION=11 python $$(which docker-rpm-builder) dir alanfranz/drb-epel-7-x86-64:latest . ../out_from_dir
	source devenv/bin/activate ; cd example/from_remote_source ; make ;  ITERATION=12 python $$(which docker-rpm-builder) dir --download-sources tmux-drbbuild . ../out_from_remote_source

cleanexample:
	rm -rf example/out_*

clean: cleanexample
	rm -rf tmp build dist 
	find \( -name '*.pyc' -o -name '*.pyo' \) -delete

distclean: clean
	rm -rf devenv *.egg-info
# PKGBUILD
install:
	cp -ar ./devenv/* $(PREFIX)

increase_minor_version:
	perl -pe 's/^(VERSION=(\d+\.)*)(\d+)(.*)$$/$$1.($$3+1).$$4/e' < packaging/env.list > packaging/env.list.tmp
	mv -f packaging/env.list.tmp packaging/env.list
