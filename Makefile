.PHONY: test fulltest clean distclean stablerelease nextrelease rpm prodenv

SHELL := /bin/bash

devenv: setup.py
	test -r devenv || virtualenv-2.7 devenv
	devenv/bin/pip install --editable . --upgrade
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython


test: devenv
	devenv/bin/python -m unittest2 discover -v
	devenv/bin/docker-rpm-builder selftest

integrationtest: devenv
	devenv/bin/python -m unittest2 discover -p 'integration_test_*' -v

fulltest: test devenv integrationtest
	cd drb/integration_tests && DRB_EXEC=../../devenv/bin/docker-rpm-builder ./test.sh ${TEST_IMAGES}

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf prodenv devenv *.tar.gz docker-rpm-builder.spec

prodenv:
	rm -rf prodenv
    
rpm: devenv
ifndef DOCKERPACKAGE
	$(error DOCKERPACKAGE is undefined)
endif
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
