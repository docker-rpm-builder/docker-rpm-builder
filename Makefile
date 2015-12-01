.PHONY: test fulltest clean distclean rpm prodenv

VIRTUALENV ?= virtualenv-2.7
SHELL := /bin/bash

devenv: setup.py
	test -r devenv || $(VIRTUALENV) devenv
	devenv/bin/pip install --editable . --upgrade
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython


test: devenv
	devenv/bin/python -m unittest2 discover -v
	devenv/bin/docker-rpm-builder selftest

integrationtest: devenv
	devenv/bin/python -m unittest2 discover -p 'integration_test_*' -v

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf prodenv devenv *.tar.gz docker-rpm-builder.spec

prodenv:
	rm -rf prodenv
    
rpm: devenv
ifndef BUILD_IMAGE
	$(error BUILD_IMAGE is undefined)
endif
ifndef OUTDIR
	$(error OUTDIR is undefined)
endif
ifndef SIGNKEY
	$(error SIGNKEY is undefined)
endif
	devenv/bin/docker-rpm-builder dir --sign-with ${SIGNKEY} --download-sources ${BUILD_IMAGE} . ${OUTDIR}
