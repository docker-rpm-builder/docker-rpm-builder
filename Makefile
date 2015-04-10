.PHONY: srpm clean distclean pypirelease test fulltest pypirelease

SHELL := /bin/bash

devenv: setup.py
	test -r devenv || virtualenv-2.7 devenv
	devenv/bin/pip install --editable . --upgrade
	devenv/bin/pip install wheel
	devenv/bin/pip install bpython


test: devenv
	devenv/bin/python -m unittest2 discover -v
	devenv/bin/docker-rpm-builder selftest

fulltest: test
	. devenv/bin/activate && cd drb/integration_tests && ./test.sh ${TEST_IMAGES}

tmp:
	mkdir -p tmp

clean:
	rm -rf tmp build dist 

distclean: clean
	rm -rf prodenv devenv *.tar.gz docker-rpm-builder.spec

stablerelease:
ifndef RELEASE_NUMBER
	@echo "Must pass RELEASE_NUMBER"
	@exit 1
endif
	# always recreate
	rm -rf prodenv
	virtualenv-2.7 prodenv
	sed -i -e "s/dev0//g" version.txt
	[ "${RELEASE_NUMBER}" == "$$(cat version.txt)" ] || { echo "Release number version mismatch"; exit 1; }
	prodenv/bin/pip install .
	prodenv/bin/pip freeze > requirements.txt
	prodenv/bin/pip install wheel
	git add version.txt requirements.txt
	git commit version.txt requirements.txt -m "Prepare for release ${RELEASE_NUMBER}"
	git tag ${RELEASE_NUMBER} -m "Release tag"
	prodenv/bin/python setup.py bdist_wheel sdist register upload

nextrelease:
	MAJOR="$$(cat version.txt | cut -d '.' -f 1)" ; MINOR="$$(cat version.txt | cut -d '.' -f 2)" ; echo $${MAJOR}.$$(($${MINOR} +1))dev0 > version.txt
	rm -rf *.egg-info
	git add version.txt
	prodenv/bin/pip uninstall -y wheel docker-rpm-builder
	prodenv/bin/pip install .
	prodenv/bin/pip freeze > requirements.txt
	git add version.txt requirements.txt
	git commit version.txt requirements.txt -m "Bump development version"
