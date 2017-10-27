.PHONY: test integrationtest testexample clean distclean cleanexample install increase_minor_version

PYTHON ?= $(shell which python)
VIRTUALENV ?= $(shell which virtualenv) -p $(PYTHON)
SHELL := /bin/bash
SRC_ROOT = drb
FIND := $(shell which gfind || which find)

devenv: setup.py requirements.txt
	test -r devenv/bin/activate || $(VIRTUALENV) devenv || rm -rf devenv
	touch -t 197001011200 devenv
	source devenv/bin/activate && python devenv/bin/pip install -r requirements.txt && python devenv/bin/pip install --editable . --no-deps && python devenv/bin/pip check
	touch devenv

# WARNING: this will freeze the CURRENT DEVELOPMENT ENVIRONMENT. Think twice if you've tinkered with it.
freeze: devenv
	source devenv/bin/activate && python devenv/bin/pip freeze | grep -v "docker-rpm-builder" > requirements.txt

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
	$(FIND) \( -name '*.pyc' -o -name '*.pyo' \) -delete

distclean: clean
	rm -rf devenv *.egg-info
# PKGBUILD
install:
	cp -ar ./devenv/* $(PREFIX)

increase_minor_version:
	perl -pe 's/^(VERSION=(\d+\.)*)(\d+)(.*)$$/$$1.($$3+1).$$4/e' < packaging/env.list > packaging/env.list.tmp
	mv -f packaging/env.list.tmp packaging/env.list
